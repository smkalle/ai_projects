# Implementation Plan: Medical Researcher Workbench

**Version**: 1.0
**Date**: 2026-03-29
**Status**: Draft

---

## Overview

This plan implements the BRD v2.0 for a medical researcher workbench built on **Cohere Transcribe** as the core engine. The workbench is a Streamlit multi-page app using `uv` for package management. MVP scope covers the core transcription pipeline (file upload, batch, live stream) and the library/benchmarking infrastructure.

---

## Implementation Order

### Phase 1: Project Scaffold

**Goal**: Stand up the empty shell project with `uv`, Streamlit, and all directory scaffolding.

| Step | File | Description |
|------|------|-------------|
| 1.1 | `pyproject.toml` | All dependencies (transformers, torch, soundfile, sounddevice, streamlit, plotly, pandas, scipy, biopython, reportlab, python-dotenv) |
| 1.2 | `.env.example` | `TRANSCRIPTION_MODE`, `MODEL_PATH`, `DEVICE`, `COHERE_API_KEY`, `VLLM_BASE_URL` |
| 1.3 | `setup.sh` | `uv sync`, auto-create `.env` from `.env.example` |
| 1.4 | `run.sh` | `uv run streamlit run app.py` |
| 1.5 | `utils/config.py` | Load `.env`, expose `get_transcription_config()` returning mode + params |
| 1.6 | `models/transcript.py` | `Transcript` dataclass: id, title, language, punctuation, audio_path, transcript_text, created_at, tags |
| 1.7 | `app.py` | Streamlit multi-page shell with sidebar nav linking to all 6 pages |

**Deliverable**: `uv sync && ./run.sh` launches empty Streamlit shell.

---

### Phase 2: Transcription Service (Local Transformer)

**Goal**: Direct `CohereLabs/cohere-transcribe-03-2026` via `transformers` with no API key needed.

| Step | File | Description |
|------|------|-------------|
| 2.1 | `services/transcription_service.py` | `TranscriptionService` class. Loads model/processor at init (cached). `transcribe(audio_path, language, punctuation) -> str`. Uses `device_map="auto"`, `torch_dtype=torch.float16` if CUDA available. |
| 2.2 | `utils/audio_utils.py` | `load_audio(path)` wrapper using `transformers.audio_utils.load_audio` at 16kHz. `validate_format(path)` checks extension. |
| 2.3 | `models/benchmark_result.py` | `BenchmarkResult` dataclass: audio_path, reference_text, transcript_text, wer, rtfx, language, duration_s, processing_time_s |
| 2.4 | `services/benchmarking_service.py` | `compute_wer(reference, hypothesis) -> float` using `jiwer`. `compute_rtfx(duration_s, processing_time_s) -> float`. `run_benchmark(audio_path, reference_text, language) -> BenchmarkResult` |

**Deliverable**: `python -c "from services.transcription_service import TranscriptionService; print(TranscriptionService().transcribe('demo.wav', 'en', True))"` outputs text.

---

### Phase 3: Transcription Page (Single File + Batch)

**Goal**: `pages/01_Transcription.py` — the primary UI for file-based transcription.

| Step | Component | Description |
|------|-----------|-------------|
| 3.1 | `components/audio_uploader.py` | Drag-drop file widget; validates wav/mp3/m4a; shows file info (duration, sample rate if obtainable) |
| 3.2 | `components/language_selector.py` | Dropdown of 14 languages with icons |
| 3.3 | `components/transcript_viewer.py` | Read-only display of transcript text with copy button |
| 3.4 | `pages/01_Transcription.py` | File uploader → language + punctuation toggles → "Transcribe" button → progress spinner → transcript viewer → "Save to Library" + "Download .txt" buttons |

**Deliverable**: Upload a wav file, get back a transcript with save/export options.

---

### Phase 4: Batch Transcription

**Goal**: Multi-file queue processing with per-file status and aggregate results.

| Step | Component | Description |
|------|-----------|-------------|
| 4.1 | `components/batch_queue.py` | Multi-file drag-drop; file list with status chips (pending/running/done/error); per-file language selection |
| 4.2 | `pages/01_Transcription.py` (batch tab) | Add batch tab alongside single-file tab. Run all queued files sequentially; progress bar per file + overall. Download all as ZIP on completion. |

