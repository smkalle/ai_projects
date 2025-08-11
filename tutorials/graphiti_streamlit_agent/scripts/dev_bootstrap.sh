#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

cd "$ROOT"

echo "[1/4] Starting Neo4j via docker-compose..."
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Please install Docker." >&2
  exit 1
fi

docker compose up -d neo4j

echo "[2/4] Creating Python venv..."
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

echo "[3/4] Installing requirements..."
pip install -r graphiti_streamlit_agent/requirements.txt

echo "[4/4] Launching Streamlit app..."
export NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
export NEO4J_USER="${NEO4J_USER:-neo4j}"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-please_change_me}"

if [ -f .env ]; then
  set -a; source .env; set +a
fi

exec streamlit run graphiti_streamlit_agent/app.py

