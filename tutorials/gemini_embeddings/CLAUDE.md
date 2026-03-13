# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Tutorial repository for **Gemini Embedding 2** (`gemini-embedding-2-preview`), Google's first natively multimodal embedding model. The primary app is **MedSearch** — a medical research intelligence tool that indexes research papers, medical images, audio recordings, and procedure videos into a single unified vector index and retrieves across all modalities from one query.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # add your GEMINI_API_KEY
```

Get a free key at https://aistudio.google.com/app/apikey.

## Running MedSearch

```bash
# Index all files in ./media
python -m medsearch.ingest --media ./media --db ./medsearch_db

# Text search (cross-modal: returns images, PDFs, audio, video)
python -m medsearch.search --query "bilateral pneumonia infiltrates"

# Image search (upload a scan → finds papers, similar images, audio)
python -m medsearch.search --image ./media/imaging/xray_001.jpg

# Combined image + text
python -m medsearch.search --image ./media/imaging/xray_001.jpg --query "ground glass opacity"

# Filter to one modality
python -m medsearch.search --query "ARDS management" --modality pdf

# Interactive REPL
python -m medsearch.search --interactive
```

## Architecture

```
medsearch/
    utils.py    — configure(), embed(), upload_and_wait(), split_pdf(), normalize()
    ingest.py   — per-modality ingest functions + ingest_directory() bulk runner
    search.py   — search() + interactive_search() + CLI entry point
```

**Key design decisions:**
- All embeddings use **1536 dimensions** (MRL truncation from 3072) — good quality/storage balance. Change `DEFAULT_DIM` in `utils.py` for 768 (fast) or 3072 (max quality).
- ChromaDB collection uses `hnsw:space=cosine`. Embeddings are L2-normalized before storage so cosine distance is meaningful.
- The **File API** is used for video, audio, and PDF. Files are deleted from the API after embedding to avoid quota buildup.
- PDFs longer than 6 pages are automatically split into 6-page chunks via PyMuPDF; each chunk gets its own embedding with a `pages` metadata field.
- Videos **must be ≤120s** per clip. Pre-split longer recordings with ffmpeg and pass `offset_seconds` in metadata.
- Cross-modal query: passing `[PIL.Image, "text string"]` as `content` to `embed()` produces **one aggregate embedding** that combines both modalities.

## Key Concepts

- **Model ID**: `models/gemini-embedding-2-preview`
- **SDK**: `google-genai` (new SDK, `client().models.embed_content()`)
- **Modality limits**: 6 images / 1 video (≤120s) / audio (≤80s) / PDF (≤6 pages) per request
- **File API**: required for video, audio, PDF — upload async, poll until `ACTIVE`
- **Task types**: `RETRIEVAL_DOCUMENT` for corpus, `RETRIEVAL_QUERY` for search queries
- `reference.txt` — canonical reference for API behavior and limits; consult before changing embedding logic
