"""
Comprehensive Backend Comparison: LanceDB vs Parquet+FAISS
Head-to-head performance comparison with detailed metrics
"""
import pytest
import time
import os
import tempfile
import shutil
import psutil
import gc
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd
from unittest.mock import patch
import json

from storage_backends import LanceDBBackend, ParquetFAISSBackend, create_backend
from text_processor import TextProcessor
from config import (
    EMBEDDING_MODEL, EMBEDDING_DEVICE, EMBEDDING_BATCH_SIZE, 
    get_embedding_model_info, validate_embedding_config
)


class MockEmbeddingModel:
    """Mock embedding model for consistent testing"""
    def __init__(self, dimension=384):
        self.dimension = dimension
        np.random.seed(42)  # For reproducible tests
    
    def encode(self, texts, show_progress_bar=False, convert_to_numpy=True):
        """Generate consistent mock embeddings"""
        embeddings = []
        for text in texts:
            # Create deterministic embeddings based on text hash
            text_hash = hash(text) % 1000000
            np.random.seed(text_hash)
            embedding = np.random.normal(0, 1, self.dimension).astype(np.float32)
            embeddings.append(embedding)
        
        if convert_to_numpy:
            return np.array(embeddings, dtype=np.float32)
        return embeddings


def create_embedding_model(use_real_model=False):
    """Create embedding model - either mock or real based on configuration"""
    if use_real_model:
        try:
            from sentence_transformers import SentenceTransformer
            
            # Validate configuration first
            config_status = validate_embedding_config()
            if not config_status['valid']:
                print(f"⚠️ Embedding config issues: {config_status['issues']}")
                print("Falling back to mock model...")
                model_info = get_embedding_model_info(EMBEDDING_MODEL)
                return MockEmbeddingModel(model_info.get('dimensions', 384))
            
            print(f"🔄 Loading real embedding model: {EMBEDDING_MODEL}")
            model_info = get_embedding_model_info(EMBEDDING_MODEL)
            print(f"📋 Model Info: {model_info['name']} ({model_info['dimensions']} dims, {model_info['size_mb']}MB)")
            
            # Load real model with configuration
            model = SentenceTransformer(
                EMBEDDING_MODEL, 
                device=EMBEDDING_DEVICE,
                cache_folder=os.getenv('MODEL_CACHE_DIR', './models')
            )
            
            print(f"✅ Successfully loaded {EMBEDDING_MODEL}")
            return model
            
        except ImportError:
            print("⚠️ sentence-transformers not available, using mock model")
            model_info = get_embedding_model_info(EMBEDDING_MODEL)
            return MockEmbeddingModel(model_info.get('dimensions', 384))
        except Exception as e:
            print(f"⚠️ Error loading real model: {e}")
            print("Falling back to mock model...")
            model_info = get_embedding_model_info(EMBEDDING_MODEL)
            return MockEmbeddingModel(model_info.get('dimensions', 384))
    else:
        # Use mock model with dimensions from config
        model_info = get_embedding_model_info(EMBEDDING_MODEL)
        return MockEmbeddingModel(model_info.get('dimensions', 384))


