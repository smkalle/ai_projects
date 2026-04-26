#!/bin/bash
set -e

# Project paths
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME="gpt55-agent-framework"
VENV_DIR="${UV_PROJECT_ENVIRONMENT:-$HOME/.venvs/$ENV_NAME}"

echo "=== GPT-5.5 Agent Framework Setup ==="
echo "Project: $PROJECT_DIR"
echo "Venv: $VENV_DIR"

# Create virtual environment if needed
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    uv venv "$VENV_DIR"
fi

# Verify installation
echo "Verifying installation..."
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Error: Virtual environment not created properly"
    exit 1
fi

"$VENV_DIR/bin/python" -c "import gpt55_agent_framework; print('✓ Framework imported successfully')"

echo ""
echo "=== Setup Complete ==="
echo "Run './run.sh' to execute the application"