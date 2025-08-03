import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Smoke tests for health endpoint"""
    
    def test_health_endpoint_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_endpoint_returns_ok_status(self):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}


class TestQueryEndpoint:
    """Smoke tests for query endpoint"""
    
    def test_query_endpoint_accepts_post(self):
        response = client.post("/query", json={"query": "test query"})
        assert response.status_code == 200
    
    def test_query_endpoint_returns_ok_true(self):
        response = client.post("/query", json={"query": "test query"})
        data = response.json()
        assert data["ok"] is True
    
    def test_query_endpoint_returns_data_field(self):
        response = client.post("/query", json={"query": "test query"})
        data = response.json()
        assert "data" in data
    
    def test_query_endpoint_requires_query_field(self):
        response = client.post("/query", json={})
        assert response.status_code == 422  # Validation error
    
    def test_query_endpoint_validates_request_format(self):
        response = client.post("/query", json={"wrong_field": "test"})
        assert response.status_code == 422  # Validation error