#!/usr/bin/env bash
set -euo pipefail

# ── MedSearch Search ──────────────────────────────────────────────────────────
# Search across all indexed medical research content (cross-modal).
#
# Usage:
#   ./search.sh                                        # interactive REPL
#   ./search.sh -q "bilateral pneumonia infiltrates"   # text query
#   ./search.sh -i ./media/imaging/xray_001.jpg        # image query
#   ./search.sh -i xray.jpg -q "ground glass opacity"  # combined
#   ./search.sh -q "ARDS management" -m pdf            # filter by modality
#   ./search.sh -q "intubation technique" -n 10        # more results
#
# Modality filter options: text | image | pdf | audio | video
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

# No args → launch interactive REPL
if [ $# -eq 0 ]; then
    "$VENV_DIR/bin/python" -m medsearch.search --interactive
else
    "$VENV_DIR/bin/python" -m medsearch.search "$@"
fi
