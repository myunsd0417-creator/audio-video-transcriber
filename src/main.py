"""Podcast, Audio & Video Transcriber (Whisper) — Apify Actor.

Transcribes audio/video files and podcast episodes with faster-whisper on CPU (no API key).
Inputs: direct file URLs, podcast RSS feeds, or Apple Podcasts show links.
Outputs: full text, timestamped segments (optionally word-level), SRT and VTT subtitles.
Optional translation of any language to English.

Pricing events (one per started minute of audio):
  - "audio-minute"       accurate mode (Whisper small)
  - "audio-minute-fast"  fast mode (Whisper base)
"""
import asyncio
import math
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import httpx
import numpy as np
from apify import Actor
from faster_whisper import WhisperModel

MODEL_DIRS = {'accurate': '/models/small', 'fast': '/models/base'}
EVENTS = {'accurate': 'audio-minute', 'fast': 'audio-minute-fast'}
MAX_BYTES = 500 * 1024 * 1024  # 500 MB per file
UA = {'User-Agent': 'Mozilla/5.0 (Apify Actor podcast transcriber)'}
CJK_LANGS = ('ja', 'zh', 'ko', 'th')


def fmt_ts(sec: float, sep: str = ',') -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02}{sep}{ms:03}'


def to_srt(segments: list[dict]) -> str:
    out = []
    for i, seg in enumerate(segments, 1):
        out += [str(i), f"{fmt_ts(seg['start'])} --> {fmt_ts(seg['end'])}", seg['text'], '']
    return '\n'.join(out)


def to_vtt(segments: list[dict]) -> str:
    out = ['WEBVTT', '']
    for seg in segments:
        out += [f"{fmt_ts(seg['start'], '.')} --> {fmt_ts(seg['end'], '.')}", seg['text'], '']
    return '\n'.join(out)


def direct_link(url: str) -> str:
    """Turn public Google Drive / Dropbox share links into direct download links."""
    m = re.search(r'drive\.google\.com/(?:file/d/|open\?id=|uc\?(?:.*&)?id=)([\w-]{10,})', url)
    if m:
        return f'https://drive.usercontent.google.com/download?id={m.group(1)}&export=download&confirm=t'
    if 'dropbox.com/' in url:
        url = re.sub(r'([?&])dl=0', r'\1dl=1', url)
        if 'dl=1' not in url and 'raw=1' not in url:
            url += ('&' if '?' in url else '?') + 'dl=1'
    return url


def clean_urls(values) -> list[str]:
    urls = []
    for u in values or []:
        u = u.get('url') if isinstance(u, dict) else u
        if isinstance(u, str) and u.strip().lower().startswith(('http://', 'https://')):
            urls.append(u.strip())
    return list(dict.fromkeys(urls))


async def resolve_feed_url(client: httpx.AsyncClient, url: str) -> str:
    """Apple Podcasts show links are turned into their public RSS feed via the iTunes lookup API."""
    m = re.search(r'podcasts\.apple\.com/.*/id(\d+)', url)
    if not m:
        return url
    r = await client.get(f'https://itunes.apple.com/lookup?id={m.group(1)}&entity=podcast', headers=UA)
    r.raise_for_status()
    results = r.json().get('results') or []
    feed = next((x.get('feedUrl') for x in results if x.get('feedUrl')), None)
    if not feed:
        raise ValueError('Could not find the RSS feed for this Apple Podcasts show')
    return feed


async def episodes_from_feed(client: httpx.AsyncClient, url: str, limit: int) -> list[dict]:
    feed_url = await resolve_feed_url(client, url)
    r = await client.get(feed_url, headers=UA)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    show = (root.findtext('channel/title') or '').strip()
    eps = []
    for item in root.iter('item'):
        enc = item.find('enclosure')
        if enc is None or not enc.get('url'):
            continue
        eps.append({
            'url': enc.get('url'),
            'title': (item.findtext('title') or '').strip(),
            'published': (item.findtext('pubDate') or '').strip(),
            'podcast': show,
            'feedUrl': feed_url,
        })
        if len(eps) >= limit:
            break
    if not eps:
        raise ValueError('No audio episodes found in this feed')
    return eps


async def download(client: httpx.AsyncClient, url: str, path: str) -> None:
    async with client.stream('GET', url, headers=UA) as r:
        r.raise_for_status()
        size = 0
        with open(path, 'wb') as f:
            async for chunk in r.aiter_bytes(1 << 20):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise ValueError('File is larger than 500 MB')
                f.write(chunk)


