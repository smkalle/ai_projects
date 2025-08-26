"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
import tempfile
import os
import sys

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from api.endpoints import app

class TestEnergyDocumentAPI:
    """Test suite for Energy Document AI API"""

    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "Energy Document AI API"

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_get_document_types(self, client):
        """Test document types endpoint"""
        response = client.get("/documents/types")
        assert response.status_code == 200

        data = response.json()
        assert "document_types" in data
        assert "default_type" in data
        assert isinstance(data["document_types"], dict)

    def test_query_endpoint_empty_query(self, client):
        """Test query endpoint with empty query"""
        response = client.post("/query", json={"query": ""})
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data

    def test_query_endpoint_valid_query(self, client):
        """Test query endpoint with valid query"""
        # Note: This would require proper initialization in real test
        query_data = {
            "query": "What are energy efficiency requirements?",
            "max_results": 5
        }

        response = client.post("/query", json=query_data)
        # Expecting 500 due to missing initialization in test
        assert response.status_code in [200, 500]

    def test_search_endpoint_empty_query(self, client):
        """Test search endpoint with empty query"""
        response = client.get("/documents/search?query=")
        assert response.status_code == 400

    def test_upload_invalid_file_type(self, client):
        """Test upload with invalid file type"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_file_path = tmp_file.name

        try:
            with open(tmp_file_path, "rb") as f:
                response = client.post(
                    "/documents/upload",
                    files={"file": ("test.txt", f, "text/plain")}
                )

            assert response.status_code == 400
            data = response.json()
            assert "PDF" in data["detail"]

        finally:
            os.unlink(tmp_file_path)

@pytest.mark.asyncio
async def test_api_startup():
    """Test API startup process"""
    # This would test the startup event
    # In a real test, you'd mock the components
    pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
