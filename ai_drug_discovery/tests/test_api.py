"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_analyze_drug_repurposing():
    """Test drug repurposing analysis endpoint"""
    test_data = {
        "disease": {
            "name": "Test Disease",
            "description": "A test rare disease"
        },
        "analysis_parameters": {
            "confidence_threshold": 0.7,
            "max_results": 5
        }
    }

    response = client.post("/api/v1/analyze/repurposing", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "results" in data