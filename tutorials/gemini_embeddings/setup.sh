#!/usr/bin/env bash
set -euo pipefail

# ── MedSearch Setup ───────────────────────────────────────────────────────────
# Uses uv for fast, reproducible installs. Run once before first use.
# https://docs.astral.sh/uv/

PYTHON_VERSION="3.11"
VENV_DIR=".venv"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Keep uv cache on same filesystem as venv to avoid cross-fs hard-link failures
export UV_CACHE_DIR="$SCRIPT_DIR/.uv_cache"

# ── Check uv ──────────────────────────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
    echo "uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Re-source shell so uv is on PATH
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
fi

echo "uv $(uv --version)"

# ── Virtual environment ────────────────────────────────────────────────────────
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR — skipping creation."
else
    echo "Creating virtual environment (Python $PYTHON_VERSION)..."
    uv venv "$VENV_DIR" --python "$PYTHON_VERSION"
fi

# ── Install dependencies ───────────────────────────────────────────────────────
echo "Installing dependencies from requirements.txt..."
uv pip install -r requirements.txt --python "$VENV_DIR/bin/python" --link-mode=copy

# ── .env setup ────────────────────────────────────────────────────────────────
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "  .env created from .env.example."
    echo "  --> Open .env and set your GEMINI_API_KEY before running."
    echo "      Get a free key: https://aistudio.google.com/app/apikey"
else
    echo ".env already exists — skipping."
fi

# ── Media directory structure ─────────────────────────────────────────────────
mkdir -p media/{abstracts,papers,imaging,recordings,procedures}

echo ""
echo "Setup complete. Next steps:"
echo "  1. Edit .env  →  add your GEMINI_API_KEY"
echo "  2. Add files to ./media/ subdirectories"
echo "  3. ./ingest.sh            (index all media)"
echo "  4. ./search.sh            (interactive search)"
echo "  5. ./search.sh -q 'query' (single query)"
