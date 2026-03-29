# Business Requirements Document: Medical Researcher Workbench

**Version**: 2.0
**Date**: 2026-03-29
**Status**: Draft

---

## 1. Executive Summary

### 1.1 Purpose
A full-fledged, production-grade research workbench for medical researchers built around **Cohere Transcribe** as the core speech-to-text engine. The workbench enables physicians and medical researchers to transcribe dictation, capture multilingual patient interviews, process long-form medical recordings, and work with live clinical conversations — all with literature review, data analysis, and report writing built in.

### 1.2 Core Technology
**Cohere Transcribe (cohere-transcribe-03-2026)** is the foundational capability:
- 2B-param Conformer-based ASR — 5.42% WER (SOTA on HF Open ASR Leaderboard)
- 14 languages: en, fr, de, it, es, pt, el, nl, pl, ar, vi, zh, ja, ko
- Optional punctuation (on/off)
- Long-form: handles 55+ minute audio via internal chunking
- Real-time microphone streaming with low latency
- Batched inference for multiple files
- Apache 2.0 license; runs locally or via Cohere API

### 1.3 Target Users
- Physicians dictating clinical notes
- Clinical researchers analyzing patient interviews and focus groups
- Medical educators processing lecture recordings
- Translational researchers working with multilingual patient cohorts

---

## 2. Feature Map: Tutorial Steps → Medical Workbench Pages

Each step from the tutorial.MD maps to a workbench capability:

| Tutorial Step | Workbench Feature | Medical Use Case |
|--------------|-------------------|-----------------|
| Step 2: Basic Transcription | File Upload → Transcript | Transcribe pre-recorded patient dictations, lecture recordings |
| Step 3: Multilingual + Punctuation | Language selector, punctuation toggle | Multilingual intake interviews; clean vs raw transcript for EHR |
| Step 4: Long-Form + Batched | Multi-file batch, long audio processing | Process 55-min seminar recordings; batch transcribe a week's dictations |
| Step 5: Real-Time Streaming | Live microphone transcription | Dictate notes in real-time during rounds; live patient interview capture |
| Step 6: Gradio Web Demo | Gradio-based UI with audio input | Browser-based demo for non-technical clinical staff |
| Step 7: Production Deployment | vLLM serving, Cohere API | Self-hosted or cloud deployment in hospital infrastructure |
| Step 8: Benchmarking | WER/RTFx benchmarking tab | Validate accuracy on domain-specific medical audio |

---

## 3. User Stories & Functional Requirements

### 3.1 Core Transcription (Cohere Transcribe)

| ID | User Story | Requirements |
|----|-----------|--------------|
| TR-01 | As a researcher, I want to upload an audio file and get a transcript | Accept wav/mp3/m4a; use Cohere Transcribe; display timestamped transcript |
| TR-02 | As a researcher, I want to select the source language from 14 options | Dropdown with all 14 languages; default to English |
| TR-03 | As a researcher, I want punctuation in transcripts for clinical notes | Toggle punctuation on/off; default on |
| TR-04 | As a researcher, I want to transcribe files over 55 minutes | Long-form chunking handled internally; progress indicator |
| TR-05 | As a researcher, I want to batch-transcribe multiple files | Queue multiple files; batch process with Cohere Transcribe; downloadable results |
| TR-06 | As a researcher, I want live transcription from my microphone | Real-time streaming via sounddevice; low-latency output; language selection |
| TR-07 | As a researcher, I want to run the workbench in a browser without installing Python | Gradio UI with upload/record + language selector + output |

### 3.2 Medical Documentation

| ID | User Story | Requirements |
|----|-----------|--------------|
| MD-01 | As a researcher, I want to save transcripts with metadata | Save to local SQLite: title, patient ID (anonymized), date, language, audio file ref, transcript text |
| MD-02 | As a researcher, I want to edit transcripts in-app | Inline text editing of transcript; version history |
| MD-03 | As a researcher, I want to export transcripts as .txt or .docx | One-click export; preserve timestamps |
| MD-04 | As a researcher, I want to flag sections of transcript | Highlight/keyword tag sections; filter by tag |
| MD-05 | As a researcher, I want to integrate with Cohere API for zero-setup | Fallback to `co.audio.transcriptions.create()` when local model unavailable |

### 3.3 Analysis & Research Tools

| ID | User Story | Requirements |
|----|-----------|--------------|
| AN-01 | As a researcher, I want to search PubMed and cross-reference with my transcripts | Entrez search; link findings to saved transcripts |
| AN-02 | As a researcher, I want to import clinical CSV/Excel datasets | Drag-drop; auto-detect column types; filter cohort |
| AN-03 | As a researcher, I want to run descriptive statistics on imported data | Mean, median, SD, CI; stratified by cohort |
| AN-04 | As a researcher, I want to visualize dataset distributions | Histogram, box plot, scatter via Plotly |
| AN-05 | As a researcher, I want to benchmark Cohere Transcribe WER on my own medical audio | Benchmarking tab; upload reference transcript; compute WER |

### 3.4 Writing & Collaboration

| ID | User Story | Requirements |
|----|-----------|--------------|
| WR-01 | As a researcher, I want AI-assisted drafting of clinical notes | Summarize transcript into structured SOAP note format |
| WR-02 | As a researcher, I want to format citations in AMA/APA style | Citation formatter using transcript metadata |
| WR-03 | As a researcher, I want to export a research session as a PDF report | Include transcript, annotations, dataset summary, figures |

---

## 4. Architecture

