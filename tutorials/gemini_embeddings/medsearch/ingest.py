"""
Ingestion pipeline for medical research content.

Supported file types and their medical use cases:
    .txt / .md  — abstracts, clinical notes, case summaries
    .pdf        — research papers, clinical guidelines (auto-chunked at 6 pages)
    .jpg / .png — X-rays, MRI slices, CT scans, pathology slides, ultrasound images
    .mp3 / .wav / .m4a — conference recordings, grand rounds, dictations
    .mp4 / .mov — surgical procedure clips, case presentation videos (must be ≤120s)

All content is embedded with Gemini Embedding 2 and stored in ChromaDB in a
unified vector space, enabling cross-modal retrieval from any query type.

Usage:
    # Index all files in ./media
    python -m medsearch.ingest --media ./media --db ./medsearch_db

    # Or call from Python
    from medsearch import ingest_directory
    ingest_directory("./media")
"""

import os
import uuid
from pathlib import Path

import chromadb
from dotenv import load_dotenv

from .utils import configure, get_mime, upload_and_wait, delete_file, embed, split_pdf

load_dotenv()


def get_collection(db_path: str = None) -> chromadb.Collection:
    path = db_path or os.getenv("MEDSEARCH_DB_PATH", "./medsearch_db")
    client = chromadb.PersistentClient(path=path)
    return client.get_or_create_collection(
        name="medical_research",
        metadata={"hnsw:space": "cosine"},
    )


def _store(collection, embedding: list, metadata: dict, document: str):
    collection.add(
        ids=[str(uuid.uuid4())],
        embeddings=[embedding],
        metadatas=[metadata],
        documents=[document],
    )


# ---------------------------------------------------------------------------
# Per-modality ingestion functions
# ---------------------------------------------------------------------------

def ingest_text(text: str, collection, metadata: dict = None):
    """
    Embed and store a text snippet.

    Examples: PubMed abstract, clinical note, case summary, image caption.

    metadata suggestions:
        {"type": "abstract", "title": "...", "author": "...", "pmid": "..."}
    """
    emb = embed(text, task_type="RETRIEVAL_DOCUMENT")
    meta = {"modality": "text", **(metadata or {})}
    _store(collection, emb, meta, text[:1000])
    print(f"  [text]  indexed {len(text)} chars")


def ingest_image(path: str, collection, metadata: dict = None):
    """
    Embed and store a medical image directly (no upload needed for JPEG/PNG).

    Examples: chest X-ray, CT slice, MRI scan, pathology slide, ultrasound frame.

    metadata suggestions:
        {"type": "xray", "body_part": "chest", "diagnosis": "pneumonia", "patient_id": "..."}
    """
    from PIL import Image
    img = Image.open(path)
    emb = embed(img, task_type="RETRIEVAL_DOCUMENT")
    meta = {"modality": "image", "source": str(path), **(metadata or {})}
    _store(collection, emb, meta, f"[image: {Path(path).name}]")
    print(f"  [image] {Path(path).name}")


def ingest_pdf(path: str, collection, metadata: dict = None):
    """
    Embed and store a research paper or clinical guideline.
    PDFs longer than 6 pages are automatically split into chunks.
    Each chunk gets its own embedding with page range in metadata.

    metadata suggestions:
        {"type": "paper", "title": "...", "journal": "...", "year": "2025", "doi": "..."}
    """
    chunks = split_pdf(path)

    # split_pdf returns [(chunk_path, first_page, last_page), ...]
    # or just [original_path] if ≤6 pages — normalise to tuples
    if chunks and isinstance(chunks[0], str):
        chunks = [(chunks[0], 0, None)]

    total = len(chunks)
    for chunk_path, p_start, p_end in chunks:
        file = upload_and_wait(chunk_path, "application/pdf")
        emb = embed(file, task_type="RETRIEVAL_DOCUMENT")
        page_label = f"pp.{p_start + 1}-{p_end + 1}" if p_end is not None else "full"
        meta = {
            "modality": "pdf",
            "source": str(path),
            "pages": page_label,
            "total_chunks": total,
            **(metadata or {}),
        }
        _store(collection, emb, meta, f"[pdf: {Path(path).name} — {page_label}]")
        delete_file(file)
        if chunk_path != str(path):
            os.unlink(chunk_path)
        print(f"  [pdf]   {Path(path).name} ({page_label})")


