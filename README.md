# Audio & Video to Text Transcriber (Whisper) + SRT Subtitles

[![Run on Apify](https://apify.com/ext/run-on-apify.png)](https://apify.com/mirumiru_miru17/audio-video-transcriber)

**Run it in the cloud with no setup: [apify.com/mirumiru_miru17/audio-video-transcriber](https://apify.com/mirumiru_miru17/audio-video-transcriber)**


Turn audio and video files into text with **OpenAI Whisper**. Paste direct links to your files and get the **full transcript**, **timestamped segments** and ready-to-use **SRT subtitles**. Works with **Japanese** and 90+ other languages, with automatic language detection.

No API key, no account elsewhere, no setup. **Pay only per minute of audio.**

## Use cases

- Meeting, interview and lecture recordings → searchable text
- Podcasts and videos → subtitles (SRT) and show notes
- Japanese audio (日本語) → accurate Japanese text with proper punctuation spacing
- Bulk transcription of many files in one run

## Input

| Field | Description |
| --- | --- |
| `audioUrls` | Direct links to audio/video files: mp3, wav, m4a, mp4, webm, ogg, flac… up to 500 MB each. |
| `language` | `auto` (default) or a language code such as `ja`, `en`, `zh`. Setting it improves accuracy. |
| `maxFiles` | Safety limit on files per run (default 20). |
| `maxMinutesPerFile` | Longer files are skipped and **not charged** (default 120). |

Page links such as YouTube watch pages are not supported. Use a direct file link (for example a public link from your cloud storage or podcast feed).

## Output

One dataset item per file:

```json
{
  "url": "https://example.com/meeting.mp3",
  "language": "ja",
  "durationSeconds": 312.4,
  "chargedMinutes": 6,
  "text": "本日の会議では…",
  "segments": [{ "start": 0.0, "end": 4.2, "text": "本日の会議では" }],
  "srt": "1\n00:00:00,000 --> 00:00:04,200\n本日の会議では\n"
}
```

Each file's subtitles are also saved as `SUBTITLES-1.srt`, `SUBTITLES-2.srt`… in the key-value store.

## Pricing

Pay per started minute of audio that is transcribed. Files that fail to download or exceed your limits are not charged. The Actor respects your maximum cost per run.

## Notes

- Uses the Whisper **small** model on CPU with voice-activity detection to skip silence.
- Accuracy depends on audio quality, accents and background noise.
- Only transcribe recordings you have the right to use.

## More tools from the same author

- [SEO Audit & AI Search Readiness Checker](https://apify.com/mirumiru_miru17/seo-ai-readiness-audit): full-site SEO audit, AI search readiness score and llms.txt generator
- [Bulk PageSpeed & Core Web Vitals Checker](https://apify.com/mirumiru_miru17/page-speed-core-web-vitals): Lighthouse scores, LCP/CLS/TBT and top fixes for a list of URLs
- [Image & PDF OCR to Text (Japanese + English)](https://apify.com/mirumiru_miru17/image-pdf-ocr-japanese): text from images and scanned PDFs, Japanese incl. vertical

---

## 日本語

音声・動画ファイルのURLを入れるだけで、OpenAIのWhisperで文字起こしします。全文テキスト、タイムスタンプ付きの区切り、SRT字幕を出力します。日本語を含む90以上の言語に対応し、言語は自動判定もできます。APIキーは不要で、料金は音声1分ごとの従量課金です。

## License

MIT
