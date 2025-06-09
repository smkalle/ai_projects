"""
Large-scale benchmark tests for storage backend comparison
"""
import pytest
import time
import os
import tempfile
import shutil
import psutil
import gc
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import pandas as pd
from unittest.mock import patch

from storage_backends import ParquetFAISSBackend, create_backend
from text_processor import TextProcessor


class MockEmbeddingModel:
    """Mock embedding model for testing with configurable dimension"""
    def __init__(self, dimension=384):
        self.dimension = dimension
        np.random.seed(42)  # For reproducible tests
    
    def encode(self, texts, show_progress_bar=False, convert_to_numpy=True):
        """Generate mock embeddings"""
        embeddings = []
        for i, text in enumerate(texts):
            # Create deterministic embeddings based on text content and index
            text_hash = (hash(text) + i) % 1000000
            np.random.seed(text_hash)
            embedding = np.random.normal(0, 1, self.dimension).astype(np.float32)
            embeddings.append(embedding)
        
        if convert_to_numpy:
            return np.array(embeddings, dtype=np.float32)
        return embeddings


def generate_synthetic_documents(count: int, avg_length: int = 500) -> List[str]:
    """Generate synthetic documents of varying lengths for testing"""
    np.random.seed(42)  # For reproducible tests
    
    # Common words and phrases to create realistic-looking documents
    topics = [
        "artificial intelligence", "machine learning", "deep learning", "neural networks",
        "data science", "big data", "cloud computing", "software engineering",
        "database systems", "web development", "mobile apps", "cybersecurity",
        "blockchain", "quantum computing", "robotics", "internet of things"
    ]
    
    words = [
        "system", "data", "application", "service", "platform", "technology",
        "solution", "framework", "architecture", "implementation", "development",
        "analysis", "performance", "optimization", "scalability", "security",
        "integration", "deployment", "monitoring", "management", "configuration"
    ]
    
    documents = []
    for i in range(count):
        # Vary document length (50% to 150% of average)
        length = int(avg_length * (0.5 + np.random.random()))
        
        # Pick a random topic
        topic = np.random.choice(topics)
        
        # Generate document content
        content = f"Document {i+1}: This document discusses {topic}. "
        
        # Add random sentences
        while len(content) < length:
            sentence_words = np.random.choice(words, size=np.random.randint(5, 15))
            sentence = " ".join(sentence_words) + ". "
            content += sentence
        
        # Truncate to desired length
        content = content[:length]
        documents.append(content)
    
    return documents


