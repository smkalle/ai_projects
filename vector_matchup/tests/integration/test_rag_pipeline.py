import pytest
from unittest.mock import Mock, patch
from rag_pipeline import RAGPipeline


class MockEmbeddingModel:
    """Mock embedding model for testing"""
    def encode(self, texts, show_progress_bar=False, convert_to_numpy=True):
        import numpy as np
        # Return mock embeddings with correct dtype for FAISS
        embeddings = np.random.rand(len(texts), 384).astype(np.float32)
        return embeddings


@pytest.fixture
def mock_embedding_model():
    """Fixture for mock embedding model"""
    return MockEmbeddingModel()


@pytest.fixture
def rag_pipeline():
    # Create RAG pipeline with parquet_faiss backend
    pipeline = RAGPipeline(backend_type="parquet_faiss")
    
    # Mock the embedding model to avoid loading actual models
    with patch('rag_pipeline.SentenceTransformer') as mock_sentence_transformer:
        mock_sentence_transformer.return_value = MockEmbeddingModel()
        
        # Initialize models with mock
        pipeline.initialize_models()
        
    return pipeline


def test_end_to_end_rag(rag_pipeline):
    # Test the complete RAG pipeline
    # 1. Process a test document
    test_doc = "This is a test document about artificial intelligence. AI is transforming the world."
    success, message = rag_pipeline.process_document(test_doc, "test_doc.txt")
    assert success is True
    assert "chunks indexed" in message
    
    # 2. Test querying
    query_result = rag_pipeline.query("What is artificial intelligence?", use_llm_synthesis=False)
    assert query_result["success"] is True
    assert len(query_result["sources"]) > 0
    assert query_result["processing_time"] > 0
    
    # 3. Test system status
    status = rag_pipeline.get_system_status()
    assert status["models_loaded"] is True
    assert status["backend_type"] == "parquet_faiss"
    assert "index_info" in status 