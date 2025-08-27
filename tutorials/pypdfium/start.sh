#!/bin/bash

# Energy Document AI - Quick Start Script
# Automates setup and launch of the application

# Exit on unset variables but allow command failures
set -u

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    Energy Document AI - Quick Start      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}\n"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    echo -e "${YELLOW}▶ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ Error: $1${NC}"
    exit 1
}

# Function to kill existing processes
kill_existing_processes() {
    print_status "Checking for existing processes..."
    
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
        fi
    done
    
    # Kill any python processes running our app
    pkill -f "app/main.py" 2>/dev/null || true
    pkill -f "streamlit.*streamlit_app.py" 2>/dev/null || true
    
    # Wait a moment for processes to terminate
    sleep 2
    print_success "Existing processes cleaned up"
}

# Graceful shutdown handler
cleanup() {
    echo -e "\n${YELLOW}Received interrupt signal. Shutting down gracefully...${NC}"
    kill_existing_processes
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check Python
print_status "Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Set Python executable path
PYTHON_EXE="venv/bin/python"
PIP_EXE="venv/bin/pip"

# Activate virtual environment for current session
print_status "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    print_success "Virtual environment activated"
else
    print_error "Virtual environment activation failed"
fi

# Upgrade pip
print_status "Upgrading pip..."
$PIP_EXE install --upgrade pip --quiet
print_success "pip upgraded"

# Check if core dependencies are already installed
print_status "Checking dependencies..."
if $PYTHON_EXE -c "import streamlit, fastapi, openai, langchain, qdrant_client, pypdfium2" 2>/dev/null; then
    print_success "Core dependencies already installed"
else
    print_status "Installing dependencies (this may take a few minutes)..."
    if $PIP_EXE install -r requirements.txt --quiet 2>/dev/null; then
        print_success "All dependencies installed"
    else
        echo -e "${YELLOW}⚠️  Some dependencies had conflicts. Trying alternative installation...${NC}"
        # Try installing core dependencies first
        if $PIP_EXE install fastapi streamlit openai langchain qdrant-client pypdfium2 plotly --quiet 2>/dev/null; then
            print_success "Core dependencies installed successfully"
        else
            echo -e "${YELLOW}⚠️  Dependency installation had issues. The app may still work with existing packages.${NC}"
        fi
    fi
fi

# Check for .env file
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_success ".env file created"
    echo -e "${YELLOW}⚠️  Please edit .env and add your OpenAI API key${NC}"
else
    print_success ".env file already exists"
fi

# Clean up any existing processes
kill_existing_processes

# Check if Docker is available
print_status "Checking for Docker..."
if command_exists docker; then
    print_success "Docker found"
    
    # Check if Qdrant is running
    if docker ps | grep -q qdrant 2>/dev/null; then
        print_success "Qdrant is already running"
    else
        echo -e "${YELLOW}Would you like to start Qdrant vector database? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_status "Starting Qdrant..."
            if docker run -d -p 6333:6333 -v ./qdrant_data:/qdrant/storage --name qdrant qdrant/qdrant 2>/dev/null; then
                print_success "Qdrant started on port 6333"
            else
                echo -e "${YELLOW}⚠️  Failed to start Qdrant. It may already be running or Docker has issues.${NC}"
            fi
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Docker not found. Qdrant vector database will not be available${NC}"
    echo -e "${YELLOW}   Install Docker to enable full functionality${NC}"
fi

# Application launch menu
echo -e "\n${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}Select launch mode:${NC}"
echo -e "  1) Streamlit UI only (recommended)"
echo -e "  2) FastAPI server only"
echo -e "  3) Both UI and API"
echo -e "  4) Generate sample PDFs"
echo -e "  5) Start Qdrant Database"
echo -e "  6) Run verification test"
echo -e "  7) Restart (kill existing processes)"
echo -e "  8) Exit"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -n "Enter choice [1-8]: "
read -r choice

case $choice in
    1)
        print_status "Starting Streamlit UI..."
        echo -e "${GREEN}═══════════════════════════════════════════${NC}"
        echo -e "${GREEN}Access the application at: http://localhost:8501${NC}"
        echo -e "${GREEN}Press Ctrl+C to stop${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════${NC}\n"
        $PYTHON_EXE app/main.py --mode ui
        ;;
    2)
        print_status "Starting FastAPI server..."
        echo -e "${GREEN}═══════════════════════════════════════════${NC}"
        echo -e "${GREEN}API documentation at: http://localhost:8000/docs${NC}"
        echo -e "${GREEN}Press Ctrl+C to stop${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════${NC}\n"
        $PYTHON_EXE app/main.py --mode api
        ;;
    3)
        print_status "Starting both UI and API..."
        echo -e "${GREEN}═══════════════════════════════════════════${NC}"
        echo -e "${GREEN}Streamlit UI at: http://localhost:8501${NC}"
        echo -e "${GREEN}API documentation at: http://localhost:8000/docs${NC}"
        echo -e "${GREEN}Press Ctrl+C to stop${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════${NC}\n"
        $PYTHON_EXE app/main.py --mode both
        ;;
    4)
        print_status "Generating sample PDFs..."
        $PYTHON_EXE scripts/generate_sample_pdfs.py --all
        echo -e "${GREEN}Sample PDFs generated successfully!${NC}"
        echo -e "${YELLOW}You can now test the system with these documents${NC}"
        echo -e "${YELLOW}Run the script again to start the application${NC}"
        ;;
    5)
        print_status "Starting Qdrant Database..."
        if [ -n "$TERMUX_VERSION" ] || [ -d "$PREFIX" ]; then
            print_status "Detected Termux environment, using native Qdrant..."
            ./start_qdrant_termux.sh
        else
            print_status "Using Docker Qdrant..."
            ./start_qdrant.sh
        fi
        echo -e "${YELLOW}Run the script again to start the application${NC}"
        ;;
    6)
        print_status "Running verification test..."
        if [ -f "verify_setup.py" ]; then
            $PYTHON_EXE verify_setup.py
        else
            echo -e "${YELLOW}Creating verification script...${NC}"
            $PYTHON_EXE -c "
import sys
sys.path.append('app')
try:
    from models.pdf_processor import EnergyPDFProcessor
    from models.rag_system import EnergyRAGSystem  
    from models.agent_workflow import EnergyDocumentAgent
    print('✅ All core modules load successfully')
except Exception as e:
    print(f'❌ Error: {e}')
"
        fi
        ;;
    7)
        print_status "Restarting - killing all existing processes..."
        kill_existing_processes
        print_success "All processes stopped. Run the script again to restart."
        exit 0
        ;;
    8)
        echo -e "${GREEN}Exiting...${NC}"
        exit 0
        ;;
    *)
        print_error "Invalid choice. Please run the script again."
        ;;
esac