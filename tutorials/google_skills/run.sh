#!/usr/bin/env bash
# run.sh — run, test, or deploy either demo app using uv only.
# Run ./setup.sh first.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOUDRUN_DIR="$REPO_ROOT/demo-gemini-cloudrun"
PYTHON_DIR="$REPO_ROOT/demo-gemini-python"

# demo-gemini-cloudrun uses system Python (no venv — Termux lib64 symlink issue)
# demo-gemini-python uses uv-managed venv via `uv sync` / `uv run`

usage() {
    cat <<EOF
Usage: ./run.sh <target> [args...]

Targets:
  web                  Start Flask web API at http://localhost:8080
                       Requires: GOOGLE_API_KEY (or Vertex AI env vars)

  cli <cmd> [opts]     Run the Gemini CLI demo
                       Commands: text chat stream json tools code embed thinking safety grounding all
                       Options:  --prompt "..." --model gemini-3-flash-preview
                       Requires: GEMINI_API_KEY in demo-gemini-python/.env (or Vertex AI env vars)

  test-web             Run demo-gemini-cloudrun tests (no credentials needed)
  test-voice-live      Run live voice server tests (requires GOOGLE_API_KEY)
  test-cli             Run demo-gemini-python tests (no credentials needed)
  test                 Run all tests

Examples:
  ./run.sh web
  ./run.sh cli text --prompt "Hello"
  ./run.sh cli all
  ./run.sh test
  ./run.sh test-web
  ./run.sh test-voice-live
EOF
}

# ── prereq check ──────────────────────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
    echo "ERROR: uv is not installed. Run setup.sh first."
    exit 1
fi

# ── targets ───────────────────────────────────────────────────────────────────
case "${1:-}" in

  web)
    echo "Starting Flask web API at http://localhost:8080  (Ctrl-C to stop)"
    (cd "$CLOUDRUN_DIR" && python3 app.py)
    ;;

  cli)
    shift
    if [[ $# -eq 0 ]]; then
        echo "ERROR: cli requires a command. Run ./run.sh --help for options."
        exit 1
    fi
    # Must run from demo-gemini-python/ — demos.* is a relative package.
    (cd "$PYTHON_DIR" && python3 main.py "$@")
    ;;

  test-web)
    echo "==> Testing demo-gemini-cloudrun"
    (cd "$CLOUDRUN_DIR" && python3 -m pytest test_app.py -v)
    ;;

  test-cli)
    echo "==> Testing demo-gemini-python"
    (cd "$PYTHON_DIR" && python3 -m pytest tests/test_demos.py -v)
    ;;

  test-voice-live)
    echo "==> Testing demo-gemini-cloudrun live voice server"
    (cd "$CLOUDRUN_DIR" && python3 -m pytest test_voice_server.py -v)
    ;;

  test)
    "$0" test-web
    echo ""
    "$0" test-cli
    ;;

  --help|-h|help)
    usage
    ;;

  *)
    usage
    exit 1
    ;;

esac
