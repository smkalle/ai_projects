#!/bin/bash
# Setup script for Rare Disease Drug Repurposing AI

echo "🧬 Setting up Rare Disease Drug Repurposing AI System"
echo "=================================================="

# Check Python version
python_version=$(python3 --version 2>&1)
echo "📋 Python Version: $python_version"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "🔐 Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys"
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 To start the system:"
echo "   Backend:  python scripts/run_backend.py"
echo "   Frontend: python scripts/run_frontend.py"
echo ""
echo "🌐 URLs:"
echo "   Frontend: http://localhost:8501"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "💡 For demo mode, no API keys are required!"