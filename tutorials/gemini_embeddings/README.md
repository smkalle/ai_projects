# MedSearch — Medical Research Intelligence

Cross-modal medical research search powered by **Gemini Embedding 2**, Google's first natively multimodal embedding model.

Index research papers, medical images, audio recordings, and procedure videos into **one unified vector space**. Search everything from a single query — text, image, or both combined.

## What makes this different

A text query like `"bilateral pneumonia infiltrates"` returns:
- Chest X-rays showing pneumonia patterns
- Research paper sections describing imaging findings
- Conference audio clips discussing the topic
- Procedure videos demonstrating diagnostic technique

**All ranked together by semantic similarity** — no keyword matching, no modality-specific pipelines.

## Architecture

```
Query (text / image / both)
    |
    v
Gemini Embedding 2  →  1536-dim normalized vector
    |
    v
ChromaDB (cosine similarity)  →  ranked results across all modalities
```

**5 input modalities**, one model, one index:

| Modality | Input | Embedding path |
|----------|-------|----------------|
| Text | Abstracts, notes, captions | Direct embed |
| Images | X-rays, MRI, CT, pathology | Direct embed (PIL) |
| PDFs | Research papers (any length) | Auto-chunk at 6 pages → File API |
| Audio | Conference talks, dictations | File API (native — no transcription) |
| Video | Procedure clips (≤120s) | File API |

## Quick start

```bash
# 1. Setup (uses uv for fast installs)
./setup.sh

# 2. Add your Gemini API key (free: https://aistudio.google.com/app/apikey)
nano .env

# 3. Download sample medical data (Open-i, PubMed, PMC — all open-source)
.venv/bin/python download_samples.py

# 4. Index everything
./run.sh ingest

# 5. Search
./run.sh search -q "bilateral pneumonia infiltrates"
./run.sh search -i media/imaging/chest_xray.jpg
./run.sh search                    # interactive REPL

# 6. Web UI
.venv/bin/python app.py            # http://localhost:7860
```

## Project structure

```
medsearch/
    utils.py    — embed(), upload_and_wait(), split_pdf(), normalize()
    ingest.py   — per-modality ingestion + bulk directory walker
    search.py   — cross-modal search + interactive REPL
app.py          — Gradio web workbench (Search, Examples, Index, About)
download_samples.py — fetch open-source medical samples from NIH/PubMed/PMC
setup.sh / run.sh / ingest.sh / search.sh — shell entry points
```

## Key technical details

- **Model**: `gemini-embedding-2-preview` (March 2026)
- **Dimensions**: 1536 (Matryoshka truncation from 3072). Change `DEFAULT_DIM` in `utils.py` for 768 (fast) or 3072 (max quality).
- **Similarity**: Cosine distance on L2-normalized vectors
- **PDF chunking**: Auto-split at 6 pages (Gemini File API limit) via PyMuPDF
- **Audio**: Natively embedded — no transcription step needed
- **Video**: ≤120s per clip. Pre-split longer recordings with ffmpeg.
- **Combined queries**: Image + text produces one aggregate embedding for highest precision

## Data sources

All samples are open-source and free:

| Source | Content | License |
|--------|---------|---------|
| [Open-i / MedPix](https://openi.nlm.nih.gov/) | Medical images | Public domain (NIH) |
| [PubMed E-utilities](https://www.ncbi.nlm.nih.gov/home/develop/api/) | Abstracts | Free API |
| [PMC Open Access](https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/) | Research papers | CC BY / CC BY-NC |

## Tech stack

- [google-genai](https://pypi.org/project/google-genai/) — Gemini API SDK
- [ChromaDB](https://www.trychroma.com/) — persistent vector store
- [Gradio](https://www.gradio.app/) — web UI
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF processing
- [uv](https://docs.astral.sh/uv/) — Python package manager

## Requirements

- Python 3.11+
- Gemini API key (free tier works)
- ~500 MB disk for dependencies + sample data

## License

MIT
