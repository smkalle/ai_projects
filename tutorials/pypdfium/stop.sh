#!/bin/bash

# Energy Document AI - Stop Script
# Kills all running processes for clean restart

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Energy Document AI - Stop Script     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}\n"

# Function to print status
print_status() {
    echo -e "${YELLOW}▶ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_status "Stopping Energy Document AI processes..."

# Kill processes on ports 8501 and 8000
for port in 8501 8000; do
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        print_status "Killing process on port $port (PID: $pid)"
        # Try graceful shutdown first
        kill -TERM $pid 2>/dev/null || true
        sleep 3
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            print_status "Force killing stubborn process on port $port"
            kill -9 $pid 2>/dev/null || true
        fi
        print_success "Process on port $port stopped"
    else
        print_success "No process found on port $port"
    fi
done

# Kill any python processes running our app
if pkill -f "app/main.py" 2>/dev/null; then
    print_success "Killed app/main.py processes"
fi

if pkill -f "streamlit.*streamlit_app.py" 2>/dev/null; then
    print_success "Killed Streamlit processes"
fi

# Wait a moment for processes to terminate
sleep 2

echo -e "\n${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}All Energy Document AI processes stopped${NC}"
echo -e "${GREEN}Run ./start.sh to restart the application${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}\n"