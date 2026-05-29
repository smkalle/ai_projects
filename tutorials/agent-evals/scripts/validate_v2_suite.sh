#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="$ROOT_DIR/artifacts"
REPORT_PATH="$REPORT_DIR/v2-suite-signoff.md"
API_LOG="$REPORT_DIR/v2-api.log"
FRONTEND_LOG="$REPORT_DIR/v2-frontend.log"
mkdir -p "$REPORT_DIR"

commands=(
  "python3 -m compileall app.py agent_eval"
  "python3 -m pytest tests"
  "npm --prefix frontend run build"
)

names=(
  "Python compile"
  "API workflow tests"
  "Frontend production build"
)

statuses=()
outputs=()
overall=0

cd "$ROOT_DIR" || exit 1

api_pid=""
frontend_pid=""

cleanup() {
  if [ -n "$frontend_pid" ] && kill -0 "$frontend_pid" 2>/dev/null; then
    kill "$frontend_pid" 2>/dev/null || true
  fi
  if [ -n "$api_pid" ] && kill -0 "$api_pid" 2>/dev/null; then
    kill "$api_pid" 2>/dev/null || true
  fi
}

wait_for_url() {
  url="$1"
  name="$2"
  attempts=60
  while [ "$attempts" -gt 0 ]; do
    if python3 - "$url" <<'PY' >/dev/null 2>&1
from sys import argv
from urllib.request import urlopen

with urlopen(argv[1], timeout=1) as response:
    raise SystemExit(0 if response.status < 500 else 1)
PY
    then
      return 0
    fi
    attempts=$((attempts - 1))
    sleep 0.5
  done
  echo "$name did not become ready at $url"
  return 1
}

trap cleanup EXIT

for idx in "${!commands[@]}"; do
  cmd="${commands[$idx]}"
  output_file="$REPORT_DIR/validate-step-$idx.log"
  echo "==> ${names[$idx]}: $cmd"
  if bash -lc "$cmd" >"$output_file" 2>&1; then
    statuses+=("PASS")
  else
    statuses+=("FAIL")
    overall=1
  fi
  outputs+=("$output_file")
  cat "$output_file"
done

ui_output_file="$REPORT_DIR/validate-step-${#commands[@]}.log"
echo "==> Playwright UI workflow tests: npm --prefix frontend run test:e2e"
{
  echo "Starting API on http://127.0.0.1:8000"
  python3 -m uvicorn agent_eval.api:app --host 127.0.0.1 --port 8000 >"$API_LOG" 2>&1 &
  api_pid="$!"
  wait_for_url "http://127.0.0.1:8000/api/health" "API" || exit 1

  echo "Starting Vite on http://127.0.0.1:5173"
  npm --prefix frontend run dev >"$FRONTEND_LOG" 2>&1 &
  frontend_pid="$!"
  wait_for_url "http://127.0.0.1:5173" "Vite frontend" || exit 1

  npm --prefix frontend run test:e2e
} >"$ui_output_file" 2>&1
if [ "$?" -eq 0 ]; then
  statuses+=("PASS")
else
  statuses+=("FAIL")
  overall=1
fi
names+=("Playwright UI workflow tests")
commands+=("npm --prefix frontend run test:e2e")
outputs+=("$ui_output_file")
cat "$ui_output_file"

{
  echo "# V2 API and UI Automation Signoff"
  echo
  echo "- Generated at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "- Overall status: $([ "$overall" -eq 0 ] && echo PASS || echo FAIL)"
  echo
  echo "## Workflow Coverage"
  echo
  echo "- API health and metadata"
  echo "- Single eval run, run detail, case evidence, and technical report"
  echo "- Multi-model x multi-scenario batch matrix"
  echo "- VC/readiness aggregation"
  echo "- Analytics rollups by model and scenario"
  echo "- Audit trail events"
  echo "- Interactive support endpoint and tool evidence"
  echo "- SaaS admin shell, analytics, observability, batch, audit, evidence, and support UI"
  echo
  echo "## Command Results"
  echo
  for idx in "${!commands[@]}"; do
    echo "### ${names[$idx]}: ${statuses[$idx]}"
    echo
    echo '```text'
    tail -n 80 "${outputs[$idx]}"
    echo '```'
    echo
  done
} >"$REPORT_PATH"

echo "Signoff report: $REPORT_PATH"
exit "$overall"
