#!/usr/bin/env python3
"""
Embedding Model Comparison Runner
Easy-to-use script for running comprehensive embedding model comparisons
"""

import sys
import argparse
import time
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run comprehensive embedding model comparisons")
    parser.add_argument("--real", action="store_true", help="Use real embedding models (slower)")
    parser.add_argument("--mock", action="store_true", help="Use mock models for fast testing")
    parser.add_argument("--multilingual", action="store_true", help="Test multilingual capabilities")
    parser.add_argument("--models", nargs="+", help="Specific models to test")
    parser.add_argument("--output", type=str, help="Output file prefix")
    parser.add_argument("--quick", action="store_true", help="Quick test with fewer documents")
    
    args = parser.parse_args()
    
    # Default to mock if nothing specified
    if not args.real and not args.mock:
        args.mock = True
    
    print("🚀 Embedding Model Comparison Runner")
    print("="*50)
    
    try:
        from tests.test_embedding_comparison import EmbeddingModelComparator, MULTILINGUAL_DOCUMENTS, TEST_DOCUMENTS
        
        comparator = EmbeddingModelComparator()
        
        # Configure test documents
        if args.multilingual:
            comparator.test_documents = MULTILINGUAL_DOCUMENTS
            print(f"🌍 Testing multilingual capabilities with {len(MULTILINGUAL_DOCUMENTS)} documents")
        elif args.quick:
            comparator.test_documents = TEST_DOCUMENTS[:5]  # Just first 5 for quick testing
            print(f"⚡ Quick test with {len(comparator.test_documents)} documents")
        else:
            comparator.test_documents = TEST_DOCUMENTS + MULTILINGUAL_DOCUMENTS
            print(f"📄 Full test with {len(comparator.test_documents)} documents")
        
        # Run comparison
        if args.real:
            print("🔄 Running with REAL embedding models...")
            print("⚠️  This may take several minutes and require significant memory")
            
            # Ask for confirmation
            if not sys.stdin.isatty():  # Running in non-interactive mode
                confirm = 'y'
            else:
                confirm = input("Continue? (y/N): ").lower().strip()
                
            if confirm != 'y':
                print("❌ Cancelled by user")
                return
            
            results = comparator.compare_all_models(use_real_embeddings=True)
        else:
            print("🎭 Running with mock embedding models (fast testing)")
            results = comparator.compare_all_models(use_real_embeddings=False)
        
        # Generate report
        print("\n" + "="*50)
        print("📊 COMPARISON RESULTS")
        print("="*50)
        
        report = comparator.generate_comparison_report(results)
        print(report)
        
        # Save results
        output_prefix = args.output or f"embedding_comparison_{int(time.time())}"
        
        # Save JSON results
        json_path = comparator.save_results(results, f"{output_prefix}.json")
        
        # Save markdown report
        report_path = json_path.parent / f"{output_prefix}_report.md"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_path}")
        
        # Summary
        print(f"\n✅ Comparison completed successfully!")
        print(f"📊 Models tested: {len(results)}")
        successful = sum(1 for r in results.values() if r['success'])
        print(f"✅ Successful: {successful}")
        failed = len(results) - successful
        if failed > 0:
            print(f"❌ Failed: {failed}")
        
        return results
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return None
    
    except Exception as e:
        print(f"❌ Error during comparison: {e}")
        print("💡 Try running with --mock for basic testing")
        return None

def run_quick_test():
    """Run a quick test to verify everything works"""
    print("🧪 Running Quick Test")
    print("-" * 30)
    
    try:
        from tests.test_embedding_comparison import EmbeddingModelComparator
        
        comparator = EmbeddingModelComparator()
        comparator.test_documents = ["Hello world", "Test document", "AI is amazing"]
        
        results = comparator.compare_all_models(use_real_embeddings=False)
        
        if results:
            print("✅ Quick test passed!")
            print(f"📊 Tested {len(results)} models")
            for model_name, result in results.items():
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {model_name}: {result.get('docs_per_second', 0):.1f} docs/sec")
        else:
            print("❌ Quick test failed - no results")
            
    except Exception as e:
        print(f"❌ Quick test failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments, show help and run quick test
        print("🧪 No arguments provided, running quick test...")
        run_quick_test()
        print("\n" + "="*50)
        print("💡 Usage examples:")
        print("  python run_embedding_comparison.py --mock          # Fast mock testing")
        print("  python run_embedding_comparison.py --real          # Real model testing")
        print("  python run_embedding_comparison.py --multilingual  # Test multilingual")
        print("  python run_embedding_comparison.py --quick --real  # Quick real test")
        print("  python run_embedding_comparison.py --help          # Show all options")
    else:
        main() 