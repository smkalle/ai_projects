#!/bin/bash

# Qdrant Vector Database Startup Script
# Starts Qdrant using Docker for the Energy Document AI system

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    Starting Qdrant Vector Database       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}\n"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

# Stop any existing Qdrant container
if [ "$(docker ps -aq -f name=qdrant)" ]; then
    echo -e "${YELLOW}Stopping existing Qdrant container...${NC}"
    docker stop qdrant &> /dev/null
    docker rm qdrant &> /dev/null
fi

# Start Qdrant container
echo -e "${YELLOW}Starting Qdrant container...${NC}"
docker run -d \
    --name qdrant \
    -p 6333:6333 \
    -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant:latest

# Wait for Qdrant to be ready
echo -e "${YELLOW}Waiting for Qdrant to be ready...${NC}"
sleep 5

# Check if Qdrant is running
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Qdrant is running successfully!${NC}"
    echo -e "${GREEN}   Web UI: http://localhost:6333/dashboard${NC}"
    echo -e "${GREEN}   API: http://localhost:6333${NC}"
    echo -e "${GREEN}   Storage: $(pwd)/qdrant_storage${NC}"
else
    echo -e "${RED}❌ Failed to start Qdrant${NC}"
    echo "Check Docker logs: docker logs qdrant"
    exit 1
fi

echo -e "\n${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}Qdrant is ready for Energy Document AI${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}\n"