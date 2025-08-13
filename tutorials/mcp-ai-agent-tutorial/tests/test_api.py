"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Test suite for API endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "MCP AI Agent API"

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_list_agents_empty(self):
        """Test listing agents when none exist."""
        response = client.get("/agents")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_agent_missing_data(self):
        """Test creating agent with missing data."""
        response = client.post("/agents/create", json={})
        assert response.status_code == 422  # Validation error

    def test_get_nonexistent_agent(self):
        """Test getting status of non-existent agent."""
        response = client.get("/agents/nonexistent/status")
        assert response.status_code == 404
