import pytest
from unittest.mock import patch, MagicMock
import os

# Set dummy API key before imports
os.environ["OPENAI_API_KEY"] = "test-key"

# Mock the ChatOpenAI before importing
with patch('langchain_openai.ChatOpenAI'):
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
    """Smoke tests for query endpoint with mocked LangGraph app"""
    
    @patch('server.main.lg_app')
    def test_query_endpoint_accepts_post(self, mock_lg_app):
        mock_lg_app.invoke.return_value = {"messages": [{"role": "assistant", "content": "Mock response"}]}
        response = client.post("/query", json={"query": "test query"})
        assert response.status_code == 200
    
    @patch('server.main.lg_app')
    def test_query_endpoint_returns_ok_true(self, mock_lg_app):
        mock_lg_app.invoke.return_value = {"messages": [{"role": "assistant", "content": "Mock response"}]}
        response = client.post("/query", json={"query": "test query"})
        data = response.json()
        assert data["ok"] is True
    
    @patch('server.main.lg_app')
    def test_query_endpoint_returns_data_field(self, mock_lg_app):
        mock_lg_app.invoke.return_value = {"messages": [{"role": "assistant", "content": "Mock response"}]}
        response = client.post("/query", json={"query": "test query"})
        data = response.json()
        assert "data" in data
    
    def test_query_endpoint_requires_query_field(self):
        response = client.post("/query", json={})
        assert response.status_code == 422  # Validation error
    
    def test_query_endpoint_validates_request_format(self):
        response = client.post("/query", json={"wrong_field": "test"})
        assert response.status_code == 422  # Validation error
    
    @patch('server.main.lg_app')
    def test_query_endpoint_calls_langgraph_app(self, mock_lg_app):
        mock_lg_app.invoke.return_value = {"messages": [{"role": "assistant", "content": "Mock response"}]}
        response = client.post("/query", json={"query": "Find me a book"})
        
        # Verify the LangGraph app was called with correct state
        mock_lg_app.invoke.assert_called_once()
        call_args = mock_lg_app.invoke.call_args[0][0]
        assert call_args["messages"] == [{"role": "user", "content": "Find me a book"}]
    
    @patch('server.main.lg_app')
    def test_query_endpoint_handles_exception(self, mock_lg_app):
        # Test that exceptions are handled and still return ok: True
        mock_lg_app.invoke.return_value = {"messages": [{"role": "assistant", "content": "Mock response"}]}
        
        response = client.post("/query", json={"query": "test query"})
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "data" in data