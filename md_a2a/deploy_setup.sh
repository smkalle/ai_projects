#!/bin/bash

# Medical AI Assistant MVP V2.0 - Deployment Setup Script
# This script automates the complete deployment process after git pull

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Print banner
echo -e "${BLUE}
╔══════════════════════════════════════════════════════════════╗
║            Medical AI Assistant MVP V2.0                     ║
║              Deployment Setup Script                         ║
╚══════════════════════════════════════════════════════════════╝
${NC}"

log "Starting deployment setup..."

# Check prerequisites
log "Checking prerequisites..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    error "Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    error "Python 3.9+ is required. Found: $PYTHON_VERSION"
    exit 1
fi

success "Python $PYTHON_VERSION detected"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    error "Please run this script from the project root directory"
    exit 1
fi

success "Project structure validated"

# Step 1: Virtual Environment Setup
log "Setting up virtual environment..."

if [ -d ".venv" ]; then
    warning "Virtual environment already exists. Removing and recreating..."
    rm -rf .venv
fi

python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

success "Virtual environment created and activated"

# Step 2: Install Dependencies
log "Installing dependencies..."

pip install -r requirements.txt

success "Dependencies installed successfully"

# Step 3: Environment Configuration
log "Setting up environment configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.sample" ]; then
        cp .env.sample .env
        success "Environment file created from sample"
    else
        # Create default .env file
        cat > .env << EOF
# OpenAI Configuration (Optional - will use fallback if not provided)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Application Configuration
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# AI Configuration
AI_FALLBACK_ENABLED=true
AI_MOCK_MODE=false
COST_OPTIMIZATION_ENABLED=true

# Database Configuration
DATABASE_URL=sqlite:///./mvp_medical.db

# Upload Configuration
UPLOAD_DIRECTORY=./static/photos
MAX_UPLOAD_SIZE_MB=10

# Logging
LOG_LEVEL=INFO
EOF
        success "Default environment file created"
    fi
    
    warning "Please edit .env file with your configuration before starting the application"
    warning "Especially set your OPENAI_API_KEY if you want to use AI features"
else
    success "Environment file already exists"
fi

# Step 4: Create Upload Directory
log "Creating upload directory..."

mkdir -p static/photos
chmod 755 static/photos

success "Upload directory created"

# Step 5: Database Initialization Test
log "Testing database initialization..."

python -c "
try:
    from src.database import init_db
    init_db()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization failed: {e}')
    exit(1)
"

success "Database initialization test passed"

# Step 6: Configuration Test
log "Testing configuration..."

python -c "
try:
    from src.config import settings
    print(f'Configuration loaded successfully - Environment: {settings.ENVIRONMENT}')
except Exception as e:
    print(f'Configuration test failed: {e}')
    exit(1)
"

success "Configuration test passed"

# Step 7: Run Tests
log "Running test suite..."

if python -m pytest -v --tb=short; then
    success "All tests passed"
else
    warning "Some tests failed, but continuing with deployment"
fi

# Step 8: API Test Suite
log "Running API test suite..."

if python api_test_suite.py; then
    success "API test suite passed"
else
    warning "API test suite had issues, but continuing"
fi

# Step 9: Health Check Test
log "Testing health endpoints..."

# Start the server in background for testing
python -m src.main &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Test health endpoint
if curl -s -f http://localhost:8000/api/health > /dev/null; then
    success "Health endpoint responding"
else
    warning "Health endpoint test failed"
fi

# Stop the test server
kill $SERVER_PID 2>/dev/null || true
sleep 2

# Step 10: Final Instructions
echo -e "${GREEN}
╔══════════════════════════════════════════════════════════════╗
║                 🎉 DEPLOYMENT COMPLETE! 🎉                  ║
╚══════════════════════════════════════════════════════════════╝
${NC}"

echo -e "${BLUE}Next Steps:${NC}"
echo "1. Edit .env file with your configuration:"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Start the application:"
echo "   ${YELLOW}source .venv/bin/activate${NC}"
echo "   ${YELLOW}python -m src.main${NC}"
echo ""
echo "3. Or start with auto-reload for development:"
echo "   ${YELLOW}uvicorn src.main:app --reload --host 0.0.0.0 --port 8000${NC}"
echo ""
echo -e "${BLUE}Access Points:${NC}"
echo "• API Documentation: ${YELLOW}http://localhost:8000/docs${NC}"
echo "• Health Check: ${YELLOW}http://localhost:8000/api/health${NC}"
echo "• Main Dashboard: ${YELLOW}http://localhost:8000/${NC}"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "• Run tests: ${YELLOW}python -m pytest -v${NC}"
echo "• API tests: ${YELLOW}python api_test_suite.py${NC}"
echo "• Health check: ${YELLOW}curl http://localhost:8000/api/health${NC}"
echo ""

if [ ! -s .env ] || grep -q "your_openai_api_key_here" .env; then
    echo -e "${YELLOW}⚠️  Important: Update your .env file with real values before starting!${NC}"
    echo -e "${YELLOW}   Especially the OPENAI_API_KEY for AI features.${NC}"
fi

success "Deployment setup completed successfully!"

log "Virtual environment is ready at: $(pwd)/.venv"
log "To activate: source .venv/bin/activate"

exit 0 