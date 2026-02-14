#!/usr/bin/env bash
# =============================================================================
# run_frontend.sh — Open the AI Commerce Agent web UI
#
# The frontend is served by the backend (FastAPI serves static files), so
# the backend must be running first. This script verifies that and opens
# the browser, or starts the backend if --start-backend is passed.
#
# Usage:
#   ./scripts/run_frontend.sh                   # Check backend & open browser
#   ./scripts/run_frontend.sh --start-backend   # Start backend, then open UI
#   ./scripts/run_frontend.sh --port 9000       # Custom backend port
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

PORT=8000
HOST="localhost"
START_BACKEND=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --port)
            PORT="$2"; shift 2 ;;
        --host)
            HOST="$2"; shift 2 ;;
        --start-backend)
            START_BACKEND=true; shift ;;
        -h|--help)
            echo "Usage: $0 [--port PORT] [--host HOST] [--start-backend]"
            echo ""
            echo "Options:"
            echo "  --port PORT         Backend port (default: 8000)"
            echo "  --host HOST         Backend host (default: localhost)"
            echo "  --start-backend     Start the backend server first"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"; exit 1 ;;
    esac
done

BASE_URL="http://${HOST}:${PORT}"

# --- Optionally start backend ---
if $START_BACKEND; then
    echo "Starting backend in background..."
    "$SCRIPT_DIR/run_backend.sh" --port "$PORT" &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"

    # Wait for backend to be ready
    echo "Waiting for backend at $BASE_URL ..."
    MAX_WAIT=30
    for i in $(seq 1 $MAX_WAIT); do
        if curl -sf "$BASE_URL/api/products" > /dev/null 2>&1; then
            echo "Backend is ready!"
            break
        fi
        if [ "$i" -eq "$MAX_WAIT" ]; then
            echo "ERROR: Backend did not start within ${MAX_WAIT}s"
            echo "Check logs above for errors."
            exit 1
        fi
        sleep 1
    done
    echo ""
fi

# --- Check if backend is running ---
echo "Checking backend at $BASE_URL ..."
if ! curl -sf "$BASE_URL/api/products" > /dev/null 2>&1; then
    echo ""
    echo "ERROR: Backend is not running at $BASE_URL"
    echo ""
    echo "Start it first:"
    echo "  ./scripts/run_backend.sh"
    echo ""
    echo "Or start backend and frontend together:"
    echo "  ./scripts/run_frontend.sh --start-backend"
    exit 1
fi

echo "Backend is running."
echo ""

# --- Open browser ---
URL="$BASE_URL"
echo "======================================"
echo "  AI Commerce Agent — Frontend"
echo "======================================"
echo ""
echo "  URL: $URL"
echo ""

# Try to open browser (works on macOS, Linux with xdg-open, or WSL)
if command -v xdg-open &> /dev/null; then
    xdg-open "$URL" 2>/dev/null &
elif command -v open &> /dev/null; then
    open "$URL" 2>/dev/null &
elif command -v wslview &> /dev/null; then
    wslview "$URL" 2>/dev/null &
else
    echo "  Could not detect a browser opener."
    echo "  Open the URL above in your browser manually."
fi

echo "  Frontend is served by the backend at $URL"
echo "  Press Ctrl+C to stop (if --start-backend was used)"
echo ""

# If we started the backend, wait for it
if $START_BACKEND; then
    wait $BACKEND_PID
fi
