#!/bin/bash

# Energize Platform Quick Start Script
# This script sets up and runs the Energize AI platform

echo "⚡ Energize AI Platform - Quick Start"
echo "======================================"
echo "🌍 Mission: Save the planet through intelligent energy management!"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Error: Python 3.11+ is required (found $python_version)"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "🔧 Creating environment configuration..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your configuration"
fi

# Start services
echo ""
echo "🚀 Starting services..."
echo "========================"

# Start backend
echo "Starting backend API..."
python start_backend.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start dashboard
echo "Starting Streamlit dashboard..."
streamlit run demo_dashboard.py --server.port 8501 --server.address 0.0.0.0 &
DASHBOARD_PID=$!

# Wait for services to start
sleep 5

echo ""
echo "✅ Services are running!"
echo "========================"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🖥️  Dashboard: http://localhost:8501"
echo "👤 Demo Login: demo@energize.io / demo123"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle shutdown
trap "echo 'Shutting down...'; kill $BACKEND_PID $DASHBOARD_PID; exit" INT

# Keep script running
wait