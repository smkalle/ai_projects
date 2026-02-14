#!/usr/bin/env bash
# =============================================================================
# run_backend.sh — Start the AI Commerce Agent backend
#
# This starts the Agent API (FastAPI on port 8000) which automatically spawns
# the UCP Merchant Server (port 8182) as a subprocess.
#
# The web UI is served at http://localhost:8000
#
# Usage:
#   ./scripts/run_backend.sh                    # Default (port 8000)
#   ./scripts/run_backend.sh --port 9000        # Custom port
#   ./scripts/run_backend.sh --reload           # Auto-reload on code changes
#   ./scripts/run_backend.sh --merchant-only    # Start only the merchant server
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

PORT=8000
HOST="0.0.0.0"
RELOAD=""
MERCHANT_ONLY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --port)
            PORT="$2"; shift 2 ;;
        --host)
            HOST="$2"; shift 2 ;;
        --reload)
            RELOAD="--reload"; shift ;;
        --merchant-only)
            MERCHANT_ONLY=true; shift ;;
        -h|--help)
            echo "Usage: $0 [--port PORT] [--host HOST] [--reload] [--merchant-only]"
            echo ""
            echo "Options:"
            echo "  --port PORT        Agent API port (default: 8000)"
            echo "  --host HOST        Bind host (default: 0.0.0.0)"
            echo "  --reload           Auto-reload on file changes"
            echo "  --merchant-only    Start only the UCP merchant server (port 8182)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"; exit 1 ;;
    esac
done

cd "$PROJECT_DIR"

# Activate venv if it exists
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$PROJECT_DIR/.venv/bin/activate"
fi

# Load .env if present
if [ -f "$PROJECT_DIR/.env" ]; then
    echo "Loading .env file..."
    set -a
    # shellcheck disable=SC1091
    source "$PROJECT_DIR/.env"
    set +a
fi

# --- Merchant-only mode ---
if $MERCHANT_ONLY; then
    echo "======================================"
    echo "  UCP Merchant Server (standalone)"
    echo "======================================"
    echo ""
    echo "  URL  : http://${HOST}:8182"
    echo "  UCP  : http://${HOST}:8182/.well-known/ucp"
    echo "  Docs : http://${HOST}:8182/docs"
    echo ""
    exec python3 -m uvicorn \
        "merchant_server.startup:create_merchant_app" \
        --factory \
        --host "$HOST" \
        --port 8182 \
        $RELOAD
fi

# --- Full Agent API (includes merchant as subprocess) ---
echo "======================================"
echo "  AI Commerce Agent — Backend"
echo "======================================"
echo ""
echo "  Agent API  : http://${HOST}:${PORT}"
echo "  Web UI     : http://${HOST}:${PORT}/"
echo "  API Docs   : http://${HOST}:${PORT}/docs"
echo "  Merchant   : http://localhost:8182 (auto-started)"
echo ""

if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "  WARNING: OPENAI_API_KEY not set."
    echo "  The agent will use keyword search fallback instead of embeddings."
    echo "  Chat/intent features require an OpenAI API key."
    echo ""
fi

echo "Starting server..."
echo ""

exec python3 -m uvicorn \
    "agent_api:app" \
    --host "$HOST" \
    --port "$PORT" \
    $RELOAD
