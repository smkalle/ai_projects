# Medical Researcher Workbench

A full-featured, local-first research workbench for medical researchers built around **Cohere Transcribe** — open-source speech-to-text with state-of-the-art accuracy across 14 languages.

---

## Why This Workbench

**Cohere Transcribe** (`cohere-transcribe-03-2026`) delivers 5.42% WER on the Hugging Face Open ASR Leaderboard — outperforming Whisper Large v3 (7.44%), ElevenLabs Scribe v2, and Qwen3-ASR-1.7B. It runs locally with no API calls required, handles 55+ minute recordings, streams real-time from a microphone, and processes 10 files as a batch.

This workbench wraps all of that in a medical-research-oriented UI with literature review tools, data analysis, and PDF export — all on your own hardware.

---

## Features

### Core Transcription
- **Single file transcription** — Upload wav/mp3/m4a, select language, get a timestamped transcript
- **Batch transcription** — Queue multiple files, process sequentially, download all as a ZIP
- **Real-time microphone** — Live speech-to-text while you record; language selectable per session
- **14 languages** — English, French, German, Italian, Spanish, Portuguese, Greek, Dutch, Polish, Arabic, Vietnamese, Chinese, Japanese, Korean
- **Punctuation toggle** — Clinical notes need punctuation; raw transcripts are cleaner for NLP pipelines

### Analysis & Research Tools
- **Transcript library** — Save, search, tag, and edit transcripts; all stored locally in SQLite
- **Dataset import** — Drag-drop CSV/Excel; preview, filter, and run descriptive statistics
- **Interactive visualizations** — Histogram, box, and scatter plots via Plotly
- **WER benchmarking** — Measure transcription accuracy on your own domain-specific audio

### Documentation & Export
- **PDF reports** — Export sessions as formatted PDF with transcript, metadata, and figures
- **Plain text export** — Download transcripts as .txt with optional timestamps
- **Session persistence** — Auto-save workspace every 60 seconds; resume exactly where you left off

### Deployment Flexibility
Three backends, zero code changes — swap by setting `TRANSCRIPTION_MODE` in `.env`:

| Mode | Setup | Best For |
|------|-------|----------|
| **Local** (transformers) | `uv sync` — no API key | Privacy-sensitive; dev/test; own GPU |
| **Cohere API** | Add `COHERE_API_KEY` | Zero-setup; machines without GPU |
| **vLLM** | `vllm serve` | Production throughput; hospital infra |

---

## Quick Start

```bash
git clone <repo-url>
cd medical-workbench

./setup.sh
$EDITOR .env        # only needed for api or vllm modes

./run.sh
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

For step-by-step instructions, see [QUICKSTART.md](QUICKSTART.md).

---

## Architecture

```
medical_workbench/
├── app.py                      # Streamlit entry point
├── pages/
│   ├── 01_Transcription.py    # File + batch upload
│   ├── 02_Live_Stream.py       # Real-time microphone
│   ├── 03_Library.py           # Saved transcripts
│   ├── 04_Data_Analysis.py     # CSV import + stats + charts
│   ├── 05_Benchmarking.py       # WER + RTFx evaluation
│   └── 06_Sessions.py          # Session management + PDF export
├── services/
│   ├── transcription_service.py # Cohere Transcribe (local / API / vLLM)
│   ├── streaming_service.py     # sounddevice mic → chunked stream
│   ├── library_db.py            # SQLite transcript library
│   ├── benchmarking_service.py  # WER + RTFx computation
│   └── export_service.py        # PDF/DOCX generation
├── models/                      # Pydantic dataclasses
├── components/                  # Reusable UI widgets
└── utils/
    └── config.py               # Environment + backend mode config
```

---

## Requirements

- Python 3.10+
- GPU with 8GB+ VRAM recommended (works on CPU — slower)
- For local transcription: `transformers>=5.4.0`, `torch`, `soundfile`, `librosa`

---

## License

Apache 2.0 — See [LICENSE](LICENSE) for full text.

---

## Built With

- [Cohere Transcribe](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026) — 2B-param Conformer ASR model
- [Streamlit](https://streamlit.io) — Web application framework
- [Plotly](https://plotly.com) — Interactive visualizations
- [scipy](https://scipy.org) — Statistical computations
- [Biopython](https://biopython.org) — Bioinformatics toolkits
