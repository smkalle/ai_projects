#!/usr/bin/env bash
# =============================================================================
# install.sh — Install all dependencies for the AI Commerce Agent
#
# Usage:
#   ./scripts/install.sh              # Install everything
#   ./scripts/install.sh --dev        # Install with dev/test dependencies
#   ./scripts/install.sh --venv       # Create a virtualenv first, then install
#   ./scripts/install.sh --venv --dev # Both
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

USE_VENV=false
DEV=false

for arg in "$@"; do
    case "$arg" in
        --venv)  USE_VENV=true ;;
        --dev)   DEV=true ;;
        -h|--help)
            echo "Usage: $0 [--venv] [--dev]"
            echo ""
            echo "Options:"
            echo "  --venv   Create and activate a Python virtualenv (.venv)"
            echo "  --dev    Also install dev/test dependencies (pytest, ruff, etc.)"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            exit 1
            ;;
    esac
done

cd "$PROJECT_DIR"

echo "======================================"
echo "  AI Commerce Agent — Installer"
echo "======================================"
echo ""
echo "Project dir : $PROJECT_DIR"
echo "Python      : $(python3 --version 2>&1)"
echo ""

# --- Optional virtualenv ---
if $USE_VENV; then
    VENV_DIR="$PROJECT_DIR/.venv"
    if [ ! -d "$VENV_DIR" ]; then
        echo "[1/4] Creating virtualenv at $VENV_DIR ..."
        python3 -m venv "$VENV_DIR"
    else
        echo "[1/4] Virtualenv already exists at $VENV_DIR"
    fi
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    echo "       Activated: $(which python)"
else
    echo "[1/4] Skipping virtualenv (use --venv to create one)"
fi

# --- Upgrade pip / setuptools ---
echo ""
echo "[2/4] Upgrading pip and setuptools ..."
python3 -m pip install --upgrade pip setuptools wheel --quiet

# --- Install core dependencies ---
echo ""
echo "[3/4] Installing project dependencies ..."
if $DEV; then
    python3 -m pip install -e ".[dev]" --quiet
    echo "       (includes dev dependencies: pytest, ruff, etc.)"
else
    python3 -m pip install -e . --quiet
fi

# --- Verify key imports ---
echo ""
echo "[4/4] Verifying installation ..."
python3 -c "
import fastapi, uvicorn, pydantic, httpx
import langchain, langchain_openai, langgraph
import chromadb
print('  Core packages  : OK')
" 2>&1 || { echo "  ERROR: Core package import failed"; exit 1; }

if $DEV; then
    python3 -c "
import pytest, ruff
print('  Dev packages   : OK')
" 2>&1 || echo "  WARNING: Some dev packages could not be imported"
fi

# --- .env hint ---
echo ""
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "NOTE: No .env file found. Create one with your OpenAI key:"
    echo ""
    echo "  echo 'OPENAI_API_KEY=sk-...' > $PROJECT_DIR/.env"
    echo ""
else
    echo ".env file found."
fi

echo "======================================"
echo "  Installation complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  ./scripts/run_backend.sh        # Start backend (merchant + agent API)"
echo "  ./scripts/run_frontend.sh       # Open frontend in browser"
echo "  ./scripts/test_backend.sh       # Run backend tests"
echo "  ./scripts/test_frontend.sh      # Run frontend smoke tests"
