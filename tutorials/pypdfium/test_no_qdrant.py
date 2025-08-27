#!/usr/bin/env python3
"""
Test script to verify system works gracefully without Qdrant
"""

import sys
import os
sys.path.append('app')

def test_rag_system():
    """Test RAG system without Qdrant"""
    print("🧪 Testing RAG System without Qdrant...")
    
    try:
        from models.rag_system import EnergyRAGSystem
        
        # Initialize without API key
        rag = EnergyRAGSystem(
            qdrant_url="localhost",
            qdrant_port=6333,
            openai_api_key=None
        )
        
        status = rag.get_status()
        print(f"✓ RAG system initialized")
        print(f"  - Qdrant available: {status['qdrant_available']}")
        print(f"  - Embeddings available: {status['embeddings_available']}")
        print(f"  - Fully operational: {status['fully_operational']}")
        
        # Test document stats
        stats = rag.get_document_stats()
        print(f"✓ Document stats retrieved: {stats}")
        
        # Test similarity search (should return empty)
        results = rag.similarity_search("test query")
        print(f"✓ Search handled gracefully: {len(results)} results")
        
        # Test document processing (should return chunk count but not store)
        chunks = rag.process_and_store_document(
            text="This is a test document with some content.",
            document_name="test.pdf",
            document_type="energy"
        )
        print(f"✓ Document processing handled: {chunks} chunks processed")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        return False

def test_ui_components():
    """Test UI components can handle missing dependencies"""
    print("\n🎨 Testing UI Components...")
    
    try:
        from utils.config import settings
        print(f"✓ Config loaded: {settings.app_version}")
        
        from utils.helpers import setup_logging, validate_pdf_file
        print("✓ Helper functions available")
        
        # Test PDF validation
        is_valid, message = validate_pdf_file("nonexistent.pdf")
        print(f"✓ PDF validation works: {message}")
        
        return True
        
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Energy Document AI without Qdrant")
    print("=" * 50)
    
    tests = [
        test_rag_system,
        test_ui_components
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! System handles missing Qdrant gracefully.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())