def ingest_audio(path: str, collection, metadata: dict = None):
    """
    Embed and store an audio recording natively (no transcription step).

    Examples: conference talk, grand rounds recording, clinical dictation, podcast.
    Supported: MP3, WAV, M4A (≤80s recommended per the model's audio limit).

    metadata suggestions:
        {"type": "conference_talk", "event": "RSNA 2025", "speaker": "...", "topic": "..."}
    """
    file = upload_and_wait(path)
    emb = embed(file, task_type="RETRIEVAL_DOCUMENT")
    meta = {"modality": "audio", "source": str(path), **(metadata or {})}
    _store(collection, emb, meta, f"[audio: {Path(path).name}]")
    delete_file(file)
    print(f"  [audio] {Path(path).name}")


def ingest_video(path: str, collection, metadata: dict = None):
    """
    Embed and store a video clip.

    Examples: surgical procedure, case presentation, technique demonstration.

    IMPORTANT: The model accepts ≤120s per clip. Pre-split longer recordings
    (e.g. with ffmpeg: ffmpeg -i long.mp4 -t 120 -c copy clip_001.mp4) and
    pass offset metadata so you can seek back to the right timestamp.

    metadata suggestions:
        {"type": "procedure", "procedure": "laparoscopic cholecystectomy",
         "offset_seconds": 0, "source_recording": "full_surgery.mp4"}
    """
    file = upload_and_wait(path)
    emb = embed(file, task_type="RETRIEVAL_DOCUMENT")
    meta = {"modality": "video", "source": str(path), **(metadata or {})}
    _store(collection, emb, meta, f"[video: {Path(path).name}]")
    delete_file(file)
    print(f"  [video] {Path(path).name}")


# ---------------------------------------------------------------------------
# Bulk ingestion
# ---------------------------------------------------------------------------

# Maps file extensions to their ingest function
_INGEST = {
    ".txt":  lambda p, c, m: ingest_text(open(p, encoding="utf-8").read(), c, m),
    ".md":   lambda p, c, m: ingest_text(open(p, encoding="utf-8").read(), c, m),
    ".pdf":  ingest_pdf,
    ".jpg":  ingest_image,
    ".jpeg": ingest_image,
    ".png":  ingest_image,
    ".mp3":  ingest_audio,
    ".wav":  ingest_audio,
    ".m4a":  ingest_audio,
    ".mp4":  ingest_video,
    ".mov":  ingest_video,
}


def ingest_directory(media_dir: str = None, db_path: str = None, metadata: dict = None):
    """
    Walk a directory and ingest all supported files into ChromaDB.

    Args:
        media_dir: Root folder to scan (falls back to MEDSEARCH_MEDIA_DIR env var)
        db_path:   ChromaDB storage path (falls back to MEDSEARCH_DB_PATH env var)
        metadata:  Extra metadata fields added to every item (e.g. study name, date)

    Typical media directory layout:
        media/
            abstracts/       ← .txt files
            papers/          ← .pdf research papers
            imaging/         ← .jpg / .png scans
            recordings/      ← .mp3 conference talks
            procedures/      ← .mp4 procedure clips (≤120s each)
    """
    configure()
    collection = get_collection(db_path)
    media_dir = media_dir or os.getenv("MEDSEARCH_MEDIA_DIR", "./media")

    all_files = [p for p in Path(media_dir).rglob("*") if p.is_file()]
    supported = [f for f in all_files if f.suffix.lower() in _INGEST]
    skipped = len(all_files) - len(supported)

    print(f"Indexing {len(supported)} files from '{media_dir}' ({skipped} skipped)\n")

    errors = []
    for f in supported:
        try:
            _INGEST[f.suffix.lower()](str(f), collection, metadata)
        except Exception as e:
            print(f"  [ERROR] {f.name}: {e}")
            errors.append((str(f), str(e)))

    print(f"\nDone. Index size: {collection.count()} items.")
    if errors:
        print(f"Errors ({len(errors)}):")
        for path, msg in errors:
            print(f"  {path}: {msg}")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(
        description="Ingest medical research content into MedSearch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--media", default=None, help="Media directory to ingest")
    p.add_argument("--db", default=None, help="ChromaDB storage path")
    args = p.parse_args()

    ingest_directory(media_dir=args.media, db_path=args.db)
