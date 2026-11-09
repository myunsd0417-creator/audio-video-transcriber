# Japanese Transcription: Whisper Audio & Video to Text + SRT

[![Run on Apify](https://apify.com/ext/run-on-apify.png)](https://apify.com/mirumiru_miru17/audio-video-transcriber)

**Run it in the cloud with no setup: [apify.com/mirumiru_miru17/audio-video-transcriber](https://apify.com/mirumiru_miru17/audio-video-transcriber)**


Transcribe **audio files, videos and whole podcasts** with **OpenAI Whisper**. Paste direct file links, a **podcast RSS feed** or an **Apple Podcasts link**, and get the **full transcript**, **SRT and VTT subtitles**, timestamped segments and optional **word-level timestamps**. Need English? Turn on **Translate to English** and get English text and subtitles from audio in any language.

Strong **Japanese** support plus 90+ languages with automatic detection. No API key, no setup. **Pay only per minute of audio.**

## Why this transcriber

- **Podcasts in one step**: paste an RSS feed or an Apple Podcasts show page and the newest episodes are transcribed automatically.
- **Two modes**: *Accurate* (Whisper small) for Japanese, accents and noisy audio, or *Fast* (Whisper base) at half the price.
- **Translate to English**: Japanese, Spanish, Korean or any other language in, English transcript and subtitles out. Use *Accurate* mode for the best translations.
- **Ready-to-use subtitles**: SRT and VTT files for YouTube, video editors and web players.
- **Word timestamps** for karaoke-style captions and precise editing.
- **Fair billing**: files that fail to download or exceed your limits are not charged, and your maximum cost per run is respected.

## Use cases

- Podcast transcripts for show notes, SEO and accessibility
- Meeting, interview and lecture recordings → searchable text
- Video subtitles in the original language or in English
- Japanese audio (日本語) → accurate Japanese text
- Bulk transcription of many files or episodes in one run, or as a tool for AI agents via the Apify MCP server

## Input

| Field | Description |
| --- | --- |
| `audioUrls` | Direct links to audio/video files: mp3, wav, m4a, mp4, webm, ogg, flac… up to 500 MB each. |
| `podcastFeeds` | Podcast RSS feed URLs or Apple Podcasts show links (`podcasts.apple.com/.../id123…`). |
| `episodesPerFeed` | Newest episodes to transcribe per feed (default 3). |
| `quality` | `accurate` (default) or `fast`. |
| `language` | `auto` (default) or a language code such as `ja`, `en`, `es`. Setting it improves accuracy. |
| `translateToEnglish` | Output English text and subtitles. |
| `wordTimestamps` | Add start/end times for each word. |
| `maxFiles` | Safety limit on files/episodes per run (default 20). |
| `maxMinutesPerFile` | Longer files are skipped and **not charged** (default 120). |

Video page links such as YouTube watch pages are not supported. Use direct file links or podcast feeds.

## Output

One dataset item per file or episode:

```json
{
  "title": "Episode 42: Interview",
  "podcast": "My Podcast",
  "url": "https://example.com/episode42.mp3",
  "spokenLanguage": "ja",
  "outputLanguage": "ja",
  "mode": "accurate",
  "durationSeconds": 1834.2,
  "chargedMinutes": 31,
  "text": "本日のゲストは…",
  "segments": [{ "start": 0.0, "end": 4.2, "text": "本日のゲストは" }],
  "srt": "1\n00:00:00,000 --> 00:00:04,200\n本日のゲストは\n",
  "vtt": "WEBVTT\n\n00:00:00.000 --> 00:00:04.200\n本日のゲストは\n"
}
```

Each item's files are also saved to the key-value store: `SUBTITLES-1.srt`, `SUBTITLES-1.vtt`, `TRANSCRIPT-1.txt`, and so on.

## Pricing

Pay per started minute of audio that is transcribed. *Fast* mode costs about half of *Accurate* mode. Translation and word timestamps are included at no extra cost.

## Notes

- Runs faster-whisper on CPU with voice-activity detection to skip silence.
- Accuracy depends on audio quality, accents and background noise.
- Only transcribe recordings you have the right to use.

## More tools from the same author

- [SEO Audit & AI Search Readiness Checker](https://apify.com/mirumiru_miru17/seo-ai-readiness-audit): full-site SEO audit, AI search readiness score and llms.txt generator
- [Bulk PageSpeed & Core Web Vitals Checker](https://apify.com/mirumiru_miru17/page-speed-core-web-vitals): Lighthouse scores, LCP/CLS/TBT and top fixes for a list of URLs
- [Japanese OCR: Image, PDF, Receipt & Invoice to Text](https://apify.com/mirumiru_miru17/image-pdf-ocr-japanese): text from images and scanned PDFs, Japanese incl. vertical

---

## 日本語

音声・動画ファイル、ポッドキャストをWhisperで文字起こしします。ファイルのURL、ポッドキャストのRSS、Apple Podcastsの番組ページを入れるだけで、全文テキスト、SRT・VTT字幕、タイムスタンプ（単語単位も可）を出力します。「英語に翻訳」をオンにすると、どの言語の音声からでも英語のテキストと字幕を作れます。高精度モードと、半額で約3倍速い高速モードを選べます。日本語に強く、90以上の言語に対応。APIキー不要、音声1分ごとの従量課金です。

## License

MIT
