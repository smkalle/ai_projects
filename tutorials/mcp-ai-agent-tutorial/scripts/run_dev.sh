#!/bin/bash
# Development runner script

echo "🚀 Starting MCP AI Agent in development mode..."

# Start API in background
echo "Starting FastAPI server..."
python src/api/main.py &
API_PID=$!

# Wait for API to start
sleep 3

# Start Streamlit
echo "Starting Streamlit UI..."
streamlit run src/ui/streamlit_app.py

# Cleanup on exit
trap "kill $API_PID" EXIT