```
medical_workbench/
├── app.py                      # Streamlit application entry point
├── pages/                      # Multi-page navigation
│   ├── 01_Transcription.py    # File upload, batch, long-form (Cohere Transcribe)
│   ├── 02_Live_Stream.py       # Real-time microphone transcription
│   ├── 03_Library.py           # Saved transcripts, search, edit, export
│   ├── 04_Data_Analysis.py     # CSV/Excel import, stats, Plotly charts
│   ├── 05_Benchmarking.py       # WER/RTFx benchmarking against reference transcripts
│   └── 06_Sessions.py          # Session management + PDF export
├── components/                  # Reusable UI components
│   ├── audio_uploader.py        # Drag-drop audio upload with format validation
│   ├── language_selector.py     # 14-language dropdown with flag icons
│   ├── transcript_viewer.py    # Timestamped, editable transcript display
│   ├── batch_queue.py           # Multi-file queue with progress
│   ├── pubmed_search.py         # Entrez search widget
│   ├── dataset_viewer.py        # Data preview + filter builder
│   └── benchmark_results.py     # WER/RTFx display cards
├── services/                    # Business logic layer
│   ├── transcription_service.py # Cohere Transcribe integration (local + API)
│   ├── streaming_service.py     # Real-time mic streaming + chunking
│   ├── library_db.py            # SQLite library (transcripts, metadata, tags)
│   ├── benchmarking_service.py  # WER computation, RTFx measurement
│   ├── pubmed_service.py        # Biopython Entrez integration
│   └── export_service.py        # PDF/DOCX/TXT generation
├── models/                      # Data models
│   ├── transcript.py           # Transcript dataclass with metadata
│   ├── benchmark_result.py     # WER, RTFx, language, audio properties
│   └── session.py              # Named session state
├── utils/
│   ├── config.py               # Cohere API key, model path, vLLM config
│   ├── audio_utils.py          # Format conversion, validation, chunking helpers
│   └── pii_detector.py         # Basic PII detection in transcripts before export
├── requirements.txt
├── setup.sh                     # Dependency installation
├── run.sh                       # Streamlit launcher
└── .env.example
```

### 4.1 Transcription Backend Modes

The `transcription_service.py` supports three modes (selected via `.env`):

```env
# Mode 1: Local Transformers (default — no API key needed)
TRANSCRIPTION_MODE=local
MODEL_PATH=CohereLabs/cohere-transcribe-03-2026
DEVICE=cuda  # or cpu

# Mode 2: Cohere API (zero-setup)
TRANSCRIPTION_MODE=api
COHERE_API_KEY=...
COHERE_MODEL=cohere-transcribe-03-2026

# Mode 3: vLLM (high-throughput self-hosted)
TRANSCRIPTION_MODE=vllm
VLLM_BASE_URL=http://localhost:8000
```

### 4.2 Real-Time Streaming Architecture

Per tutorial Step 5:
- `sounddevice` InputStream at 16kHz mono float32
- Thread-safe queue accumulates chunks
- Every ~5s of audio → call transcription_service
- Language passed per stream session (no auto-detection)

### 4.3 Long-Form Handling

Per tutorial Step 4: processor handles chunking internally; audio_chunk_index returned for decode. No manual chunking needed up to 55+ minutes.

---

## 5. Benchmarking Tab

Per tutorial Step 8 — a dedicated benchmarking interface:

| Metric | How It's Measured |
|--------|-------------------|
| **WER** | Upload reference .txt; compute against transcript output |
| **RTFx** | `audio_duration / processing_time` — measures offline throughput |
| **Language** | Per-language breakdown of WER and RTFx |
| **Audio properties** | SNR estimate, duration, sample rate |

Use cases: Validate accuracy on domain-specific medical audio (accented speech, terminology-heavy recordings) before committing to production use.

---

## 6. Deployment Options

Per tutorial Step 7 — three deployment paths:

| Mode | When to Use | Setup |
|------|-------------|-------|
| **Local (transformers)** | Privacy-sensitive; small team; dev/test | `pip install transformers>=5.4.0`; no API key |
| **Cohere API** | Zero-setup; non-GPU machines | `COHERE_API_KEY` in `.env` |
| **vLLM** | Production; high-volume; hospital infra | `vllm serve CohereLabs/cohere-transcribe-03-2026` |

---

## 7. Out of Scope (v1)

- Direct EHR/EMR integration (Epic, Cerner)
- Automated systematic review workflows
- Diarization (who spoke when) — requires PyAnnote integration
- Fine-tuning Cohere Transcribe on medical audio
- Real-time translation (transcribe + translate pipeline)
- Multi-user collaborative sessions

---

## 8. Success Metrics (v1)

| Metric | Target |
|--------|--------|
| File transcription success rate | >95% for supported formats (wav, mp3, m4a) |
| Live stream latency | <3s end-to-end (chunk → transcript) |
| Long-form (55min) completion | 100% without OOM on 8GB GPU |
| Batch (10 files) throughput | All 10 completed within 3× single-file time |
| WER benchmark UI | WER computed and displayed within 5s of reference upload |
| Session export | PDF generated with all figures and transcript in <10s |

---

## 9. Dependencies

From tutorial.MD + additional for the full workbench:

```
# Core (from tutorial)
transformers>=5.4.0
torch
huggingface_hub
soundfile
librosa
sentencepiece
protobuf

# Real-time streaming (from tutorial Step 5)
sounddevice
numpy

# Web UI (from tutorial Step 6)
gradio

# Workbench extras
streamlit
biopython  # PubMed Entrez
scipy
statsmodels
plotly
pandas
python-docx
reportlab  # PDF export
sqlite-utils
```

---

## 10. Appendix: Reference Workbenches

Sibling implementations inform the architecture patterns:
- `code_eval_workbench/` — Streamlit multi-tab, CLI + UI modes, scoring service pattern
- `celltype-research-workbench/` — Agent chat, workflow modules, session state management
- `ai_drug_discovery/` — FastAPI + Streamlit, cited output, PDF report generation