def get_directory_size(path: str) -> int:
    """Get the total size of a directory in bytes"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def get_memory_usage() -> float:
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


class TestLargeScaleBenchmarks:
    """Large-scale benchmark tests for storage backends"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_dir = tempfile.mkdtemp(prefix="rag_benchmark_")
        self.original_paths = {}
        
        # Override storage paths for testing
        import storage_backends
        self.original_paths['FAISS_INDEX_PATH'] = storage_backends.FAISS_INDEX_PATH
        self.original_paths['PARQUET_PATH'] = storage_backends.PARQUET_PATH
        
        storage_backends.FAISS_INDEX_PATH = os.path.join(self.test_dir, "test_faiss.index")
        storage_backends.PARQUET_PATH = os.path.join(self.test_dir, "test_documents.parquet")
        
        self.embedding_model = MockEmbeddingModel()
        self.text_processor = TextProcessor()
    
    def teardown_method(self):
        """Cleanup after each test method"""
        # Restore original paths
        import storage_backends
        for key, value in self.original_paths.items():
            setattr(storage_backends, key, value)
        
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        # Force garbage collection
        gc.collect()
    
    @pytest.mark.benchmark
    @pytest.mark.parametrize("doc_count,avg_length", [
        (1000, 300),    # 1K short documents
        (1000, 1000),   # 1K medium documents
        (5000, 500),    # 5K documents
        (10000, 400),   # 10K documents
    ])
    def test_scalability_benchmark(self, doc_count: int, avg_length: int):
        """Comprehensive scalability benchmark test"""
        print(f"\n{'='*60}")
        print(f"🚀 BENCHMARK: {doc_count:,} documents, avg {avg_length} chars")
        print(f"{'='*60}")
        
        # Generate test documents
        print(f"📝 Generating {doc_count:,} synthetic documents...")
        start_time = time.time()
        documents = generate_synthetic_documents(doc_count, avg_length)
        generation_time = time.time() - start_time
        
        # Calculate document statistics
        doc_lengths = [len(doc) for doc in documents]
        total_chars = sum(doc_lengths)
        avg_doc_length = total_chars / len(documents)
        
        print(f"   Generated in {generation_time:.2f}s")
        print(f"   Total characters: {total_chars:,}")
        print(f"   Average document length: {avg_doc_length:.0f} chars")
        print(f"   Min/Max length: {min(doc_lengths)}/{max(doc_lengths)} chars")
        
        # Process documents into chunks
        print(f"\n🔄 Processing documents into chunks...")
        start_time = time.time()
        all_chunks = []
        for i, doc in enumerate(documents):
            chunks = self.text_processor.process_text(doc, f"doc_{i}")
            all_chunks.extend(chunks)
        processing_time = time.time() - start_time
        
        chunk_lengths = [len(chunk) for chunk in all_chunks]
        print(f"   Processed in {processing_time:.2f}s")
        print(f"   Total chunks: {len(all_chunks):,}")
        print(f"   Average chunks per document: {len(all_chunks)/len(documents):.1f}")
        print(f"   Average chunk length: {sum(chunk_lengths)/len(chunk_lengths):.0f} chars")
        
        # Test Parquet+FAISS backend
        results = self._benchmark_backend("parquet_faiss", all_chunks, doc_count)
        
        # Print comprehensive results
        self._print_benchmark_results(results, doc_count, total_chars)
        
        # Verify functionality
        assert results['build_success'] is True
        assert results['search_results'] > 0
        assert results['build_time'] > 0
        assert results['search_time'] >= 0
    
    def _benchmark_backend(self, backend_type: str, chunks: List[str], doc_count: int) -> Dict[str, Any]:
        """Benchmark a specific backend"""
        print(f"\n🧪 Testing {backend_type.upper()} backend...")
        
        # Initialize backend
        backend = create_backend(backend_type, self.embedding_model)
        
        # Measure memory before indexing
        memory_before = get_memory_usage()
        
        # Build index
        print(f"   🏗️  Building index for {len(chunks):,} chunks...")
        start_time = time.time()
        build_success = backend.build_index(chunks)
        build_time = time.time() - start_time
        
        # Measure memory after indexing
        memory_after = get_memory_usage()
        memory_used = memory_after - memory_before
        
        # Measure storage size
        storage_size = get_directory_size(self.test_dir)
        
        print(f"   ✅ Index built in {build_time:.2f}s")
        print(f"   💾 Storage size: {storage_size / 1024 / 1024:.1f} MB")
        print(f"   🧠 Memory used: {memory_used:.1f} MB")
        
        # Test search performance with multiple queries
        search_queries = [
            "artificial intelligence and machine learning",
            "data science and analytics",
            "software development best practices",
            "system architecture and design",
            "performance optimization techniques"
        ]
        
        print(f"   🔍 Testing search performance...")
        search_times = []
        total_results = 0
        
        for query in search_queries:
            start_time = time.time()
            results = backend.search(query, top_k=10)
            search_time = time.time() - start_time
            search_times.append(search_time)
            total_results += len(results)
        
        avg_search_time = sum(search_times) / len(search_times)
        avg_results = total_results / len(search_queries)
        
        print(f"   ⚡ Average search time: {avg_search_time*1000:.2f}ms")
        print(f"   📊 Average results per query: {avg_results:.1f}")
        
        # Get index info
        index_info = backend.get_index_info()
        
        return {
            'backend_type': backend_type,
            'build_success': build_success,
            'build_time': build_time,
            'search_time': avg_search_time,
            'search_results': avg_results,
            'storage_size_mb': storage_size / 1024 / 1024,
            'memory_used_mb': memory_used,
            'chunk_count': len(chunks),
            'index_info': index_info,
            'search_times': search_times
        }
    
    def _print_benchmark_results(self, results: Dict[str, Any], doc_count: int, total_chars: int):
        """Print formatted benchmark results"""
        print(f"\n📊 BENCHMARK RESULTS SUMMARY")
        print(f"{'='*60}")
        
        # Calculate efficiency metrics
        chars_per_mb = total_chars / results['storage_size_mb'] if results['storage_size_mb'] > 0 else 0
        docs_per_second = doc_count / results['build_time'] if results['build_time'] > 0 else 0
        throughput_mb_per_sec = (total_chars / 1024 / 1024) / results['build_time'] if results['build_time'] > 0 else 0
        
        print(f"📈 Performance Metrics:")
        print(f"   Build Time: {results['build_time']:.2f}s")
        print(f"   Search Time: {results['search_time']*1000:.2f}ms per query")
        print(f"   Throughput: {docs_per_second:.0f} docs/sec")
        print(f"   Data Rate: {throughput_mb_per_sec:.1f} MB/sec")
        
        print(f"\n💾 Storage Metrics:")
        print(f"   Total Size: {results['storage_size_mb']:.1f} MB")
        print(f"   Compression: {chars_per_mb:.0f} chars/MB")
        print(f"   Memory Used: {results['memory_used_mb']:.1f} MB")
        
        print(f"\n🎯 Quality Metrics:")
        print(f"   Chunks Indexed: {results['chunk_count']:,}")
        print(f"   Search Success: {results['search_results']:.1f} results/query")
        print(f"   Index Status: {results['index_info'].get('status', 'unknown')}")
        
        # Performance rating
        if results['search_time'] < 0.001:
            search_rating = "🚀 Excellent"
        elif results['search_time'] < 0.01:
            search_rating = "⚡ Good"
        else:
            search_rating = "🐢 Needs improvement"
        
        print(f"\n🏆 Overall Rating:")
        print(f"   Search Performance: {search_rating}")
        print(f"   Storage Efficiency: {'🎯 Excellent' if chars_per_mb > 1000000 else '📊 Good'}")
        
    @pytest.mark.benchmark
    def test_memory_stress_test(self):
        """Test memory usage under stress"""
        print(f"\n🧠 MEMORY STRESS TEST")
        print(f"{'='*60}")
        
        # Generate progressively larger datasets
        sizes = [1000, 5000, 10000]
        memory_usage = []
        
        for size in sizes:
            print(f"\n📊 Testing with {size:,} documents...")
            
            # Generate documents
            documents = generate_synthetic_documents(size, 400)
            
            # Process into chunks
            all_chunks = []
            for i, doc in enumerate(documents):
                chunks = self.text_processor.process_text(doc, f"doc_{i}")
                all_chunks.extend(chunks)
            
            # Measure memory usage during indexing
            memory_before = get_memory_usage()
            
            backend = create_backend("parquet_faiss", self.embedding_model)
            backend.build_index(all_chunks)
            
            memory_after = get_memory_usage()
            memory_used = memory_after - memory_before
            memory_usage.append(memory_used)
            
            print(f"   Memory used: {memory_used:.1f} MB")
            print(f"   Memory per document: {memory_used/size:.3f} MB")
            print(f"   Memory per chunk: {memory_used/len(all_chunks):.3f} MB")
            
            # Cleanup for next iteration
            del backend, all_chunks, documents
            gc.collect()
        
        # Analyze memory scaling
        print(f"\n📈 Memory Scaling Analysis:")
        for i, (size, memory) in enumerate(zip(sizes, memory_usage)):
            if i > 0:
                ratio = memory / memory_usage[0]
                size_ratio = size / sizes[0]
                efficiency = ratio / size_ratio
                print(f"   {size:,} docs: {memory:.1f} MB (efficiency: {efficiency:.2f})")
            else:
                print(f"   {size:,} docs: {memory:.1f} MB (baseline)")
        
        # Memory usage should scale reasonably (not more than 2x per size increase)
        for i in range(1, len(memory_usage)):
            ratio = memory_usage[i] / memory_usage[i-1]
            size_ratio = sizes[i] / sizes[i-1]
            assert ratio / size_ratio < 2.0, f"Memory usage scaling too poorly: {ratio/size_ratio:.2f}x" 