#!/usr/bin/env bash
set -euo pipefail

# ── MedSearch Ingest ──────────────────────────────────────────────────────────
# Walks ./media (or --media <dir>) and embeds all supported files into ChromaDB.
#
# Usage:
#   ./ingest.sh                          # index ./media into ./medsearch_db
#   ./ingest.sh --media /path/to/data    # custom media directory
#   ./ingest.sh --db /path/to/db         # custom ChromaDB path
#
# Supported files:
#   .txt / .md  — abstracts, notes
#   .pdf        — research papers (auto-chunked at 6 pages)
#   .jpg / .png — X-rays, MRI, pathology slides
#   .mp3 / .wav / .m4a — conference talks, dictations
#   .mp4 / .mov — procedure clips (must be ≤120s each)
# ─────────────────────────────────────────────────────────────────────────────

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

if [ ! -f .env ]; then
    echo ".env not found. Run ./setup.sh first and add your GEMINI_API_KEY."
    exit 1
fi

# Load .env
set -a; source .env; set +a

if [ -z "${GEMINI_API_KEY:-}" ] || [ "$GEMINI_API_KEY" = "your_key_here" ]; then
    echo "GEMINI_API_KEY is not set in .env."
    echo "Get a free key at https://aistudio.google.com/app/apikey"
    exit 1
fi

echo "Starting ingestion..."
"$VENV_DIR/bin/python" -m medsearch.ingest "$@"
