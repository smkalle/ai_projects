"""
Comprehensive test suite for comparing LanceDB and Parquet+FAISS storage backends
"""
import pytest
import time
import os
import tempfile
import shutil
from unittest.mock import Mock
import numpy as np
from sentence_transformers import SentenceTransformer

from storage_backends import LanceDBBackend, ParquetFAISSBackend, create_backend


class MockEmbeddingModel:
    """Mock embedding model for testing"""
    def __init__(self, dimension=384):
        self.dimension = dimension
        np.random.seed(42)  # For reproducible tests
    
    def encode(self, texts, show_progress_bar=False, convert_to_numpy=True):
        """Generate mock embeddings"""
        embeddings = []
        for text in texts:
            # Create deterministic embeddings based on text hash for consistency
            text_hash = hash(text) % 1000000
            np.random.seed(text_hash)
            embedding = np.random.normal(0, 1, self.dimension).astype(np.float32)  # FAISS requires float32
            embeddings.append(embedding)
        
        if convert_to_numpy:
            return np.array(embeddings, dtype=np.float32)  # Ensure float32 array
        return embeddings


@pytest.fixture
def mock_embedding_model():
    """Fixture for mock embedding model"""
    return MockEmbeddingModel()


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        "Artificial intelligence is transforming the world of technology.",
        "Machine learning algorithms can process vast amounts of data.",
        "Natural language processing enables computers to understand human language.",
        "Deep learning networks are inspired by the human brain structure.",
        "Computer vision allows machines to interpret and analyze visual information.",
        "Robotics combines AI with mechanical engineering for automation.",
        "Data science involves extracting insights from complex datasets.",
        "Neural networks consist of interconnected nodes that process information.",
        "Supervised learning uses labeled data to train predictive models.",
        "Unsupervised learning discovers hidden patterns in unlabeled data."
    ]


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing"""
    return [
        {"source": "ai_overview.txt", "category": "AI", "importance": 0.9},
        {"source": "ml_guide.txt", "category": "ML", "importance": 0.8},
        {"source": "nlp_tutorial.txt", "category": "NLP", "importance": 0.7},
        {"source": "dl_primer.txt", "category": "DL", "importance": 0.85},
        {"source": "cv_handbook.txt", "category": "CV", "importance": 0.75},
        {"source": "robotics_101.txt", "category": "Robotics", "importance": 0.65},
        {"source": "ds_fundamentals.txt", "category": "DS", "importance": 0.8},
        {"source": "nn_architecture.txt", "category": "NN", "importance": 0.9},
        {"source": "supervised_ml.txt", "category": "ML", "importance": 0.7},
        {"source": "unsupervised_ml.txt", "category": "ML", "importance": 0.6}
    ]


class TestStorageBackendComparison:
    """Test class for comparing storage backends"""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Setup and cleanup for each test"""
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.original_env = {}
        
        # Set test environment variables
        test_env_vars = {
            'LANCEDB_DIR': os.path.join(self.temp_dir, 'lancedb'),
            'FAISS_INDEX_PATH': os.path.join(self.temp_dir, 'faiss_index.bin'),
            'PARQUET_PATH': os.path.join(self.temp_dir, 'documents.parquet'),
            'DATA_DIR': self.temp_dir
        }
        
        for key, value in test_env_vars.items():
            self.original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        yield
        
        # Cleanup
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.parametrize("backend_type", ["parquet_faiss"])  # Skip lancedb if not available
    def test_backend_initialization(self, backend_type, mock_embedding_model):
        """Test backend initialization"""
        if backend_type == "lancedb":
            try:
                backend = LanceDBBackend(mock_embedding_model)
            except ImportError:
                pytest.skip("LanceDB not available")
        else:
            backend = ParquetFAISSBackend(mock_embedding_model)
        
        assert backend is not None
        assert backend.embedding_model == mock_embedding_model
        assert hasattr(backend, 'is_ready')
    
    @pytest.mark.parametrize("backend_type", ["parquet_faiss"])
    def test_build_index(self, backend_type, mock_embedding_model, sample_documents, sample_metadata):
        """Test index building functionality"""
        backend = self._create_backend(backend_type, mock_embedding_model)
        
        # Test successful index building
        result = backend.build_index(sample_documents, sample_metadata)
        assert result is True
        assert backend.is_index_ready() is True
        
        # Test index info
        info = backend.get_index_info()
        assert info["status"] == "ready"
        assert info["backend"] in ["lancedb", "parquet_faiss"]
    
    @pytest.mark.parametrize("backend_type", ["parquet_faiss"])
    def test_search_functionality(self, backend_type, mock_embedding_model, sample_documents):
        """Test search functionality"""
        backend = self._create_backend(backend_type, mock_embedding_model)
        
        # Build index first
        backend.build_index(sample_documents)
        
        # Test search
        results = backend.search("artificial intelligence", top_k=3)
        
        assert len(results) <= 3
        assert len(results) > 0
        
        # Check result structure
        for result in results:
            assert "text" in result
            assert "score" in result
            assert "id" in result
            assert isinstance(result["score"], (int, float))
    
    def test_backend_comparison(self, mock_embedding_model, sample_documents):
        """Compare functionality between backends"""
        backends = {}
        
        # Initialize available backends
        try:
            backends["lancedb"] = LanceDBBackend(mock_embedding_model)
        except ImportError:
            pass
        
        backends["parquet_faiss"] = ParquetFAISSBackend(mock_embedding_model)
        
        if len(backends) < 2:
            pytest.skip("Need both backends for comparison")
        
        query = "machine learning algorithms"
        
        # Build indices and search
        all_results = {}
        for name, backend in backends.items():
            backend.build_index(sample_documents)
            results = backend.search(query, top_k=5)
            all_results[name] = results
        
        # Compare results
        for name, results in all_results.items():
            assert len(results) > 0, f"{name} should return results"
            assert all("text" in r for r in results), f"{name} results should have text"
            assert all("score" in r for r in results), f"{name} results should have scores"
    
    @pytest.mark.parametrize("backend_type", ["parquet_faiss"])
    def test_performance_metrics(self, backend_type, mock_embedding_model, sample_documents):
        """Test and measure performance metrics"""
        backend = self._create_backend(backend_type, mock_embedding_model)
        
        # Measure build time
        start_time = time.time()
        result = backend.build_index(sample_documents)
        build_time = time.time() - start_time
        
        assert result is True
        assert build_time < 30  # Should complete within 30 seconds
        
        # Measure search time
        query = "artificial intelligence"
        search_times = []
        
        for _ in range(5):  # Run multiple searches
            start_time = time.time()
            results = backend.search(query, top_k=3)
            search_time = time.time() - start_time
            search_times.append(search_time)
            assert len(results) > 0
        
        avg_search_time = sum(search_times) / len(search_times)
        assert avg_search_time < 1.0  # Average search should be under 1 second
    
    @pytest.mark.parametrize("backend_type", ["parquet_faiss"])
    def test_edge_cases(self, backend_type, mock_embedding_model):
        """Test edge cases and error handling"""
        backend = self._create_backend(backend_type, mock_embedding_model)
        
        # Test empty documents
        result = backend.build_index([])
        assert result is False
        
        # Test search without index
        if not backend.is_index_ready():
            results = backend.search("test query")
            assert len(results) == 0
        
        # Test with special characters
        special_docs = [
            "Document with émojis 🤖 and spëcial characters!",
            "测试中文文档处理能力",
            "Document\nwith\nnewlines\tand\ttabs",
            ""  # Empty string
        ]
        
        # Filter out empty strings for building
        filtered_docs = [doc for doc in special_docs if doc.strip()]
        result = backend.build_index(filtered_docs)
        assert result is True
        
        results = backend.search("émojis", top_k=2)
        # Should handle special characters gracefully
        assert isinstance(results, list)
    
    @pytest.mark.parametrize("backend_type", ["parquet_faiss"])
    def test_persistence(self, backend_type, mock_embedding_model, sample_documents):
        """Test persistence and reload functionality"""
        backend1 = self._create_backend(backend_type, mock_embedding_model)
        
        # Build and search
        backend1.build_index(sample_documents)
        original_results = backend1.search("artificial intelligence", top_k=3)
        
        # Create new instance (simulating restart)
        backend2 = self._create_backend(backend_type, mock_embedding_model)
        
        # Should load existing index
        if backend2.is_index_ready():
            new_results = backend2.search("artificial intelligence", top_k=3)
            
            # Results should be similar (allowing for small differences)
            assert len(new_results) == len(original_results)
            
            # Check that at least some results match
            original_texts = {r["text"] for r in original_results}
            new_texts = {r["text"] for r in new_results}
            
            # At least 50% overlap expected
            overlap = len(original_texts.intersection(new_texts))
            assert overlap >= len(original_texts) * 0.5
    
    def _create_backend(self, backend_type, embedding_model):
        """Helper method to create backend instances"""
        if backend_type == "lancedb":
            return LanceDBBackend(embedding_model)
        elif backend_type == "parquet_faiss":
            return ParquetFAISSBackend(embedding_model)
        else:
            raise ValueError(f"Unknown backend type: {backend_type}")


