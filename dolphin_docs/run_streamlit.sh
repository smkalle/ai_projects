#!/bin/bash

echo "🐬 Starting Dolphin Medical Document Parser..."

# Activate virtual environment
source dolphin_venv/bin/activate

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Streamlit app
echo "🚀 Launching Streamlit app..."
echo "📱 Open your browser to: http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop the server"

streamlit run dolphin_app_minimal.py --server.port 8501 --server.address 0.0.0.0