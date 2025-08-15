#!/usr/bin/env bash
# Manage a local Tavily-based MCP search server (no Docker).
# Usage:
#   ./scripts/run_search_server.sh start|stop|status
# Env vars:
#   TAVILY_API_KEY   (required)
#   SEARCH_PORT      (default: 8765)
#   SEARCH_SERVER_URL (optional; if set, port is derived unless SEARCH_PORT set)

set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

CMD=${1:-start}

# Load env
if [ -f .env ]; then
  set -a; # export all vars
  # shellcheck disable=SC1091
  source .env
  set +a
fi

derive_port_from_url() {
  url="$1"
  # Extract :port if present, else default 80/443; we'll fallback to default 8765 later
  # Example matches: http://host:1234, https://host:1234
  echo "$url" | sed -n 's#^[a-zA-Z]\+://[^:/]\+\(:\([0-9]\+\)\).*$#\2#p'
}

DEFAULT_PORT=8765
URL_PORT=""
if [ -n "${SEARCH_SERVER_URL:-}" ]; then
  URL_PORT=$(derive_port_from_url "$SEARCH_SERVER_URL" || true)
fi
SEARCH_PORT=${SEARCH_PORT:-${URL_PORT:-$DEFAULT_PORT}}

LOG_DIR=.logs
PID_FILE=$LOG_DIR/search.pid
LOG_FILE=$LOG_DIR/search.log
mkdir -p "$LOG_DIR"

status() {
  if [ -f "$PID_FILE" ] && ps -p "$(cat "$PID_FILE")" >/dev/null 2>&1; then
    echo "Search server running (PID $(cat "$PID_FILE")) on port $SEARCH_PORT"
    return 0
  fi
  # Fallback check by port
  if command -v ss >/dev/null 2>&1 && ss -ltn 2>/dev/null | grep -q ":$SEARCH_PORT"; then
    echo "Search server listening on port $SEARCH_PORT (PID unknown)"
    return 0
  fi
  echo "Search server not running"
  return 1
}

start() {
  if ! command -v npx >/dev/null 2>&1; then
    echo "npx is required. Please install Node.js (includes npx)." >&2
    exit 1
  fi
  if [ -z "${TAVILY_API_KEY:-}" ]; then
    echo "TAVILY_API_KEY is required to start the Tavily search server." >&2
    exit 1
  fi
  if status >/dev/null 2>&1; then
    status; exit 0
  fi
  echo "Starting Tavily MCP search server on port $SEARCH_PORT..."
  nohup npx -y mcp-server-tavily --apiKey "$TAVILY_API_KEY" --port "$SEARCH_PORT" > "$LOG_FILE" 2>&1 & echo $! > "$PID_FILE"
  sleep 1
  status || (echo "Failed to start search server; see $LOG_FILE" >&2; exit 1)
}

stop() {
  if [ -f "$PID_FILE" ]; then
    kill "$(cat "$PID_FILE")" 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "Stopped search server"
    return 0
  fi
  echo "No PID file; nothing to stop"
}

case "$CMD" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  *) echo "Usage: $0 {start|stop|status}" >&2; exit 1 ;;
esac