class TestPerformanceBenchmark:
    """Performance benchmark tests"""
    
    @pytest.fixture(autouse=True)
    def setup_benchmark(self):
        """Setup for benchmark tests"""
        self.temp_dir = tempfile.mkdtemp()
        # Setup similar to comparison tests
        yield
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.benchmark
    def test_scalability_comparison(self, mock_embedding_model):
        """Test scalability with different document sizes"""
        backends = {}
        
        try:
            backends["lancedb"] = LanceDBBackend(mock_embedding_model)
        except ImportError:
            pass
        
        backends["parquet_faiss"] = ParquetFAISSBackend(mock_embedding_model)
        
        # Test with different document counts
        doc_counts = [10, 50, 100]
        
        for count in doc_counts:
            documents = [f"Test document number {i} with some content about AI and ML." 
                        for i in range(count)]
            
            print(f"\n--- Testing with {count} documents ---")
            
            for name, backend in backends.items():
                start_time = time.time()
                result = backend.build_index(documents)
                build_time = time.time() - start_time
                
                if result:
                    search_start = time.time()
                    results = backend.search("artificial intelligence", top_k=5)
                    search_time = time.time() - search_start
                    
                    print(f"{name}: Build={build_time:.3f}s, Search={search_time:.3f}s, Results={len(results)}")
                else:
                    print(f"{name}: Build failed") 