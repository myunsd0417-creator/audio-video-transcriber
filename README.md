# Audio to Text & Speech to Text: Whisper, Podcast, Japanese

[![Run on Apify](https://apify.com/ext/run-on-apify.png)](https://apify.com/mirumiru_miru17/audio-video-transcriber)

**Run it in the cloud with no setup: [apify.com/mirumiru_miru17/audio-video-transcriber](https://apify.com/mirumiru_miru17/audio-video-transcriber)**

Turn **audio files, videos and whole podcasts into text** with **OpenAI Whisper** (faster-whisper). Paste direct file links, public Google Drive or Dropbox share links, a **podcast RSS feed** or an **Apple Podcasts** show link, and get the **full transcript**, **SRT, VTT and TXT files**, timestamped segments and optional **word-level timestamps**.

Need English? Turn on **Translate to English** to get English text and subtitles from audio in any language. Automatic language detection covers 90+ languages and is especially strong for **Japanese**. No API key, no setup. Use it from the API, on a schedule, or as a tool for AI agents through the Apify MCP server.

## Why this transcriber

- **Podcasts in one step**: paste an RSS feed or an Apple Podcasts show link and the newest N episodes are transcribed automatically.
- **Works with the links you already have**: direct mp3, wav, m4a, mp4, webm, ogg and flac URLs (up to 500 MB each), plus public Google Drive and Dropbox share links, which are converted for you. YouTube, TikTok and Instagram page links are not supported.
- **Two modes, clear prices**: *Accurate* (Whisper small) at $0.01 per audio minute for accents, noisy audio and Japanese, or *Fast* (Whisper base) at $0.005 per minute. Paid Apify plans get discounts.
- **Pay only for what is transcribed**: you are charged per started minute of audio actually transcribed. Failed downloads, files over your length limit and files with no speech are not charged, and your max cost per run is respected.
- **Ready-to-use subtitles and transcripts**: SRT and VTT for video editors and web players, TXT and full text for show notes, search and archives.
- **Word-level timestamps** (optional) for karaoke-style captions and precise editing.
- **Translate to English from any language**: best results in Accurate mode.
- **Built for automation**: structured JSON output, one dataset item per file or episode, ready for the API, schedules and AI agent workflows.

## Use cases

- Podcast transcripts for show notes, SEO and accessibility
- Meeting, interview and lecture recordings → searchable text
- Video subtitles in the original language or in English
- Japanese audio (日本語) → accurate Japanese text
- Bulk transcription of many files or episodes in one run, or as a tool for AI agents via the Apify MCP server

## Input

| Field | Description |
| --- | --- |
| `audioUrls` | Direct links to audio/video files (mp3, wav, m4a, mp4, webm, ogg, flac… up to 500 MB each), or public Google Drive / Dropbox share links. |
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

Pay per started minute of audio that is transcribed. *Fast* mode costs half of *Accurate* mode. Failed downloads, files over your length limit and files with no speech are not charged. Translation and word timestamps are included at no extra cost.

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

音声・動画ファイルやポッドキャストを、OpenAI Whisper（faster-whisper）で文字起こしします。ファイルのURL、公開のGoogleドライブ・Dropbox共有リンク、ポッドキャストのRSS、Apple Podcastsの番組リンクを入れるだけで、全文テキスト、SRT・VTT・TXTファイル、タイムスタンプ（単語単位も可）を出力します。日本語の音声に特に強く、90以上の言語を自動判定できます。「英語に翻訳」をオンにすると、どの言語の音声からでも英語のテキストと字幕を作れます。高精度モードは1分あたり0.01ドル、高速モードはその半額で、実際に文字起こしした分だけの課金です。ダウンロードに失敗したファイルや無音のファイルには課金されません。APIキーや設定は不要です（YouTube・TikTok・Instagramのページリンクは非対応です）。

## License

MIT
