#!/usr/bin/env python3
"""
Comprehensive Embedding Model Comparison Tests
Systematically compares multiple embedding models across various metrics
"""

import pytest
import time
import psutil
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import json
from datetime import datetime
from pathlib import Path

# Import our configuration and models
try:
    from config import (
        get_available_embedding_models, 
        get_embedding_model_info, 
        EMBEDDING_DEVICE
    )
    from tests.test_backend_comparison import MockEmbeddingModel, BackendComparator
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Test documents for comparison
TEST_DOCUMENTS = [
    "Artificial intelligence is revolutionizing the way we work and live.",
    "Machine learning algorithms can process vast amounts of data to identify patterns.",
    "Natural language processing enables computers to understand human language.",
    "Deep learning neural networks are inspired by the structure of the human brain.",
    "Computer vision allows machines to interpret and analyze visual information.",
    "Reinforcement learning teaches agents to make decisions through trial and error.",
    "The transformer architecture has become fundamental in modern NLP applications.",
    "Generative AI models can create new content including text, images, and code.",
    "Large language models demonstrate emergent capabilities at scale.",
    "Vector databases enable efficient similarity search for AI applications."
]

# Multilingual test documents
MULTILINGUAL_DOCUMENTS = [
    "Hello, how are you today?",  # English
    "Bonjour, comment allez-vous?",  # French
    "Hola, ¿cómo estás?",  # Spanish
    "Guten Tag, wie geht es Ihnen?",  # German
    "你好，你今天怎么样？",  # Chinese
    "こんにちは、元気ですか？",  # Japanese
    "안녕하세요, 어떻게 지내세요?",  # Korean
    "Привет, как дела?",  # Russian
    "مرحبا، كيف حالك؟",  # Arabic
    "नमस्ते, आप कैसे हैं?",  # Hindi
]