def decode_audio(path: str) -> np.ndarray:
    """Decode any audio/video file to 16 kHz mono float32 with ffmpeg."""
    proc = subprocess.run(
        ['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', path, '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
        capture_output=True, check=False,
    )
    if proc.returncode != 0 or not proc.stdout:
        raise ValueError('Could not read audio from this file: ' + proc.stderr.decode(errors='ignore')[-300:].strip())
    return np.frombuffer(proc.stdout, dtype=np.float32)


async def main() -> None:
    async with Actor:
        inp = await Actor.get_input() or {}
        language = inp.get('language') or 'auto'
        quality = 'fast' if inp.get('quality') == 'fast' else 'accurate'
        task = 'translate' if inp.get('translateToEnglish') else 'transcribe'
        word_ts = bool(inp.get('wordTimestamps'))
        max_minutes = float(inp.get('maxMinutesPerFile', 120))
        max_files = int(inp.get('maxFiles', 20))
        event = EVENTS[quality]

        jobs = [{'url': u} for u in clean_urls(inp.get('audioUrls'))]
        for j in jobs:
            d = direct_link(j['url'])
            if d != j['url']:
                j['sourceUrl'], j['url'] = j['url'], d
        feeds = clean_urls(inp.get('podcastFeeds'))
        per_feed = int(inp.get('episodesPerFeed', 3))

        async with httpx.AsyncClient(follow_redirects=True, timeout=120) as client:
            for f in feeds:
                try:
                    jobs += await episodes_from_feed(client, f, per_feed)
                except Exception as e:  # report and continue with other inputs
                    Actor.log.warning(f'Feed failed: {f} — {e}')
                    await Actor.push_data({'url': f, 'error': f'Podcast feed: {e}'})
            seen, unique = set(), []
            for j in jobs:
                if j['url'] not in seen:
                    seen.add(j['url'])
                    unique.append(j)
            jobs = unique[:max_files]

            if not jobs:
                await Actor.fail(status_message='Add at least one direct audio/video link in "audioUrls" or a podcast feed in "podcastFeeds".')
                return

            Actor.log.info(f'Loading Whisper model ({quality})...')
            model = WhisperModel(MODEL_DIRS[quality], device='cpu', compute_type='int8', cpu_threads=os.cpu_count() or 1)
            cm = Actor.get_charging_manager()

            for idx, job in enumerate(jobs, 1):
                url = job['url']
                with tempfile.TemporaryDirectory() as tmp:
                    path = os.path.join(tmp, 'media')
                    try:
                        Actor.log.info(f'Downloading {url}')
                        await download(client, url, path)
                        audio = await asyncio.to_thread(decode_audio, path)
                        duration = audio.size / 16000
                        if duration / 60 > max_minutes:
                            raise ValueError(f'Audio is {duration / 60:.1f} min, above the limit of {max_minutes:g} min per file (not charged)')
                        minutes = max(1, math.ceil(duration / 60))

                        # Respect the user's spending limit before doing the expensive work.
                        allowed = cm.calculate_max_event_charge_count_within_limit(event)
                        if allowed is not None and allowed < minutes:
                            await Actor.push_data({**job, 'error': f'Spending limit too low: this file needs {minutes} audio minute(s).'})
                            Actor.log.info('Spending limit reached — stopping.')
                            break

                        segments_iter, info = model.transcribe(
                            audio,
                            language=None if language == 'auto' else language,
                            task=task,
                            vad_filter=True,
                            beam_size=1,
                            condition_on_previous_text=False,
                            word_timestamps=word_ts,
                        )
                        Actor.log.info(f'Transcribing {duration / 60:.1f} min ({info.language}, {quality}, {task})')
                        segs = []
                        for s in segments_iter:
                            seg = {'start': round(s.start, 2), 'end': round(s.end, 2), 'text': s.text.strip()}
                            if word_ts and s.words:
                                seg['words'] = [{'start': round(w.start, 2), 'end': round(w.end, 2), 'word': w.word.strip()} for w in s.words]
                            segs.append(seg)
                        if not any(s['text'] for s in segs):
                            raise ValueError('No speech was found in this file (not charged)')
                        await Actor.charge(event_name=event, count=minutes)

                        out_lang = 'en' if task == 'translate' else info.language
                        sep = '' if out_lang in CJK_LANGS else ' '
                        text = sep.join(s['text'] for s in segs).strip()
                        srt, vtt = to_srt(segs), to_vtt(segs)
                        await Actor.set_value(f'SUBTITLES-{idx}.srt', srt, content_type='text/plain; charset=utf-8')
                        await Actor.set_value(f'SUBTITLES-{idx}.vtt', vtt, content_type='text/vtt; charset=utf-8')
                        await Actor.set_value(f'TRANSCRIPT-{idx}.txt', text, content_type='text/plain; charset=utf-8')
                        await Actor.push_data({
                            **job,
                            'spokenLanguage': info.language,
                            'languageProbability': round(info.language_probability or 0, 3),
                            'outputLanguage': out_lang,
                            'mode': quality,
                            'translated': task == 'translate',
                            'durationSeconds': round(duration, 1),
                            'chargedMinutes': minutes,
                            'text': text,
                            'segments': segs,
                            'srt': srt,
                            'vtt': vtt,
                            'files': {'srt': f'SUBTITLES-{idx}.srt', 'vtt': f'SUBTITLES-{idx}.vtt', 'txt': f'TRANSCRIPT-{idx}.txt'},
                            'error': None,
                        })
                    except Exception as e:  # keep going with the next file
                        Actor.log.warning(f'Failed: {url} — {e}')
                        await Actor.push_data({**job, 'error': str(e)})
