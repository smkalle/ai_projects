#!/bin/bash

# Hospital Booking System - Setup Script
# This script sets up the development environment for the Hospital Booking System

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        exit 1
    fi
}

# Banner
echo -e "${BLUE}"
echo "🏥 Hospital Booking System Setup"
echo "================================="
echo -e "${NC}"

# Check prerequisites
print_status "Checking prerequisites..."

check_command python3
check_command pip

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_error "Python 3.8+ is required. Found version $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing production dependencies..."
pip install -r requirements.txt

print_status "Installing development dependencies..."
pip install -r requirements-dev.txt

print_success "Dependencies installed"

# Set up pre-commit hooks
if command -v pre-commit &> /dev/null; then
    print_status "Setting up pre-commit hooks..."
    pre-commit install
    print_success "Pre-commit hooks installed"
else
    print_warning "pre-commit not found, skipping hook installation"
fi

# Set up environment variables
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration"
    else
        print_status "Creating default .env file..."
        cat > .env << EOF
# Hospital Booking System Configuration
DATABASE_URL=sqlite:///hospital_booking.db

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# JWT Secret
JWT_SECRET_KEY=your-secret-key-change-this-in-production

# API Keys (Optional)
GOOGLE_CALENDAR_CLIENT_ID=your-google-client-id
GOOGLE_CALENDAR_CLIENT_SECRET=your-google-client-secret
MICROSOFT_GRAPH_CLIENT_ID=your-microsoft-client-id
MICROSOFT_GRAPH_CLIENT_SECRET=your-microsoft-client-secret
EOF
        print_warning "Default .env file created. Please edit with your configuration"
    fi
else
    print_warning ".env file already exists"
fi

# Initialize database
print_status "Initializing database..."
python -c "from database.models import init_db; init_db()"
print_success "Database initialized"

# Seed database with sample data
print_status "Seeding database with sample data..."
if [ -f "database/seed_data.py" ]; then
    python database/seed_data.py
    print_success "Database seeded with sample data"
else
    print_warning "Seed data script not found, skipping"
fi

# Run basic tests
print_status "Running basic tests..."
if python -c "import streamlit; import sqlalchemy; import plotly" 2>/dev/null; then
    print_success "Core dependencies are working"
else
    print_error "Core dependencies test failed"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs reports uploads temp
print_success "Directories created"

# Set permissions (if needed)
chmod +x setup.sh 2>/dev/null || true

# Final success message
echo ""
print_success "Setup completed successfully!"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Edit the .env file with your configuration"
echo "2. Run the application: streamlit run app.py"
echo "3. Open your browser to http://localhost:8501"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "• Run app: streamlit run app.py"
echo "• Run tests: python -m pytest tests/"
echo "• Format code: make format"
echo "• See all commands: make help"
echo ""

# Check if we should start the application
read -p "Would you like to start the application now? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting Hospital Booking System..."
    streamlit run app.py
fi