class BackendComparator:
    """Comprehensive backend comparison utility"""
    
    def __init__(self):
        self.results = {
            "lancedb": {},
            "parquet_faiss": {},
            "comparison": {}
        }
        self.test_data_sizes = [100, 500, 1000, 2000]
        
    def generate_test_documents(self, num_docs: int, avg_length: int = 300) -> List[str]:
        """Generate realistic test documents"""
        documents = []
        topics = [
            "artificial intelligence and machine learning applications",
            "climate change and environmental sustainability practices", 
            "financial technology and digital transformation trends",
            "healthcare innovation and medical research developments",
            "space exploration and astronomical discoveries",
            "renewable energy and green technology solutions",
            "cybersecurity and data protection measures",
            "biotechnology and genetic engineering advances"
        ]
        
        np.random.seed(42)
        for i in range(num_docs):
            topic = topics[i % len(topics)]
            length = np.random.normal(avg_length, avg_length * 0.3)
            length = max(100, int(length))
            
            # Generate realistic document content
            sentences = []
            current_length = 0
            while current_length < length:
                sentence_starters = [
                    f"This document discusses {topic} in detail.",
                    f"Recent developments in {topic} show promising results.",
                    f"The impact of {topic} on modern society is significant.",
                    f"Research in {topic} has led to breakthrough discoveries.",
                    f"Companies are investing heavily in {topic} technologies."
                ]
                sentence = np.random.choice(sentence_starters)
                sentences.append(sentence)
                current_length += len(sentence)
            
            documents.append(" ".join(sentences)[:length])
        
        return documents
    
    def measure_backend_performance(self, backend, documents: List[str], 
                                  backend_name: str) -> Dict[str, Any]:
        """Measure comprehensive performance metrics for a backend"""
        print(f"\n🔄 Testing {backend_name} with {len(documents)} documents...")
        
        # Memory before
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Build index - timing
        build_start = time.time()
        success = backend.build_index(documents)
        build_time = time.time() - build_start
        
        if not success:
            return {"error": "Failed to build index", "backend": backend_name}
        
        # Memory after build
        memory_after_build = process.memory_info().rss / 1024 / 1024  # MB
        memory_used_build = memory_after_build - memory_before
        
        # Index info
        index_info = backend.get_index_info()
        
        # Search performance testing
        test_queries = [
            "artificial intelligence applications",
            "climate change solutions", 
            "financial technology innovation",
            "healthcare research developments",
            "space exploration discoveries"
        ]
        
        search_times = []
        search_results_counts = []
        
        for query in test_queries:
            search_start = time.time()
            results = backend.search(query, top_k=10)
            search_time = time.time() - search_start
            
            search_times.append(search_time * 1000)  # Convert to ms
            search_results_counts.append(len(results))
        
        # Calculate storage size
        storage_size = self._calculate_storage_size(backend_name)
        
        # Memory efficiency
        memory_per_doc = memory_used_build / len(documents) if len(documents) > 0 else 0
        
        # Throughput calculations
        docs_per_second = len(documents) / build_time if build_time > 0 else 0
        
        metrics = {
            "backend": backend_name,
            "documents_count": len(documents),
            "build_time_seconds": round(build_time, 3),
            "build_success": success,
            "throughput_docs_per_sec": round(docs_per_second, 2),
            "memory_used_mb": round(memory_used_build, 2),
            "memory_per_doc_mb": round(memory_per_doc, 4),
            "storage_size_mb": round(storage_size, 2),
            "search_times_ms": {
                "min": round(min(search_times), 3),
                "max": round(max(search_times), 3),
                "avg": round(np.mean(search_times), 3),
                "median": round(np.median(search_times), 3)
            },
            "search_results_avg": round(np.mean(search_results_counts), 1),
            "index_info": index_info,
            "chars_per_mb": round(sum(len(doc) for doc in documents) / storage_size, 0) if storage_size > 0 else 0
        }
        
        return metrics
    
    def _calculate_storage_size(self, backend_name: str) -> float:
        """Calculate storage size for backend data"""
        if backend_name == "lancedb":
            # LanceDB stores in a directory
            lancedb_path = "./data/lancedb"
            if os.path.exists(lancedb_path):
                return self._get_directory_size(lancedb_path) / 1024 / 1024  # MB
        elif backend_name == "parquet_faiss":
            # Parquet + FAISS files
            total_size = 0
            files = ["./data/documents.parquet", "./data/faiss_index.idx"]
            for file_path in files:
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
            return total_size / 1024 / 1024  # MB
        
        return 0.0
    
    def _get_directory_size(self, path: str) -> int:
        """Get total size of directory"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size
    
    def compare_backends(self, documents: List[str], use_real_embeddings=False) -> Dict[str, Any]:
        """Run comprehensive comparison between backends"""
        print(f"\n🚀 Starting comprehensive backend comparison with {len(documents)} documents")
        
        # Create embedding model
        embedding_model = create_embedding_model(use_real_embeddings)
        model_info = get_embedding_model_info(EMBEDDING_MODEL)
        
        print(f"📊 Using embedding model: {model_info['name']}")
        print(f"🔧 Configuration: {EMBEDDING_DEVICE} device, batch_size={EMBEDDING_BATCH_SIZE}")
        
        # Test both backends
        # LanceDB Backend
        try:
            lancedb_backend = LanceDBBackend(embedding_model=embedding_model)
            lancedb_metrics = self.measure_backend_performance(
                lancedb_backend, documents, "lancedb"
            )
        except Exception as e:
            print(f"⚠️ LanceDB test failed: {e}")
            lancedb_metrics = {"error": str(e), "backend": "lancedb"}
        
        # Parquet+FAISS Backend  
        try:
            faiss_backend = ParquetFAISSBackend(embedding_model=embedding_model)
            faiss_metrics = self.measure_backend_performance(
                faiss_backend, documents, "parquet_faiss"
            )
        except Exception as e:
            print(f"⚠️ Parquet+FAISS test failed: {e}")
            faiss_metrics = {"error": str(e), "backend": "parquet_faiss"}
        
        # Cleanup
        gc.collect()
        
        # Generate comparison analysis
        comparison = self._generate_comparison_analysis(lancedb_metrics, faiss_metrics)
        
        return {
            "lancedb": lancedb_metrics,
            "parquet_faiss": faiss_metrics,
            "comparison": comparison,
            "embedding_config": {
                "model_name": EMBEDDING_MODEL,
                "model_info": model_info,
                "device": EMBEDDING_DEVICE,
                "batch_size": EMBEDDING_BATCH_SIZE,
                "use_real_model": use_real_embeddings
            },
            "test_metadata": {
                "documents_count": len(documents),
                "avg_doc_length": np.mean([len(doc) for doc in documents]),
                "total_characters": sum(len(doc) for doc in documents),
                "test_timestamp": time.time()
            }
        }
    
    def _generate_comparison_analysis(self, lancedb_metrics: Dict, faiss_metrics: Dict) -> Dict[str, Any]:
        """Generate detailed comparison analysis"""
        if "error" in lancedb_metrics or "error" in faiss_metrics:
            return {"status": "error", "message": "One or both backends failed"}
        
        # Performance comparisons
        build_time_winner = "lancedb" if lancedb_metrics["build_time_seconds"] < faiss_metrics["build_time_seconds"] else "parquet_faiss"
        throughput_winner = "lancedb" if lancedb_metrics["throughput_docs_per_sec"] > faiss_metrics["throughput_docs_per_sec"] else "parquet_faiss"
        search_speed_winner = "lancedb" if lancedb_metrics["search_times_ms"]["avg"] < faiss_metrics["search_times_ms"]["avg"] else "parquet_faiss"
        memory_winner = "lancedb" if lancedb_metrics["memory_used_mb"] < faiss_metrics["memory_used_mb"] else "parquet_faiss"
        storage_winner = "lancedb" if lancedb_metrics["storage_size_mb"] < faiss_metrics["storage_size_mb"] else "parquet_faiss"
        
        # Calculate percentage differences
        build_time_diff = abs(lancedb_metrics["build_time_seconds"] - faiss_metrics["build_time_seconds"])
        throughput_diff = abs(lancedb_metrics["throughput_docs_per_sec"] - faiss_metrics["throughput_docs_per_sec"])
        search_diff = abs(lancedb_metrics["search_times_ms"]["avg"] - faiss_metrics["search_times_ms"]["avg"])
        memory_diff = abs(lancedb_metrics["memory_used_mb"] - faiss_metrics["memory_used_mb"])
        storage_diff = abs(lancedb_metrics["storage_size_mb"] - faiss_metrics["storage_size_mb"])
        
        # Overall winner calculation
        scores = {"lancedb": 0, "parquet_faiss": 0}
        scores[build_time_winner] += 1
        scores[throughput_winner] += 1  
        scores[search_speed_winner] += 1
        scores[memory_winner] += 1
        scores[storage_winner] += 1
        
        overall_winner = "lancedb" if scores["lancedb"] > scores["parquet_faiss"] else "parquet_faiss"
        
        return {
            "winners": {
                "build_time": build_time_winner,
                "throughput": throughput_winner,
                "search_speed": search_speed_winner,
                "memory_efficiency": memory_winner,
                "storage_efficiency": storage_winner,
                "overall": overall_winner
            },
            "differences": {
                "build_time_seconds": round(build_time_diff, 3),
                "throughput_docs_per_sec": round(throughput_diff, 2),
                "search_time_ms": round(search_diff, 3),
                "memory_mb": round(memory_diff, 2),
                "storage_mb": round(storage_diff, 2)
            },
            "scores": scores,
            "summary": f"{overall_winner.replace('_', '+')} wins overall with {scores[overall_winner]}/5 categories"
        }


@pytest.fixture
def backend_comparator():
    """Fixture for backend comparator"""
    return BackendComparator()


@pytest.fixture
def small_test_documents():
    """Small test dataset"""
    comparator = BackendComparator()
    return comparator.generate_test_documents(100, 250)


@pytest.fixture
def medium_test_documents():
    """Medium test dataset"""
    comparator = BackendComparator()
    return comparator.generate_test_documents(500, 350)


@pytest.fixture
def large_test_documents():
    """Large test dataset"""
    comparator = BackendComparator()
    return comparator.generate_test_documents(1000, 400)


@pytest.mark.comparison
class TestBackendComparison:
    """Comprehensive backend comparison tests"""
    
    def test_small_dataset_comparison(self, backend_comparator, small_test_documents):
        """Compare backends on small dataset (100 docs)"""
        results = backend_comparator.compare_backends(small_test_documents)
        
        # Validate results structure
        assert "lancedb" in results
        assert "parquet_faiss" in results
        assert "comparison" in results
        
        # Print results
        print(f"\n📊 SMALL DATASET COMPARISON RESULTS:")
        print(f"Documents: {len(small_test_documents)}")
        print(f"Overall Winner: {results['comparison']['winners']['overall']}")
        print(f"LanceDB Build Time: {results['lancedb'].get('build_time_seconds', 'N/A')}s")
        print(f"Parquet+FAISS Build Time: {results['parquet_faiss'].get('build_time_seconds', 'N/A')}s")
        
        # Store results for reporting
        backend_comparator.results["small_dataset"] = results
    
    def test_medium_dataset_comparison(self, backend_comparator, medium_test_documents):
        """Compare backends on medium dataset (500 docs)"""
        results = backend_comparator.compare_backends(medium_test_documents)
        
        print(f"\n📊 MEDIUM DATASET COMPARISON RESULTS:")
        print(f"Documents: {len(medium_test_documents)}")
        print(f"Overall Winner: {results['comparison']['winners']['overall']}")
        
        backend_comparator.results["medium_dataset"] = results
    
    def test_large_dataset_comparison(self, backend_comparator, large_test_documents):
        """Compare backends on large dataset (1000 docs)"""
        results = backend_comparator.compare_backends(large_test_documents)
        
        print(f"\n📊 LARGE DATASET COMPARISON RESULTS:")
        print(f"Documents: {len(large_test_documents)}")
        print(f"Overall Winner: {results['comparison']['winners']['overall']}")
        
        backend_comparator.results["large_dataset"] = results
    
    def test_generate_comparison_report(self, backend_comparator):
        """Generate comprehensive comparison report"""
        # This test should run after the dataset tests
        if not backend_comparator.results:
            pytest.skip("No comparison results available")
        
        report = self._generate_detailed_report(backend_comparator.results)
        
        # Save report to file
        with open("backend_comparison_results.json", "w") as f:
            json.dump(backend_comparator.results, f, indent=2)
        
        print(f"\n📋 COMPREHENSIVE COMPARISON REPORT GENERATED")
        print("Saved to: backend_comparison_results.json")
    
    def _generate_detailed_report(self, results: Dict) -> str:
        """Generate a detailed markdown report"""
        # This will be used by the publishing system
        return "Detailed comparison report generated"


# Standalone function for running comparisons
def run_backend_comparison():
    """Run complete backend comparison suite"""
    comparator = BackendComparator()
    
    print("🚀 Starting Comprehensive Backend Comparison: LanceDB vs Parquet+FAISS")
    print("=" * 80)
    
    all_results = {}
    
    for size in [100, 500, 1000]:
        print(f"\n📊 Testing with {size} documents...")
        documents = comparator.generate_test_documents(size)
        results = comparator.compare_backends(documents)
        all_results[f"{size}_docs"] = results
        
        # Print summary
        if "error" not in results["comparison"]:
            winner = results["comparison"]["winners"]["overall"]
            print(f"🏆 Winner for {size} docs: {winner.replace('_', '+').upper()}")
    
    # Save complete results
    with open("complete_backend_comparison.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("\n✅ Complete comparison saved to: complete_backend_comparison.json")
    return all_results


if __name__ == "__main__":
    run_backend_comparison() 