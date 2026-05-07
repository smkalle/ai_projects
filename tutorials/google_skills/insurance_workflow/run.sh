#!/usr/bin/env bash
set -euo pipefail

# Debug runner for Iteration 1 insurance claims workflow
# Usage: ./run.sh [backend|frontend|both]
#   backend  — uvicorn with reload + trace logging on :8897
#   frontend — Vite dev server on :5177
#   both     — start both in parallel (default)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}"

cd "${SCRIPT_DIR}"

mode="${1:-both}"

start_backend() {
  echo "[run.sh] Starting backend on http://localhost:8897 (DEBUG + reload)"
  # Set DEBUG=1 so the backend returns full trace logs
  export DEBUG=1
  export PYTHONUNBUFFERED=1
  uvicorn backend.server:app \
    --host 0.0.0.0 \
    --port 8897 \
    --reload \
    --log-level debug \
    --access-log
}

start_frontend() {
  echo "[run.sh] Starting frontend on http://localhost:5177"
  cd "${SCRIPT_DIR}/frontend"
  npm install
  npm run dev -- --port 5177
}

if [[ "$mode" == "backend" ]]; then
  start_backend
elif [[ "$mode" == "frontend" ]]; then
  start_frontend
elif [[ "$mode" == "both" ]]; then
  start_backend &
  BACKEND_PID=$!
  sleep 2
  start_frontend &
  FRONTEND_PID=$!
  echo "[run.sh] Backend PID=$BACKEND_PID  Frontend PID=$FRONTEND_PID"
  echo "[run.sh] Press Ctrl+C to stop both"
  wait $BACKEND_PID $FRONTEND_PID
else
  echo "Usage: $0 [backend|frontend|both]"
  exit 1
fi