**Deliverable**: Upload 5 audio files, see per-file progress, download all transcripts at once.

---

### Phase 5: Live Stream Page

**Goal**: `pages/02_Live_Stream.py` — real-time microphone transcription.

| Step | Component | Description |
|------|-----------|-------------|
| 5.1 | `services/streaming_service.py` | `StreamingService`. `start_stream(language, callback)`: starts `sounddevice` InputStream at 16kHz mono float32. Accumulates chunks in thread-safe queue. Every 5s buffer → `transcription_service.transcribe()`. Yields transcript chunks via callback. `stop_stream()` terminates. |
| 5.2 | `pages/02_Live_Stream.py` | Start/Stop button, language selector, rolling transcript display (updates in place), clear button. Status indicator (Recording / Stopped). |

**Deliverable**: Press record, speak into mic, see live transcript appear in <3s.

---

### Phase 6: Library & Persistence

**Goal**: SQLite-backed transcript library with save, search, edit, tag, and export.

| Step | Component | Description |
|------|-----------|-------------|
| 6.1 | `services/library_db.py` | `LibraryDB` class wrapping `sqlite3`. `save_transcript(t: Transcript)`, `get_all()`, `get_by_id(id)`, `update(id, **fields)`, `delete(id)`, `search(query)`, `get_by_tag(tag)`. Schema: `transcripts(id, title, language, punctuation, audio_path, transcript_text, created_at, tags)`. |
| 6.2 | `pages/03_Library.py` | List view of saved transcripts (cards with title, language, date). Search bar filters by title/content. Click card → detail view with editable transcript text, tag editor, "Export .txt", "Export .docx", delete button. |

**Deliverable**: Save a transcript, close the app, reopen, find it in the library.

---

### Phase 7: Benchmarking Page

**Goal**: `pages/05_Benchmarking.py` — WER/RTFx evaluation interface.

| Step | Component | Description |
|------|-----------|-------------|
| 7.1 | `components/benchmark_results.py` | Score cards: WER (green/amber/red), RTFx (numeric). Bar chart comparing multiple runs. |
| 7.2 | `pages/05_Benchmarking.py` | Upload audio file + upload reference transcript (.txt). Select language. "Run Benchmark" → calls `benchmarking_service.run_benchmark()`. Display `BenchmarkResult` with WER card, RTFx card, processing time, audio duration. History of past runs persisted in `~/.medical_workbench/benchmark_history.json`. |

**Deliverable**: Upload audio + reference, see WER < 10% on clean English demo.

---

### Phase 8: Data Analysis Page (MVP Only)

**Goal**: `pages/04_Data_Analysis.py` — CSV import and basic stats/charts.

| Step | Component | Description |
|------|-----------|-------------|
| 8.1 | `components/dataset_viewer.py` | Drag-drop CSV/Excel; data preview table (first 100 rows); column type indicators; filter builder UI (column + operator + value) |
| 8.2 | `pages/04_Data_Analysis.py` | Import section → dataset preview → filter builder → descriptive stats (n, mean, median, SD per numeric column) → Plotly chart selector (histogram, box, scatter). No cohort stratification or advanced stats in MVP. |

**Deliverable**: Upload a CSV, see summary stats and a histogram.

---

### Phase 9: Sessions & Export (MVP Only)

**Goal**: `pages/06_Sessions.py` — named sessions and PDF export.

| Step | Component | Description |
|------|-----------|-------------|
| 9.1 | `models/session.py` | `Session` dataclass: id, name, created_at, transcript_ids, dataset_path, chart_count |
| 9.2 | `services/export_service.py` | `export_pdf(session: Session, transcript: Transcript, charts: list) -> bytes`. Uses `reportlab`. Includes transcript text, metadata header, timestamp. |
| 9.3 | `pages/06_Sessions.py` | Named session save/load from JSON in `~/.medical_workbench/sessions/`. Auto-save every 60s via `st.session_state` persistence. PDF export button combining active transcript + any open charts. |

**Deliverable**: Save session, reload it, export a PDF with transcript + chart.

---

## Dependency Specification (pyproject.toml)

