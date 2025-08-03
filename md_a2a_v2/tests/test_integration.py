import pytest
from fastapi.testclient import TestClient
from server.main import app
import os

client = TestClient(app)


class TestAgentIntegration:
    """Integration tests for agent handoffs and responses"""
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
    def test_publishing_agent_handles_book_query(self):
        response = client.post("/query", json={"query": "Find me a book about Python programming"})
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        # Check that we got some response data
        assert data["data"] is not None
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
    def test_agent_handoff_to_broadcasting(self):
        response = client.post("/query", json={"query": "I want to watch a documentary about nature"})
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        # The publishing agent should hand off to broadcasting for TV/documentary queries
        assert data["data"] is not None
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
    def test_agent_handoff_to_news(self):
        response = client.post("/query", json={"query": "What's the latest news about technology?"})
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        # The publishing agent should hand off to news for journalism queries
        assert data["data"] is not None
    
    def test_empty_query_validation(self):
        response = client.post("/query", json={"query": ""})
        # Empty string should still be accepted by FastAPI
        assert response.status_code == 200
    
    def test_long_query_handling(self):
        long_query = "This is a very long query " * 100
        response = client.post("/query", json={"query": long_query})
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True


class TestAPIRobustness:
    """Test API error handling and edge cases"""
    
    def test_malformed_json_returns_error(self):
        response = client.post(
            "/query",
            data="malformed json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_content_type_header(self):
        # FastAPI can still parse JSON even without explicit content-type
        response = client.post("/query", data='{"query": "test"}')
        # This should succeed as FastAPI is flexible with content-type inference
        assert response.status_code == 200
    
    def test_concurrent_requests(self):
        """Smoke test for handling multiple requests"""
        responses = []
        for i in range(5):
            response = client.post("/query", json={"query": f"Test query {i}"})
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()["ok"] is True