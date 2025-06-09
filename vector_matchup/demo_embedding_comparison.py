#!/usr/bin/env python3
"""
Demo: Embedding Model Comparison
Demonstrates how to use the comprehensive embedding model comparison system
"""

def demo_quick_comparison():
    """Quick demonstration of embedding model comparison"""
    print("🚀 Demo: Quick Embedding Model Comparison")
    print("="*50)
    
    try:
        from tests.test_embedding_comparison import EmbeddingModelComparator
        
        # Create comparator
        comparator = EmbeddingModelComparator()
        
        # Use smaller test set for demo
        demo_docs = [
            "Machine learning is transforming industries.",
            "AI models process natural language effectively.", 
            "Vector databases enable similarity search.",
            "Deep learning neural networks are powerful.",
            "Transformer architectures revolutionized NLP."
        ]
        
        comparator.test_documents = demo_docs
        
        print(f"📄 Testing with {len(demo_docs)} documents")
        print("🎭 Using mock models for fast demonstration")
        
        # Run comparison
        results = comparator.compare_all_models(use_real_embeddings=False)
        
        # Show top 3 fastest models
        successful = {k: v for k, v in results.items() if v['success']}
        fastest = sorted(successful.items(), key=lambda x: x[1]['docs_per_second'], reverse=True)
        
        print("\n🏆 Top 3 Fastest Models:")
        for i, (model_name, result) in enumerate(fastest[:3]):
            print(f"{i+1}. {result['model_info']['name']}: {result['docs_per_second']:.1f} docs/sec")
        
        # Most efficient
        most_efficient = min(successful.items(), key=lambda x: x[1]['memory_usage_mb'])
        print(f"\n💾 Most Memory Efficient: {most_efficient[1]['model_info']['name']} ({most_efficient[1]['memory_usage_mb']:.1f} MB)")
        
        return results
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return None

def demo_multilingual_focus():
    """Demonstrate multilingual model comparison"""
    print("\n🌍 Demo: Multilingual Model Focus")
    print("="*50)
    
    try:
        from tests.test_embedding_comparison import EmbeddingModelComparator, MULTILINGUAL_DOCUMENTS
        
        comparator = EmbeddingModelComparator()
        
        # Focus on multilingual documents
        multilingual_subset = MULTILINGUAL_DOCUMENTS[:6]  # First 6 languages
        comparator.test_documents = multilingual_subset
        
        print(f"🌐 Testing {len(multilingual_subset)} multilingual documents:")
        for doc in multilingual_subset:
            print(f"   • {doc}")
        
        # Run comparison
        results = comparator.compare_all_models(use_real_embeddings=False)
        
        # Focus on multilingual models
        multilingual_models = []
        for model_name, result in results.items():
            if result['success']:
                languages = result['model_info']['languages']
                if len(languages) > 1 or 'multilingual' in languages:
                    multilingual_models.append((model_name, result))
        
        print(f"\n🎯 Found {len(multilingual_models)} multilingual-capable models:")
        for model_name, result in multilingual_models:
            langs = result['model_info']['languages']
            lang_str = ', '.join(langs[:3])
            if len(langs) > 3:
                lang_str += f" +{len(langs) - 3} more"
            print(f"   • {result['model_info']['name']}: {lang_str}")
        
        return results
        
    except Exception as e:
        print(f"❌ Multilingual demo failed: {e}")
        return None

