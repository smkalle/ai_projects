# MedSearch — Quick Start Guide

Cross-modal medical research search powered by **Gemini Embedding 2**.
Index research papers, medical images, audio recordings, and procedure videos
into one unified vector index. Search everything from a single query.

---

## 1. Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (installed automatically by `setup.sh` if missing)
- Gemini API key — free at https://aistudio.google.com/app/apikey

---

## 2. Setup (one time)

```bash
chmod +x setup.sh ingest.sh search.sh
./setup.sh
```

Then open `.env` and set your key:

```
GEMINI_API_KEY=AIza...your_key_here
```

---

## 3. Add your research content

Drop files into `./media/` subdirectories:

```
media/
  abstracts/       ← .txt files (PubMed abstracts, case summaries)
  papers/          ← .pdf research papers (any length — auto-chunked)
  imaging/         ← .jpg / .png (X-rays, CT, MRI, pathology slides)
  recordings/      ← .mp3 / .wav (conference talks, grand rounds)
  procedures/      ← .mp4 clips, each ≤120s (surgical videos)
```

You can use any folder structure — the ingestion pipeline scans recursively.

**Sample files to try first:**
- A chest X-ray JPEG
- A 2–3 page PDF abstract or clinical guideline
- A 60s MP3 clip from a radiology conference talk

---

## 4. Index your content

```bash
./ingest.sh
```

What happens per file type:

| Type | How it's indexed |
|---|---|
| `.txt` / `.md` | Embedded directly as text |
| `.pdf` | Uploaded via File API; auto-split into 6-page chunks |
| `.jpg` / `.png` | Embedded directly as image (no upload needed) |
| `.mp3` / `.wav` | Uploaded via File API; embedded natively (no transcription) |
| `.mp4` / `.mov` | Uploaded via File API; must be ≤120s per clip |

All embeddings go into a ChromaDB collection at `./medsearch_db/` using
1536-dimension vectors in a shared cosine similarity space.

---

## 5. Search

### Interactive REPL (recommended to start)

```bash
./search.sh
```

Inside the REPL:

```
Query> bilateral pneumonia infiltrates
Query> img:./media/imaging/chest_xray.jpg
Query> img:./media/imaging/chest_xray.jpg ground glass opacity
Query> q
```

### Single query

```bash
# Text query — returns matching PDFs, images, audio, video ranked together
./search.sh -q "BRCA1 mutation breast cancer prognosis"

# Image query — cross-modal: a scan finds related papers and conference audio
./search.sh -i ./media/imaging/ct_chest.jpg

# Combined image + text (highest precision)
./search.sh -i ./media/imaging/ct_chest.jpg -q "COVID pneumonia ground glass"

# Filter to one modality
./search.sh -q "intubation technique" -m video

# More results
./search.sh -q "ARDS ventilation strategy" -n 15
```

### Python API

```python
from dotenv import load_dotenv
load_dotenv()

from medsearch import ingest_text, search

# Index a single abstract
from medsearch.ingest import get_collection
collection = get_collection()
ingest_text(
    "Bilateral ground-glass opacification was the most common CT finding in COVID-19 pneumonia...",
    collection,
    metadata={"type": "abstract", "journal": "Radiology", "year": "2020"},
)

# Search
results = search("ground glass opacity CT findings", collection=collection)
for r in results:
    print(r["score"], r["modality"], r["source"])
```

---

## 6. Splitting long videos

The model accepts ≤120 seconds per video clip. For longer recordings use ffmpeg:

```bash
# Split into 2-minute segments
ffmpeg -i grand_rounds_full.mp4 -c copy -map 0 -segment_time 120 \
       -f segment -reset_timestamps 1 \
       media/recordings/grand_rounds_%03d.mp4
```

Pass `offset_seconds` in metadata so you can seek back to the right timestamp:

```python
from medsearch.ingest import ingest_video, get_collection
col = get_collection()
for i, clip in enumerate(sorted(Path("media/recordings").glob("grand_rounds_*.mp4"))):
    ingest_video(str(clip), col, metadata={
        "type": "grand_rounds",
        "topic": "ARDS ventilation",
        "offset_seconds": i * 120,
        "source_recording": "grand_rounds_full.mp4",
    })
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `GEMINI_API_KEY not set` | Add key to `.env` |
| `Upload failed: FAILED` | File may exceed modality limits (PDF >6 pages, video >120s, audio >80s) |
| `Virtual environment not found` | Run `./setup.sh` |
| Slow ingestion | File API upload speed depends on file size and network; audio/video/PDF are slower than images |
| Empty search results | Run `./ingest.sh` first; check `./medsearch_db/` exists |
