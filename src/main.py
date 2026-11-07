"""Audio & Video Transcriber (Whisper) — Apify Actor.

Transcribes audio/video files from direct URLs with faster-whisper (Whisper "small",
runs on CPU, no API key). Outputs plain text, timestamped segments and SRT subtitles.
Charges one "audio-minute" event per started minute of audio that was transcribed.
"""
import asyncio
import math
import os
import tempfile

import subprocess

import httpx
import numpy as np
from apify import Actor
from faster_whisper import WhisperModel

MODEL_DIR = os.environ.get('WHISPER_MODEL_DIR', '/models/small')
MAX_BYTES = 500 * 1024 * 1024  # 500 MB per file


def fmt_ts(sec: float, sep: str = ',') -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02}{sep}{ms:03}'


def to_srt(segments: list[dict]) -> str:
    lines = []
    for i, seg in enumerate(segments, 1):
        lines += [str(i), f"{fmt_ts(seg['start'])} --> {fmt_ts(seg['end'])}", seg['text'], '']
    return '\n'.join(lines)


async def download(url: str, path: str) -> None:
    async with httpx.AsyncClient(follow_redirects=True, timeout=120) as client:
        async with client.stream('GET', url, headers={'User-Agent': 'Mozilla/5.0 (Apify Actor transcriber)'}) as r:
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
        raw = inp.get('audioUrls') or []
        urls = []
        for u in raw:
            u = u.get('url') if isinstance(u, dict) else u
            if isinstance(u, str) and u.strip().lower().startswith(('http://', 'https://')):
                urls.append(u.strip())
        urls = list(dict.fromkeys(urls))[: int(inp.get('maxFiles', 20))]
        language = inp.get('language') or 'auto'
        max_minutes = float(inp.get('maxMinutesPerFile', 120))

        if not urls:
            await Actor.fail(status_message='Input "audioUrls" must contain at least one direct link to an audio or video file.')
            return

        Actor.log.info('Loading Whisper model...')
        model = WhisperModel(MODEL_DIR, device='cpu', compute_type='int8', cpu_threads=os.cpu_count() or 1)

        for url in urls:
            with tempfile.TemporaryDirectory() as tmp:
                path = os.path.join(tmp, 'media')
                try:
                    Actor.log.info(f'Downloading {url}')
                    await download(url, path)
                    audio = await asyncio.to_thread(decode_audio, path)
                    if audio.size / 16000 / 60 > max_minutes:
                        raise ValueError(f'Audio is {audio.size / 16000 / 60:.1f} min, above the limit of {max_minutes} min per file')
                    segments_iter, info = model.transcribe(
                        audio,
                        language=None if language == 'auto' else language,
                        vad_filter=True,
                        beam_size=1,
                        condition_on_previous_text=False,
                    )
                    duration = float(info.duration or 0)
                    if duration / 60 > max_minutes:
                        raise ValueError(f'Audio is {duration / 60:.1f} min, above the limit of {max_minutes} min per file')
                    minutes = max(1, math.ceil(duration / 60))

                    # Respect the user's spending limit before doing the expensive work.
                    allowed = Actor.get_charging_manager().calculate_max_event_charge_count_within_limit('audio-minute')
                    if allowed is not None and allowed < minutes:
                        await Actor.push_data({'url': url, 'error': f'Spending limit too low: this file needs {minutes} audio minute(s).'})
                        Actor.log.info('Spending limit reached — stopping.')
                        break
                    await Actor.charge(event_name='audio-minute', count=minutes)

                    Actor.log.info(f'Transcribing {duration / 60:.1f} min ({info.language})')
                    segs = [
                        {'start': round(s.start, 2), 'end': round(s.end, 2), 'text': s.text.strip()}
                        for s in segments_iter
                    ]
                    sep = '' if info.language in ('ja', 'zh', 'ko', 'th') else ' '
                    text = sep.join(s['text'] for s in segs).strip()
                    key = f'SUBTITLES-{urls.index(url) + 1}.srt'
                    srt = to_srt(segs)
                    await Actor.set_value(key, srt, content_type='text/plain; charset=utf-8')
                    await Actor.push_data({
                        'url': url,
                        'language': info.language,
                        'languageProbability': round(info.language_probability or 0, 3),
                        'durationSeconds': round(duration, 1),
                        'chargedMinutes': minutes,
                        'text': text,
                        'segments': segs,
                        'srtKey': key,
                        'srt': srt,
                        'error': None,
                    })
                except Exception as e:  # keep going with the next file
                    Actor.log.warning(f'Failed: {url} — {e}')
                    await Actor.push_data({'url': url, 'error': str(e)})

