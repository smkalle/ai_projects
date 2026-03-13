#!/usr/bin/env bash
set -euo pipefail

# ── MedSearch — Single entry point ───────────────────────────────────────────
#
# Usage:
#   ./run.sh                                        # ingest + interactive search
#   ./run.sh ingest                                 # ingest only
#   ./run.sh search                                 # search only (interactive)
#   ./run.sh search -q "bilateral pneumonia"        # search with query
#   ./run.sh search -i media/imaging/xray.jpg       # search by image
#   ./run.sh search -q "ARDS" -m pdf                # filter by modality
# ─────────────────────────────────────────────────────────────────────────────

VENV_DIR=".venv"
PYTHON="$VENV_DIR/bin/python"

# ── Ensure setup has been run ─────────────────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "First run detected — running setup..."
    ./setup.sh
fi

# ── Load and validate .env ────────────────────────────────────────────────────
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "  .env created. Add your GEMINI_API_KEY then re-run:"
    echo "    echo 'GEMINI_API_KEY=AIza...' >> .env && ./run.sh"
    exit 1
fi

set -a; source .env; set +a

if [ -z "${GEMINI_API_KEY:-}" ] || [ "$GEMINI_API_KEY" = "your_key_here" ]; then
    echo "GEMINI_API_KEY is not set in .env"
    echo "  Get a free key: https://aistudio.google.com/app/apikey"
    echo "  Then: echo 'GEMINI_API_KEY=AIza...' >> .env"
    exit 1
fi

DB_PATH="${MEDSEARCH_DB_PATH:-./medsearch_db}"
MEDIA_DIR="${MEDSEARCH_MEDIA_DIR:-./media}"

# ── Subcommand dispatch ───────────────────────────────────────────────────────
CMD="${1:-}"
shift || true

case "$CMD" in

    ingest)
        echo "Ingesting '$MEDIA_DIR' → '$DB_PATH'"
        "$PYTHON" -m medsearch.ingest --media "$MEDIA_DIR" --db "$DB_PATH" "$@"
        ;;

    search)
        if [ $# -eq 0 ]; then
            "$PYTHON" -m medsearch.search --interactive --db "$DB_PATH"
        else
            "$PYTHON" -m medsearch.search --db "$DB_PATH" "$@"
        fi
        ;;

    "")
        # Default: ingest if DB is empty or missing, then launch interactive search
        ITEM_COUNT=0
        if [ -d "$DB_PATH" ]; then
            ITEM_COUNT=$("$PYTHON" -c "
import chromadb, os
try:
    c = chromadb.PersistentClient(path='$DB_PATH')
    print(c.get_collection('medical_research').count())
except Exception:
    print(0)
" 2>/dev/null || echo 0)
        fi

        if [ "$ITEM_COUNT" -eq 0 ]; then
            echo "Index is empty. Checking for files in '$MEDIA_DIR'..."
            FILE_COUNT=$(find "$MEDIA_DIR" -type f \( \
                -iname "*.txt" -o -iname "*.md" -o -iname "*.pdf" \
                -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \
                -o -iname "*.mp3" -o -iname "*.wav" -o -iname "*.m4a" \
                -o -iname "*.mp4" -o -iname "*.mov" \
            \) 2>/dev/null | wc -l || echo 0)

            if [ "$FILE_COUNT" -eq 0 ]; then
                echo ""
                echo "No media files found in '$MEDIA_DIR'."
                echo "Add files then run:  ./run.sh ingest"
                echo ""
                echo "Supported types:"
                echo "  media/abstracts/    ← .txt  (abstracts, notes)"
                echo "  media/papers/       ← .pdf  (research papers)"
                echo "  media/imaging/      ← .jpg / .png  (X-rays, MRI, CT, pathology)"
                echo "  media/recordings/   ← .mp3 / .wav  (conference talks, dictations)"
                echo "  media/procedures/   ← .mp4  (procedure clips, must be ≤120s)"
                exit 0
            fi

            echo "Found $FILE_COUNT file(s). Indexing now..."
            "$PYTHON" -m medsearch.ingest --media "$MEDIA_DIR" --db "$DB_PATH"
            echo ""
        else
            echo "Index: $ITEM_COUNT item(s) in '$DB_PATH'"
        fi

        echo "Launching search..."
        "$PYTHON" -m medsearch.search --interactive --db "$DB_PATH"
        ;;

    *)
        echo "Unknown command: $CMD"
        echo ""
        echo "Usage:"
        echo "  ./run.sh                         ingest (if needed) + interactive search"
        echo "  ./run.sh ingest                  index all files in ./media"
        echo "  ./run.sh search                  interactive search REPL"
        echo "  ./run.sh search -q 'query'       text search"
        echo "  ./run.sh search -i image.jpg     image search"
        echo "  ./run.sh search -q 'x' -m pdf    filter by modality"
        exit 1
        ;;
esac