class EmbeddingModelComparator:
    """Comprehensive embedding model comparison suite"""
    
    def __init__(self):
        self.results = {}
        self.test_documents = TEST_DOCUMENTS + MULTILINGUAL_DOCUMENTS
        self.process = psutil.Process(os.getpid())
        
    def measure_performance(self, model, model_name: str, documents: List[str]) -> Dict[str, Any]:
        """Measure comprehensive performance metrics for an embedding model"""
        
        print(f"\n🔍 Testing {model_name}...")
        
        # Memory before loading
        memory_before = self.process.memory_info().rss / 1024 / 1024
        
        # Test embedding generation
        start_time = time.time()
        
        try:
            if hasattr(model, 'encode'):
                # Real SentenceTransformer model
                embeddings = model.encode(documents, show_progress_bar=False)
                model_type = "real"
            else:
                # Mock model
                embeddings = np.array([model.encode(doc) for doc in documents])
                model_type = "mock"
                
            encoding_time = time.time() - start_time
            
            # Memory after encoding
            memory_after = self.process.memory_info().rss / 1024 / 1024
            memory_usage = memory_after - memory_before
            
            # Calculate metrics
            embedding_dim = embeddings.shape[1] if len(embeddings.shape) > 1 else len(embeddings[0])
            docs_per_second = len(documents) / encoding_time if encoding_time > 0 else float('inf')
            avg_time_per_doc = encoding_time / len(documents) if len(documents) > 0 else 0
            
            # Quality metrics (for real embeddings)
            quality_metrics = {}
            if model_type == "real" and len(embeddings) > 1:
                # Calculate embedding diversity (average cosine distance)
                from sklearn.metrics.pairwise import cosine_similarity
                similarity_matrix = cosine_similarity(embeddings)
                # Average similarity excluding diagonal
                mask = np.eye(similarity_matrix.shape[0], dtype=bool)
                avg_similarity = similarity_matrix[~mask].mean()
                quality_metrics['avg_cosine_similarity'] = float(avg_similarity)
                quality_metrics['embedding_diversity'] = float(1 - avg_similarity)
                
                # Standard deviation of embedding values (measure of expressiveness)
                quality_metrics['embedding_std'] = float(np.std(embeddings))
                quality_metrics['embedding_norm_avg'] = float(np.linalg.norm(embeddings, axis=1).mean())
            
            return {
                'model_name': model_name,
                'model_type': model_type,
                'encoding_time': encoding_time,
                'docs_per_second': docs_per_second,
                'avg_time_per_doc': avg_time_per_doc,
                'memory_usage_mb': memory_usage,
                'embedding_dimension': embedding_dim,
                'num_documents': len(documents),
                'success': True,
                'error': None,
                'quality_metrics': quality_metrics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'model_name': model_name,
                'model_type': 'failed',
                'encoding_time': None,
                'docs_per_second': 0,
                'avg_time_per_doc': None,
                'memory_usage_mb': 0,
                'embedding_dimension': None,
                'num_documents': len(documents),
                'success': False,
                'error': str(e),
                'quality_metrics': {},
                'timestamp': datetime.now().isoformat()
            }
    
    def compare_all_models(self, use_real_embeddings: bool = True) -> Dict[str, Any]:
        """Compare all available embedding models"""
        
        if not CONFIG_AVAILABLE:
            print("⚠️ Config not available, using mock comparison")
            return self.compare_mock_models()
        
        available_models = get_available_embedding_models()
        comparison_results = {}
        
        print(f"🚀 Starting comparison of {len(available_models)} embedding models...")
        print(f"📄 Test documents: {len(self.test_documents)}")
        print(f"🖥️ Device: {EMBEDDING_DEVICE}")
        print(f"⚡ Real embeddings: {use_real_embeddings}")
        
        for i, model_name in enumerate(available_models):
            print(f"\n{'='*50}")
            print(f"📊 Progress: {i+1}/{len(available_models)}")
            
            model_info = get_embedding_model_info(model_name)
            print(f"🔧 Model: {model_info['name']}")
            print(f"📐 Dimensions: {model_info['dimensions']}")
            print(f"💾 Size: {model_info['size_mb']}MB")
            
            if use_real_embeddings:
                try:
                    from sentence_transformers import SentenceTransformer
                    model = SentenceTransformer(model_name, device=EMBEDDING_DEVICE)
                    print(f"✅ Loaded real model: {model_name}")
                except Exception as e:
                    print(f"❌ Failed to load {model_name}: {e}")
                    print(f"🔄 Falling back to mock model")
                    model = MockEmbeddingModel(model_info.get('dimensions', 384))
            else:
                model = MockEmbeddingModel(model_info.get('dimensions', 384))
                print(f"🎭 Using mock model")
            
            # Run performance test
            result = self.measure_performance(model, model_name, self.test_documents)
            result['model_info'] = model_info
            comparison_results[model_name] = result
            
            # Cleanup memory
            if use_real_embeddings and hasattr(model, 'to'):
                try:
                    del model
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except:
                    pass
        
        return comparison_results
    
    def compare_mock_models(self) -> Dict[str, Any]:
        """Fallback comparison using mock models"""
        mock_models = {
            'small_model': MockEmbeddingModel(384),
            'medium_model': MockEmbeddingModel(768),
            'large_model': MockEmbeddingModel(1024),
        }
        
        comparison_results = {}
        
        for model_name, model in mock_models.items():
            result = self.measure_performance(model, model_name, self.test_documents)
            result['model_info'] = {
                'name': model_name,
                'dimensions': model.embedding_dim,
                'size_mb': model.embedding_dim * 0.01,  # Rough estimate
                'speed': 'fast',
                'quality': 'mock',
                'languages': ['en'],
                'use_case': 'testing'
            }
            comparison_results[model_name] = result
        
        return comparison_results
    
    def generate_comparison_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive comparison report"""
        
        successful_results = {k: v for k, v in results.items() if v['success']}
        failed_results = {k: v for k, v in results.items() if not v['success']}
        
        report = []
        report.append("# 🚀 Embedding Model Comparison Report")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Test Documents:** {len(self.test_documents)}")
        report.append(f"**Successful Models:** {len(successful_results)}")
        report.append(f"**Failed Models:** {len(failed_results)}")
        report.append("")
        
        if successful_results:
            # Performance ranking
            report.append("## 🏆 Performance Rankings")
            report.append("")
            
            # Sort by docs per second
            speed_ranking = sorted(successful_results.items(), 
                                 key=lambda x: x[1]['docs_per_second'], reverse=True)
            
            report.append("### ⚡ Speed Ranking (docs/second)")
            for i, (model_name, result) in enumerate(speed_ranking):
                report.append(f"{i+1}. **{result['model_info']['name']}**: {result['docs_per_second']:.1f} docs/sec")
            report.append("")
            
            # Memory efficiency ranking
            memory_ranking = sorted(successful_results.items(), 
                                  key=lambda x: x[1]['memory_usage_mb'])
            
            report.append("### 💾 Memory Efficiency Ranking")
            for i, (model_name, result) in enumerate(memory_ranking):
                report.append(f"{i+1}. **{result['model_info']['name']}**: {result['memory_usage_mb']:.1f} MB")
            report.append("")
            
            # Detailed comparison table
            report.append("## 📊 Detailed Comparison")
            report.append("")
            report.append("| Model | Dimensions | Speed (docs/sec) | Memory (MB) | Avg Time/Doc (ms) | Type |")
            report.append("|-------|------------|------------------|-------------|-------------------|------|")
            
            for model_name, result in successful_results.items():
                name = result['model_info']['name']
                dims = result['embedding_dimension']
                speed = f"{result['docs_per_second']:.1f}"
                memory = f"{result['memory_usage_mb']:.1f}"
                avg_time = f"{result['avg_time_per_doc']*1000:.1f}" if result['avg_time_per_doc'] else "N/A"
                model_type = result['model_type']
                
                report.append(f"| {name} | {dims} | {speed} | {memory} | {avg_time} | {model_type} |")
            
            report.append("")
            
            # Quality metrics (if available)
            quality_results = {k: v for k, v in successful_results.items() 
                             if v['quality_metrics']}
            
            if quality_results:
                report.append("## 🎯 Quality Metrics (Real Models Only)")
                report.append("")
                report.append("| Model | Diversity | Avg Similarity | Std Dev | Avg Norm |")
                report.append("|-------|-----------|----------------|---------|----------|")
                
                for model_name, result in quality_results.items():
                    name = result['model_info']['name']
                    metrics = result['quality_metrics']
                    diversity = f"{metrics.get('embedding_diversity', 0):.3f}"
                    similarity = f"{metrics.get('avg_cosine_similarity', 0):.3f}"
                    std_dev = f"{metrics.get('embedding_std', 0):.3f}"
                    avg_norm = f"{metrics.get('embedding_norm_avg', 0):.3f}"
                    
                    report.append(f"| {name} | {diversity} | {similarity} | {std_dev} | {avg_norm} |")
                
                report.append("")
        
        # Failed models
        if failed_results:
            report.append("## ❌ Failed Models")
            report.append("")
            for model_name, result in failed_results.items():
                report.append(f"- **{model_name}**: {result['error']}")
            report.append("")
        
        # Recommendations
        report.append("## 💡 Recommendations")
        report.append("")
        
        if successful_results:
            fastest_model = max(successful_results.items(), key=lambda x: x[1]['docs_per_second'])
            most_efficient = min(successful_results.items(), key=lambda x: x[1]['memory_usage_mb'])
            
            report.append(f"- **Fastest Model**: {fastest_model[1]['model_info']['name']} ({fastest_model[1]['docs_per_second']:.1f} docs/sec)")
            report.append(f"- **Most Memory Efficient**: {most_efficient[1]['model_info']['name']} ({most_efficient[1]['memory_usage_mb']:.1f} MB)")
            
            # Find balanced option
            if len(successful_results) > 2:
                # Score based on normalized speed and inverse memory usage
                def balance_score(result):
                    fastest_speed = fastest_model[1]['docs_per_second']
                    most_efficient_memory = most_efficient[1]['memory_usage_mb']
                    
                    # Avoid division by zero
                    if fastest_speed == 0:
                        speed_norm = 0
                    else:
                        speed_norm = result['docs_per_second'] / fastest_speed
                    
                    if result['memory_usage_mb'] == 0:
                        memory_norm = 1
                    else:
                        memory_norm = most_efficient_memory / result['memory_usage_mb']
                    
                    return (speed_norm + memory_norm) / 2
                
                balanced_model = max(successful_results.items(), key=lambda x: balance_score(x[1]))
                report.append(f"- **Best Balance**: {balanced_model[1]['model_info']['name']} (speed + efficiency)")
        
        return "\n".join(report)
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"embedding_comparison_{timestamp}.json"
        
        output_dir = Path("test_results")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {filepath}")
        return filepath


# Test functions
def test_embedding_model_comparison_mock():
    """Test embedding model comparison with mock models"""
    comparator = EmbeddingModelComparator()
    results = comparator.compare_all_models(use_real_embeddings=False)
    
    assert len(results) > 0, "Should have comparison results"
    
    for model_name, result in results.items():
        assert 'encoding_time' in result
        assert 'docs_per_second' in result
        assert 'memory_usage_mb' in result
        assert 'embedding_dimension' in result
        
    print("✅ Mock embedding comparison test passed")

@pytest.mark.skipif(not CONFIG_AVAILABLE, reason="Config not available")
def test_embedding_model_comparison_real():
    """Test embedding model comparison with real models (if available)"""
    try:
        import sentence_transformers
        comparator = EmbeddingModelComparator()
        results = comparator.compare_all_models(use_real_embeddings=True)
        
        assert len(results) > 0, "Should have comparison results"
        
        # Generate and save report
        report = comparator.generate_comparison_report(results)
        assert len(report) > 0, "Should generate a report"
        
        comparator.save_results(results)
        
        print("✅ Real embedding comparison test passed")
        print(f"📊 Tested {len(results)} models")
        
    except ImportError:
        pytest.skip("sentence-transformers not available")

def test_multilingual_comparison():
    """Test embedding models specifically on multilingual content"""
    if not CONFIG_AVAILABLE:
        pytest.skip("Config not available")
    
    comparator = EmbeddingModelComparator()
    comparator.test_documents = MULTILINGUAL_DOCUMENTS
    
    # Test with mock models for speed
    results = comparator.compare_all_models(use_real_embeddings=False)
    
    assert len(results) > 0, "Should have multilingual results"
    
    # Check that all models handled multilingual content
    for model_name, result in results.items():
        assert result['num_documents'] == len(MULTILINGUAL_DOCUMENTS)
    
    print("✅ Multilingual comparison test passed")

def run_comprehensive_comparison():
    """Run a comprehensive comparison and generate full report"""
    print("🚀 Starting Comprehensive Embedding Model Comparison")
    print("="*60)
    
    comparator = EmbeddingModelComparator()
    
    # Run comparison
    results = comparator.compare_all_models(use_real_embeddings=True)
    
    # Generate report
    report = comparator.generate_comparison_report(results)
    print("\n" + report)
    
    # Save results
    filepath = comparator.save_results(results)
    
    # Save report
    report_path = filepath.parent / f"report_{filepath.stem}.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"📄 Report saved to: {report_path}")
    
    return results, report

if __name__ == "__main__":
    # Run comprehensive comparison
    results, report = run_comprehensive_comparison() 