def demo_custom_comparison():
    """Demonstrate custom comparison with specific criteria"""
    print("\n🎯 Demo: Custom Comparison Analysis")
    print("="*50)
    
    try:
        from tests.test_embedding_comparison import EmbeddingModelComparator
        
        comparator = EmbeddingModelComparator()
        
        # Custom test documents for specific domain
        ai_docs = [
            "Neural networks learn complex patterns from data.",
            "Attention mechanisms focus on relevant information.",
            "Gradient descent optimizes model parameters.",
            "Backpropagation updates network weights.",
            "Overfitting occurs when models memorize training data."
        ]
        
        comparator.test_documents = ai_docs
        
        print(f"🧠 Testing AI/ML domain with {len(ai_docs)} documents")
        
        # Run comparison
        results = comparator.compare_all_models(use_real_embeddings=False)
        
        # Analyze by model size categories
        small_models = []
        medium_models = []
        large_models = []
        
        for model_name, result in results.items():
            if result['success']:
                dims = result['embedding_dimension']
                if dims <= 400:
                    small_models.append((model_name, result))
                elif dims <= 800:
                    medium_models.append((model_name, result))
                else:
                    large_models.append((model_name, result))
        
        print(f"\n📊 Model Categories:")
        print(f"   🔹 Small (≤400 dims): {len(small_models)} models")
        print(f"   🔸 Medium (401-800 dims): {len(medium_models)} models") 
        print(f"   🔶 Large (>800 dims): {len(large_models)} models")
        
        # Best in each category
        if small_models:
            best_small = max(small_models, key=lambda x: x[1]['docs_per_second'])
            print(f"   🏆 Best Small: {best_small[1]['model_info']['name']} ({best_small[1]['docs_per_second']:.1f} docs/sec)")
        
        if medium_models:
            best_medium = max(medium_models, key=lambda x: x[1]['docs_per_second'])
            print(f"   🏆 Best Medium: {best_medium[1]['model_info']['name']} ({best_medium[1]['docs_per_second']:.1f} docs/sec)")
        
        if large_models:
            best_large = max(large_models, key=lambda x: x[1]['docs_per_second'])
            print(f"   🏆 Best Large: {best_large[1]['model_info']['name']} ({best_large[1]['docs_per_second']:.1f} docs/sec)")
        
        return results
        
    except Exception as e:
        print(f"❌ Custom demo failed: {e}")
        return None

def demo_report_generation():
    """Demonstrate report generation and saving"""
    print("\n📊 Demo: Report Generation")
    print("="*50)
    
    try:
        from tests.test_embedding_comparison import EmbeddingModelComparator
        
        comparator = EmbeddingModelComparator()
        
        # Quick test for report demo
        comparator.test_documents = ["Test document for report generation."]
        
        print("📋 Generating comprehensive comparison report...")
        
        # Run comparison
        results = comparator.compare_all_models(use_real_embeddings=False)
        
        # Generate report
        report = comparator.generate_comparison_report(results)
        
        # Show report structure
        lines = report.split('\n')
        print("\n📄 Generated Report Structure:")
        section_headers = [line for line in lines if line.startswith('#')]
        for header in section_headers[:8]:  # Show first 8 sections
            print(f"   {header}")
        
        if len(section_headers) > 8:
            print(f"   ... and {len(section_headers) - 8} more sections")
        
        # Save results
        filepath = comparator.save_results(results, "demo_comparison.json")
        print(f"\n💾 Results saved to: {filepath}")
        
        # Save report  
        report_path = filepath.parent / "demo_comparison_report.md"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_path}")
        
        return results, report
        
    except Exception as e:
        print(f"❌ Report demo failed: {e}")
        return None, None

def main():
    """Run all embedding comparison demos"""
    print("🧪 Embedding Model Comparison Demo Suite")
    print("="*60)
    print("This demo showcases the comprehensive embedding model")
    print("comparison capabilities built into Vector Matchup Pro.")
    print()
    
    # Run demos
    demo_quick_comparison()
    demo_multilingual_focus()
    demo_custom_comparison()
    results, report = demo_report_generation()
    
    print("\n✅ Demo Suite Completed!")
    print("="*60)
    print("\n💡 Next Steps:")
    print("1. Run with real models: python run_embedding_comparison.py --real")
    print("2. Test multilingual: python run_embedding_comparison.py --multilingual")
    print("3. Quick test: python run_embedding_comparison.py --quick")
    print("4. Use in Streamlit app: Check the sidebar for dynamic model selection")
    print("\n🎯 The embedding comparison system provides:")
    print("   • Performance benchmarking (speed, memory)")
    print("   • Quality metrics (diversity, similarity)")
    print("   • Multilingual testing capabilities")
    print("   • Comprehensive reporting (JSON + Markdown)")
    print("   • Integration with Vector Matchup Pro interface")
    
    return results

if __name__ == "__main__":
    main() 