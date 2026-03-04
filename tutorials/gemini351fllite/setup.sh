#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== Gemini 3.1 Flash-Lite Explorer Setup ==="

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Using uv: $(uv --version)"

# Create venv and install deps
# Note: uses python3 -m venv (includes pip) + uv pip for fast installs
echo "Installing dependencies..."
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
uv pip install --python .venv/bin/python -r requirements.txt 2>/dev/null \
    || .venv/bin/pip install -q -r requirements.txt

# Create .env if missing
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "Created .env file. Please set your GEMINI_API_KEY:"
    echo "  Edit .env and replace 'your-api-key-here' with your actual key"
    echo "  Get one at: https://aistudio.google.com/apikey"
else
    echo ".env already exists"
fi

echo ""
echo "Setup complete! Run:"
echo "  ./run_cli.sh chat        # Interactive chat"
echo "  ./run_cli.sh --help      # See all CLI commands"
echo "  ./run_app.sh             # Launch Streamlit app"
