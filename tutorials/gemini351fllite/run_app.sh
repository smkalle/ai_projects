#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    echo "Run ./setup.sh first" && exit 1
fi

.venv/bin/streamlit run gemini_explorer/app.py "$@"
