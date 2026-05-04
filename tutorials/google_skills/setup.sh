#!/usr/bin/env bash
# setup.sh — install dependencies for both demo apps into system Python.
# Safe to re-run. No venvs — Termux/Android blocks the lib64 symlink venvs need.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── prereq check ──────────────────────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
    echo "ERROR: uv is not installed."
    echo "Install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "uv $(uv --version)"
echo "python3 $(python3 --version)"
echo ""

# ── demo-gemini-cloudrun (Flask web API) ──────────────────────────────────────
# No pyproject.toml — install directly into the system Python.
# Venvs are skipped: Termux/Android filesystems block the lib64 symlink that
# Python's venv module creates on 64-bit systems.
echo "==> demo-gemini-cloudrun: installing dependencies (system Python)"
uv pip install --system -r "$REPO_ROOT/demo-gemini-cloudrun/requirements.txt"

echo ""

# ── demo-gemini-python (CLI demo) ─────────────────────────────────────────────
# Install deps explicitly into system Python (matches pyproject.toml dependencies).
echo "==> demo-gemini-python: installing dependencies (system Python)"
uv pip install --system \
    "google-genai>=0.8" \
    "pydantic>=2.0" \
    "python-dotenv>=1.0" \
    "pytest>=8.0"

echo ""
echo "Setup complete."
echo ""
echo "Usage:"
echo "  ./run.sh web                  # Start Flask web API (requires GOOGLE_API_KEY)"
echo "  ./run.sh cli text --prompt .. # Run CLI demo    (requires GEMINI_API_KEY in demo-gemini-python/.env)"
echo "  ./run.sh test                 # Run all tests (no credentials needed)"
echo ""
echo "Both demos use system python3 directly (no venvs — Termux compatibility)."
