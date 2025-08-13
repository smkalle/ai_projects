#!/bin/bash
# Deployment script

echo "🚀 Deploying MCP AI Agent..."

# Build Docker image
docker build -t mcp-ai-agent .

# Run with Docker Compose
docker-compose up -d

echo "✅ Deployment completed!"
echo "Access the application at:"
echo "- Frontend: http://localhost:8501"
echo "- API: http://localhost:8000"
