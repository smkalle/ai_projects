"""
Tests for RAG system functionality
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
import sys

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from models.rag_system import EnergyRAGSystem
from models.pdf_processor import EnergyPDFProcessor
from utils.config import settings

class TestEnergyRAGSystem:
    """Test suite for EnergyRAGSystem"""

    @pytest.fixture
    def mock_rag_system(self):
        """Mock RAG system for testing"""
        with patch('models.rag_system.QdrantClient') as mock_client, \
             patch('models.rag_system.OpenAIEmbeddings') as mock_embeddings:

            mock_embeddings.return_value.embed_query.return_value = [0.1] * 1536
            mock_embeddings.return_value.embed_documents.return_value = [[0.1] * 1536]

            rag_system = EnergyRAGSystem(
                qdrant_url="localhost",
                qdrant_port=6333,
                openai_api_key="test_key",
                collection_name="test_collection"
            )

            return rag_system, mock_client, mock_embeddings

    def test_initialization(self, mock_rag_system):
        """Test RAG system initialization"""
        rag_system, mock_client, mock_embeddings = mock_rag_system

        assert rag_system.collection_name == "test_collection"
        assert rag_system.text_splitter is not None
        mock_client.assert_called_once()
        mock_embeddings.assert_called_once()

    def test_process_and_store_document(self, mock_rag_system):
        """Test document processing and storage"""
        rag_system, mock_client, mock_embeddings = mock_rag_system

        # Mock successful processing
        mock_client.return_value.get_collections.return_value.collections = []
        mock_client.return_value.upsert.return_value = True

        test_text = "This is a test energy document about solar panels and wind turbines."

        result = rag_system.process_and_store_document(
            text=test_text,
            document_name="test_doc.pdf",
            document_type="renewable"
        )

        assert result > 0  # Should return number of chunks stored
        mock_client.return_value.upsert.assert_called_once()

    def test_similarity_search(self, mock_rag_system):
        """Test similarity search functionality"""
        rag_system, mock_client, mock_embeddings = mock_rag_system

        # Mock search results
        mock_result = Mock()
        mock_result.payload = {
            "chunk_text": "Test content about energy systems",
            "document_name": "test_doc.pdf",
            "document_type": "technical",
            "chunk_index": 0
        }
        mock_result.score = 0.85

        mock_client.return_value.search.return_value = [mock_result]

        results = rag_system.similarity_search(
            query="energy systems",
            k=5,
            document_type="technical"
        )

        assert len(results) == 1
        assert results[0]["score"] == 0.85
        assert results[0]["document_name"] == "test_doc.pdf"

class TestEnergyPDFProcessor:
    """Test suite for EnergyPDFProcessor"""

    @pytest.fixture
    def mock_pdf_processor(self):
        """Mock PDF processor for testing"""
        with patch('models.pdf_processor.OpenAI') as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Extracted text from PDF"

            mock_openai.return_value.chat.completions.create.return_value = mock_response

            processor = EnergyPDFProcessor(
                openai_api_key="test_key",
                dpi=300
            )

            return processor, mock_openai

    def test_initialization(self, mock_pdf_processor):
        """Test PDF processor initialization"""
        processor, mock_openai = mock_pdf_processor

        assert processor.dpi == 300
        mock_openai.assert_called_once()

    @patch('models.pdf_processor.pdfium.PdfDocument')
    def test_render_page_to_image(self, mock_pdf_doc, mock_pdf_processor):
        """Test page rendering functionality"""
        processor, _ = mock_pdf_processor

        # Mock PDF document and page
        mock_doc = Mock()
        mock_page = Mock()
        mock_image = Mock()

        mock_pdf_doc.return_value = mock_doc
        mock_doc.get_page.return_value = mock_page
        mock_page.render.return_value.to_pil.return_value = mock_image

        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            result = processor.render_page_to_image(tmp_file.name, 0)

            assert result == mock_image
            mock_doc.get_page.assert_called_once_with(0)
            mock_page.close.assert_called_once()
            mock_doc.close.assert_called_once()

def test_configuration():
    """Test configuration loading"""
    assert settings.app_name is not None
    assert settings.chunk_size > 0
    assert settings.max_iterations > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
