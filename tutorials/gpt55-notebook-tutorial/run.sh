#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME="gpt55-agent-framework"
VENV_DIR="${UV_PROJECT_ENVIRONMENT:-$HOME/.venvs/$ENV_NAME}"

# Default: run all demos
DEMO="${1:-all}"
EXPORT_JSON=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --demo)
      DEMO="$2"
      shift 2
      ;;
    --export-json)
      EXPORT_JSON="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [--demo all|improvements|architecture|eval|agent|workflows] [--export-json PATH]"
      echo ""
      echo "Demos:"
      echo "  all          - Run all demonstrations (default)"
      echo "  improvements - Show GPT-5.5 improvements table"
      echo "  architecture - Show architecture backlog"
      echo "  eval         - Show evaluation checklist"
      echo "  agent        - Run agent control system demo"
      echo "  workflows    - Show workflow evaluation examples"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

echo "=== GPT-5.5 Agent Framework ==="
echo "Demo: $DEMO"
echo ""

# Ensure venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found. Run setup.sh first."
    exit 1
fi

cd "$PROJECT_DIR"

# Use venv Python directly (simplest approach)
PYTHON="$VENV_DIR/bin/python"

if [ -n "$EXPORT_JSON" ]; then
  echo "Exporting to: $EXPORT_JSON"
  "$PYTHON" gpt55_agent_framework.py --export-json "$EXPORT_JSON"
else
  "$PYTHON" gpt55_agent_framework.py --demo "$DEMO"
fi