```toml
[project]
name = "medical-workbench"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    # Core (Cohere Transcribe from tutorial)
    "transformers>=5.4.0",
    "torch",
    "huggingface_hub",
    "soundfile",
    "librosa",
    "sentencepiece",
    "protobuf",
    # Real-time streaming (tutorial Step 5)
    "sounddevice",
    "numpy",
    # Workbench
    "streamlit>=1.28.0",
    "pandas>=2.0.0",
    "plotly>=5.0.0",
    "scipy",
    "biopython",           # PubMed Entrez
    "reportlab",           # PDF export
    "python-docx",         # DOCX export
    "python-dotenv>=1.0.0",
    "jiwer",               # WER computation
    "openai-whisper",      # Only if SNR estimation is needed from audio
]

[project.optional-dependencies.dev]
pytest = ["pytest>=7.4.0"]
```

---

## Critical Files to Create (in order)

```
medical_workbench/
├── pyproject.toml                  # Step 1.1
├── .env.example                    # Step 1.2
├── setup.sh                        # Step 1.3
├── run.sh                          # Step 1.4
├── verify.sh                       # Step 1.4
├── app.py                          # Step 1.7
├── utils/
│   ├── __init__.py
│   └── config.py                   # Step 1.5
├── models/
│   ├── __init__.py
│   ├── transcript.py               # Step 1.6
│   └── benchmark_result.py         # Step 2.3
├── services/
│   ├── __init__.py
│   ├── transcription_service.py   # Step 2.1
│   ├── library_db.py               # Step 6.1
│   └── benchmarking_service.py     # Step 2.4
├── components/
│   ├── __init__.py
│   ├── audio_uploader.py           # Step 3.1
│   ├── language_selector.py         # Step 3.2
│   ├── transcript_viewer.py        # Step 3.3
│   ├── batch_queue.py              # Step 4.1
│   ├── dataset_viewer.py           # Step 8.1
│   └── benchmark_results.py        # Step 7.1
├── pages/
│   ├── 01_Transcription.py        # Step 3.4 + 4.2
│   ├── 02_Live_Stream.py           # Step 5.2
│   ├── 03_Library.py              # Step 6.2
│   ├── 04_Data_Analysis.py         # Step 8.2
│   ├── 05_Benchmarking.py          # Step 7.2
│   └── 06_Sessions.py              # Step 9.3
├── utils/
│   └── audio_utils.py              # Step 2.2
└── services/
    ├── streaming_service.py        # Step 5.1
    └── export_service.py           # Step 9.2
```

---

## Out of Scope for MVP

- **PubMed integration** (AN-01) — requires Biopython Entrez setup + UI; deferred post-MVP
- **DOCX export** (MD-03) — TXT export only in MVP
- **Inline transcript editing with version history** (MD-02) — basic text edit without versioning in MVP
- **SOAP note auto-generation** (WR-01) — requires LLM integration; deferred post-MVP
- **Gradio UI** (TR-07) — Streamlit covers browser access; Gradio is a Step 6 tutorial artifact
- **vLLM and Cohere API modes** — MVP ships with local transformers only; API/vLLM modes are deployment configuration

---

## Verification Plan

| Test | Command | Pass Criterion |
|------|---------|----------------|
| App launches | `./run.sh` | Streamlit opens without error |
| Basic transcription | Upload `demo.wav` (en) | Transcript appears in <30s on GPU |
| Batch (3 files) | Queue 3 files | All 3 complete; ZIP downloads |
| Live stream | Record 10s of speech | Transcript appears within 3s |
| Library save/load | Save transcript, restart app | Transcript appears in library |
| WER benchmark | Upload audio + reference | WER computed and displayed |
| PDF export | Export session as PDF | PDF opens with transcript text |

---

## Reference: code_eval_workbench Patterns to Follow

- `uv sync` for all dependency management; `uv run` for all executions
- `setup.sh` creates `.env` from `.env.example` if absent
- Single `app.py` at root with `st.tabs()` for section navigation
- `get_*_config()` function at module level caches config at import time
- `conftest.py` sets env vars before module imports for test isolation
- Pydantic dataclasses for all result models
- Results/history persisted to JSON in `~/.medical_workbench/`
- Custom CSS via `st.markdown()` for score cards and color coding
- Plotly charts with dark theme matching the workbench aesthetic
