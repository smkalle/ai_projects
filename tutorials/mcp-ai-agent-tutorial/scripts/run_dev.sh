#!/bin/bash
# Development runner script

echo "🚀 Starting MCP AI Agent in development mode..."

# Export variables from .env if present
if [ -f .env ]; then
  echo "Loading environment from .env"
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

# Default API_BASE_URL if not provided
if [ -z "${API_BASE_URL:-}" ]; then
  export API_BASE_URL="http://localhost:${API_PORT:-8000}"
fi

# Optionally prep and start local search server (Tavily) if requested
SEARCH_STARTED=0
if [ "${START_SEARCH_SERVER:-false}" = "true" ] || [ "${START_SEARCH_SERVER:-0}" = "1" ]; then
  echo "Preparing MCP tools (run_tools.sh)..."
  ./scripts/run_tools.sh || true
  echo "Starting local search server (Tavily)..."
  ./scripts/run_search_server.sh start || true
  SEARCH_STARTED=1
fi

# Start API in background (ensure src is on PYTHONPATH)
echo "Starting FastAPI server..."
env PYTHONPATH=src uvicorn api.main:app --reload --port "${API_PORT:-8000}" &
API_PID=$!

# Wait for API to start
sleep 3

# Start Streamlit
echo "Starting Streamlit UI..."
streamlit run src/ui/streamlit_app.py --server.port "${UI_PORT:-8501}"

# Cleanup on exit
cleanup() {
  kill $API_PID 2>/dev/null || true
  if [ "$SEARCH_STARTED" = "1" ]; then
    ./scripts/run_search_server.sh stop || true
  fi
}
trap cleanup EXIT
