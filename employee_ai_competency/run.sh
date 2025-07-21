#!/bin/bash

# AI Competency Assessment Survey - Launch Script
# This script starts the web server and opens the browser

PORT=8000
HOST="localhost"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AI Competency Assessment Survey${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 is required but not installed.${NC}"
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port $PORT is already in use.${NC}"
    echo "Stopping existing server..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

# Start the Python HTTP server
echo -e "${GREEN}✓ Starting web server on port $PORT...${NC}"
python3 -m http.server $PORT > server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > server.pid

# Wait for server to start
sleep 2

# Check if server started successfully
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Failed to start server. Check server.log for details.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Server started successfully (PID: $SERVER_PID)${NC}"
echo ""
echo -e "${BLUE}📊 Access the survey at:${NC}"
echo -e "   ${GREEN}http://$HOST:$PORT${NC}"
echo ""

# Try to open in default browser based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://$HOST:$PORT" 2>/dev/null
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://$HOST:$PORT" 2>/dev/null
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start "http://$HOST:$PORT" 2>/dev/null
fi

echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping server...${NC}"
    kill $SERVER_PID 2>/dev/null
    rm -f server.pid
    echo -e "${GREEN}✓ Server stopped${NC}"
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup INT

# Keep script running
wait $SERVER_PID