#!/usr/bin/env bash
set -euo pipefail

echo "🧬 Setting up Rare Disease Drug Repurposing AI with uv"
echo "======================================================"

if ! command -v uv >/dev/null 2>&1; then
  echo "❌ 'uv' is not installed. Install it first:"
  echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

echo "📦 Syncing dependencies (including dev tools)..."
uv sync --dev

if [ ! -f .env ]; then
  echo "🔐 Creating .env from .env.example"
  cp .env.example .env
fi

echo
echo "✅ uv environment ready. Useful commands:"
echo "   uv run python scripts/run_backend.py"
echo "   uv run python scripts/run_frontend.py"
echo "   uv run pytest -q"
echo
echo "💡 Hint: 'uv sync' creates and manages .venv automatically."

