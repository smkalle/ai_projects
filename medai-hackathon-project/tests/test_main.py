"""
Test suite for NGO Medical AI Assistant
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint returns HTML"""
    response = client.get("/")
    assert response.status_code == 200
    assert "NGO Medical AI Assistant" in response.text

def test_sample_cases():
    """Test sample cases endpoint"""
    response = client.get("/api/sample-cases")
    assert response.status_code == 200
    data = response.json()
    assert "sample_cases" in data
    assert len(data["sample_cases"]) > 0

def test_medical_analysis():
    """Test medical analysis endpoint"""
    test_request = {
        "symptoms": "Patient has persistent cough and fever for 3 days",
        "patient_history": "No previous medical issues",
        "image_type": "chest_xray",
        "priority": "normal"
    }

    response = client.post("/api/analyze", json=test_request)
    assert response.status_code == 200
    data = response.json()

    # Check required fields
    assert "analysis_id" in data
    assert "reasoning_chain" in data
    assert "findings" in data
    assert "recommendations" in data
    assert "confidence_score" in data
    assert "disclaimers" in data

def test_medical_chat():
    """Test medical chat endpoint"""
    test_request = {
        "message": "What are the signs of pneumonia?"
    }

    response = client.post("/api/chat", json=test_request)
    assert response.status_code == 200
    data = response.json()

    assert "response" in data
    assert "disclaimers" in data
    assert len(data["response"]) > 0

def test_invalid_analysis_request():
    """Test analysis with invalid request"""
    test_request = {
        "symptoms": "short",  # Too short, should fail validation
        "patient_history": "",
        "image_type": "chest_xray"
    }

    response = client.post("/api/analyze", json=test_request)
    assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    pytest.main([__file__])
