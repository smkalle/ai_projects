"""
Shared utilities: API configuration, embedding, normalization, PDF chunking.

All embeddings use 1536 dimensions by default — a good balance between quality
and storage cost using Matryoshka (MRL). Switch to 3072 for max quality or 768
for speed-sensitive workloads.

Uses the new google-genai SDK (replaces deprecated google-generativeai).
"""

import os
import time
import tempfile
from pathlib import Path

import numpy as np
from google import genai
from google.genai import types

MODEL = "gemini-embedding-2-preview"
DEFAULT_DIM = 1536  # recommended sweet spot; 3072 for max quality

MIME_MAP = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".mp4":  "video/mp4",
    ".mov":  "video/quicktime",
    ".mp3":  "audio/mpeg",
    ".wav":  "audio/wav",
    ".m4a":  "audio/mp4",
    ".pdf":  "application/pdf",
}

# Module-level client, initialized by configure()
_client: genai.Client | None = None


def configure():
    """Load API key from environment and initialize the genai Client."""
    global _client
    if _client is not None:
        return
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY not set. "
            "Copy .env.example to .env and add your key from https://aistudio.google.com/app/apikey"
        )
    _client = genai.Client(api_key=api_key)


def client() -> genai.Client:
    """Return the configured genai Client (calls configure() if needed)."""
    if _client is None:
        configure()
    return _client


def get_mime(path: str) -> str:
    ext = Path(path).suffix.lower()
    mime = MIME_MAP.get(ext)
    if not mime:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {list(MIME_MAP)}")
    return mime


def upload_and_wait(path: str, mime_type: str = None):
    """
    Upload a file via the Gemini File API and block until it is ACTIVE.
    Required for video, audio, and PDF (large binary files).
    Returns the file object.
    """
    if mime_type is None:
        mime_type = get_mime(path)
    print(f"    uploading {Path(path).name}...", end=" ", flush=True)
    file = client().files.upload(file=path, config={"mime_type": mime_type})
    while file.state == "PROCESSING":
        time.sleep(3)
        file = client().files.get(name=file.name)
    if file.state != "ACTIVE":
        raise RuntimeError(f"Upload failed ({file.state}): {path}")
    print("ready")
    return file


def delete_file(file):
    """Clean up a File API upload to avoid quota buildup."""
    try:
        client().files.delete(name=file.name)
    except Exception:
        pass


def normalize(emb) -> list:
    """L2-normalize an embedding vector (required after MRL truncation)."""
    v = np.array(emb, dtype=np.float32)
    norm = np.linalg.norm(v)
    return (v / norm).tolist() if norm > 0 else v.tolist()


def embed(content, task_type: str = "RETRIEVAL_DOCUMENT", dim: int = DEFAULT_DIM) -> list:
    """
    Embed any content and return a normalized vector.

    content can be:
        str                 — text (abstract, note, caption)
        PIL.Image           — medical image (X-ray, pathology slide, MRI)
        File API object     — uploaded video / audio / PDF
        list                — interleaved mix of the above (produces ONE aggregate embedding)

    task_type:
        "RETRIEVAL_DOCUMENT" — use for all indexed corpus items
        "RETRIEVAL_QUERY"    — use for user search queries
    """
    # Build the contents list for the new SDK
    if isinstance(content, list):
        contents = content
    else:
        contents = [content]

    result = client().models.embed_content(
        model=MODEL,
        contents=contents,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=dim,
        ),
    )
    # result.embeddings is a list of ContentEmbedding objects
    raw = result.embeddings[0].values
    return normalize(raw)


def split_pdf(path: str, max_pages: int = 6) -> list:
    """
    Split a PDF into ≤max_pages chunks (Gemini File API limit is 6 pages per request).
    Returns a list of file paths — the original path if ≤6 pages, otherwise temp files.
    Caller is responsible for deleting temp files after use.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF is required for PDF splitting: pip install PyMuPDF")

    doc = fitz.open(path)
    total = len(doc)
    if total <= max_pages:
        doc.close()
        return [path]

    chunks = []
    for start in range(0, total, max_pages):
        end = min(start + max_pages, total)
        sub = fitz.open()
        sub.insert_pdf(doc, from_page=start, to_page=end - 1)
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        sub.save(tmp.name)
        sub.close()
        chunks.append((tmp.name, start, end - 1))  # (path, first_page, last_page)
    doc.close()
    return chunks  # list of (path, first_page, last_page)
