#!/bin/bash
# Setup script for MCP AI Agent Tutorial

echo "🚀 Setting up MCP AI Agent Tutorial..."

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file. Please add your API keys."
fi

echo "✅ Setup completed!"
echo "Next steps:"
echo "1. Add your API keys to .env file"
echo "2. Run: ./scripts/run_dev.sh"
