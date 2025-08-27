#!/bin/bash

# Qdrant Vector Database Startup Script for Termux
# Downloads and runs Qdrant binary natively on Android/Termux

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    Qdrant for Termux/Android Setup       ║${NC}"
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

# Check if we're in Termux
if [ ! -n "$TERMUX_VERSION" ] && [ ! -d "$PREFIX" ]; then
    echo -e "${YELLOW}⚠️  This script is optimized for Termux. For regular Linux, use start_qdrant.sh${NC}"
fi

# Create qdrant directory
QDRANT_DIR="$HOME/qdrant"
QDRANT_DATA_DIR="$QDRANT_DIR/storage"

print_status "Setting up Qdrant directories..."
mkdir -p "$QDRANT_DIR"
mkdir -p "$QDRANT_DATA_DIR"
cd "$QDRANT_DIR"

# Check architecture
ARCH=$(uname -m)
case $ARCH in
    aarch64|arm64)
        QDRANT_ARCH="aarch64-unknown-linux-gnu"
        ;;
    armv7l|armhf)
        QDRANT_ARCH="armv7-unknown-linux-gnueabihf"
        ;;
    x86_64)
        QDRANT_ARCH="x86_64-unknown-linux-gnu"
        ;;
    *)
        print_error "Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

print_success "Detected architecture: $ARCH"

# Qdrant version
QDRANT_VERSION="v1.7.4"
QDRANT_BINARY="qdrant-$QDRANT_ARCH"
QDRANT_URL="https://github.com/qdrant/qdrant/releases/download/$QDRANT_VERSION/$QDRANT_BINARY"

# Check if Qdrant binary exists
if [ ! -f "qdrant" ]; then
    print_status "Downloading Qdrant binary for $ARCH..."
    if command -v curl >/dev/null 2>&1; then
        if curl -L -o qdrant "$QDRANT_URL"; then
            chmod +x qdrant
            print_success "Qdrant binary downloaded and made executable"
        else
            print_error "Failed to download Qdrant binary"
            echo -e "${YELLOW}Manual download: $QDRANT_URL${NC}"
            exit 1
        fi
    elif command -v wget >/dev/null 2>&1; then
        if wget -O qdrant "$QDRANT_URL"; then
            chmod +x qdrant
            print_success "Qdrant binary downloaded and made executable"
        else
            print_error "Failed to download Qdrant binary"
            exit 1
        fi
    else
        print_error "Neither curl nor wget found. Please install one of them:"
        echo "pkg install curl"
        exit 1
    fi
else
    print_success "Qdrant binary already exists"
fi

# Kill existing Qdrant processes
print_status "Checking for existing Qdrant processes..."
if pgrep -f "qdrant" > /dev/null; then
    print_status "Stopping existing Qdrant processes..."
    pkill -f "qdrant"
    sleep 2
fi

# Create Qdrant configuration
print_status "Creating Qdrant configuration..."
cat > config.yaml << EOF
service:
  host: 0.0.0.0
  http_port: 6333
  grpc_port: 6334
  
storage:
  storage_path: ./storage
  snapshots_path: ./snapshots
  on_disk_payload: true
  
log_level: INFO

hnsw_config:
  m: 16
  ef_construct: 100
  full_scan_threshold: 10000

# Memory optimization for mobile devices
cluster:
  enabled: false

# Reduce memory usage
service:
  max_request_size_mb: 32
EOF

print_success "Configuration created"

# Start Qdrant
print_status "Starting Qdrant vector database..."
echo -e "${BLUE}Starting Qdrant on:${NC}"
echo -e "${BLUE}  HTTP API: http://localhost:6333${NC}"
echo -e "${BLUE}  gRPC API: localhost:6334${NC}"
echo -e "${BLUE}  Data dir: $QDRANT_DATA_DIR${NC}"
echo -e "${BLUE}  Config: $QDRANT_DIR/config.yaml${NC}\n"

# Function to handle shutdown
cleanup() {
    echo -e "\n${YELLOW}Shutting down Qdrant...${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Qdrant with configuration
./qdrant --config-path config.yaml &
QDRANT_PID=$!

# Wait for Qdrant to start
print_status "Waiting for Qdrant to initialize..."
sleep 5

# Check if Qdrant is running
if kill -0 $QDRANT_PID 2>/dev/null; then
    # Try to connect to health endpoint
    for i in {1..10}; do
        if curl -s http://localhost:6333/health > /dev/null 2>&1; then
            print_success "Qdrant is running successfully!"
            echo -e "${GREEN}Access Qdrant at: http://localhost:6333${NC}"
            echo -e "${GREEN}API Documentation: http://localhost:6333/docs${NC}"
            break
        fi
        sleep 2
    done
    
    if ! curl -s http://localhost:6333/health > /dev/null 2>&1; then
        print_error "Qdrant started but health check failed"
        echo -e "${YELLOW}Check if port 6333 is available${NC}"
    fi
    
    echo -e "\n${GREEN}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}Qdrant is ready for Energy Document AI${NC}"
    echo -e "${GREEN}Press Ctrl+C to stop${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════${NC}\n"
    
    # Wait for the process
    wait $QDRANT_PID
    
else
    print_error "Failed to start Qdrant"
    echo -e "${YELLOW}Check the logs above for details${NC}"
    exit 1
fi