#!/usr/bin/env bash
# Setup script for Code Eval Workbench

set -e

echo "Installing Python dependencies..."
UV_LINK_MODE=copy uv sync

echo ""
if [[ -f .env ]]; then
    echo "✓ .env already exists"
else
    if [[ -f .env.example ]]; then
        cp .env.example .env
        echo "✓ Created .env from .env.example"
        echo "  → Edit .env and add your ANTHROPIC_API_KEY"
    else
        echo "✓ No .env or .env.example found — skipping env setup"
    fi
fi

echo ""
echo "Setup complete. Run './run.sh' to launch."
