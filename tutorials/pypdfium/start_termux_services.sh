#!/bin/bash

# Termux Services Startup Script
# Starts Qdrant and Streamlit in background for Android/Termux

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Termux Background Services Start     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}\n"

# Function to print status
print_status() {
    echo -e "${YELLOW}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ Error: $1${NC}"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Run setup first."
    echo "python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Kill existing processes
print_status "Stopping any existing services..."
pkill -f qdrant 2>/dev/null || true
pkill -f streamlit 2>/dev/null || true
pkill -f uvicorn 2>/dev/null || true
sleep 2

# Create logs directory
mkdir -p logs

# Start Qdrant in background
print_status "Starting Qdrant vector database..."
if [ -f "start_qdrant_termux.sh" ]; then
    nohup ./start_qdrant_termux.sh > logs/qdrant.log 2>&1 &
    QDRANT_PID=$!
    sleep 3
    
    # Check if Qdrant started successfully
    if kill -0 $QDRANT_PID 2>/dev/null; then
        print_success "Qdrant started (PID: $QDRANT_PID)"
    else
        print_error "Failed to start Qdrant"
        exit 1
    fi
else
    print_error "start_qdrant_termux.sh not found"
    exit 1
fi

# Wait for Qdrant to be ready
print_status "Waiting for Qdrant to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        print_success "Qdrant is ready"
        break
    fi
    sleep 1
done

if ! curl -s http://localhost:6333/health > /dev/null 2>&1; then
    print_error "Qdrant health check failed"
    exit 1
fi

# Activate virtual environment and start Streamlit
print_status "Starting Streamlit UI..."
source venv/bin/activate
nohup python app/main.py --mode ui > logs/streamlit.log 2>&1 &
STREAMLIT_PID=$!
sleep 3

# Check if Streamlit started successfully  
if kill -0 $STREAMLIT_PID 2>/dev/null; then
    print_success "Streamlit started (PID: $STREAMLIT_PID)"
else
    print_error "Failed to start Streamlit"
    exit 1
fi

# Wait for Streamlit to be ready
print_status "Waiting for Streamlit to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        print_success "Streamlit is ready"
        break
    fi
    sleep 1
done

# Summary
echo -e "\n${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}All services started successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}📊 Streamlit UI:    http://localhost:8501${NC}"
echo -e "${GREEN}🔍 Qdrant API:     http://localhost:6333${NC}"
echo -e "${GREEN}📋 Qdrant Dashboard: http://localhost:6333/dashboard${NC}"
echo -e "\n${YELLOW}Service Status:${NC}"
echo -e "${YELLOW}  Qdrant PID:      $QDRANT_PID${NC}"
echo -e "${YELLOW}  Streamlit PID:   $STREAMLIT_PID${NC}"
echo -e "\n${YELLOW}Logs:${NC}"
echo -e "${YELLOW}  Qdrant:    tail -f logs/qdrant.log${NC}"
echo -e "${YELLOW}  Streamlit: tail -f logs/streamlit.log${NC}"
echo -e "\n${YELLOW}Stop services:${NC}"
echo -e "${YELLOW}  ./stop.sh  or  pkill -f 'qdrant|streamlit'${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}\n"

# Optional: Keep script running to monitor services
if [ "$1" = "--monitor" ]; then
    echo -e "${YELLOW}Monitoring services... Press Ctrl+C to stop monitoring (services will continue)${NC}\n"
    
    while true; do
        sleep 10
        
        # Check if services are still running
        if ! kill -0 $QDRANT_PID 2>/dev/null; then
            print_error "Qdrant process died (PID: $QDRANT_PID)"
            break
        fi
        
        if ! kill -0 $STREAMLIT_PID 2>/dev/null; then
            print_error "Streamlit process died (PID: $STREAMLIT_PID)"
            break
        fi
        
        echo -e "${GREEN}Services running OK ($(date))${NC}"
    done
fi