#!/usr/bin/env bash
# Run script for Code Eval Workbench

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Detect mode: default is ui, pass "cli" for CLI mode
MODE="${1:-ui}"

if [[ "$MODE" == "ui" ]]; then
    echo "Launching Streamlit UI..."
    uv run streamlit run "$SCRIPT_DIR/app.py"
else
    shift
    echo "Running CLI evaluation..."
    uv run python "$SCRIPT_DIR/run_eval.py" "$@"
fi
