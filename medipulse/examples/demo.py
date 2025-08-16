#!/usr/bin/env python3
"""
MediPulse Demo Script

This script demonstrates how to use MediPulse for medical document extraction.
It includes examples for different document types and shows the complete workflow.

Usage:
    python examples/demo.py
"""

import sys
import os
import base64
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from medipulse import MediPulse, MediPulseConfig

def create_sample_base64():
    """Create a minimal sample base64 image for demo purposes"""
    # This is a 1x1 pixel PNG - replace with actual medical document for real testing
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def demo_lab_report():
    """Demo processing a lab report"""
    print("\n" + "="*60)
    print("DEMO: Lab Report Processing")
    print("="*60)

    try:
        medipulse = MediPulse()

        # In real usage, you would load an actual medical document image
        sample_base64 = create_sample_base64()

        print("Processing sample lab report...")
        result = medipulse.process_document(sample_base64)

        print("\nProcessing Result:")
        print(json.dumps(result, indent=2, default=str))

        if result['success']:
            print("\n✅ Lab report processed successfully!")
            if result['extracted_data']:
                print(f"Document Type: {result.get('doc_classification', {}).get('doc_type', 'Unknown')}")
                print(f"Confidence: {result.get('doc_classification', {}).get('confidence', 'N/A')}")
        else:
            print("\n❌ Processing failed:")
            print(result['error_message'])

    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("Make sure you have:")
        print("1. Set OPENAI_API_KEY in your .env file")
        print("2. Installed all requirements: pip install -r requirements.txt")

def demo_file_processing():
    """Demo processing from a file (if available)"""
    print("\n" + "="*60)
    print("DEMO: File Processing")
    print("="*60)

    # Look for sample images in test_data directory
    test_data_dir = Path(__file__).parent.parent / "tests" / "test_data"

    if not test_data_dir.exists():
        print("No test data directory found. Skipping file processing demo.")
        print("To test with real files:")
        print("1. Create tests/test_data/ directory")
        print("2. Add sample medical document images (JPG, PNG)")
        print("3. Run this demo again")
        return

    # Look for image files
    image_files = list(test_data_dir.glob("*.jpg")) + list(test_data_dir.glob("*.png"))

    if not image_files:
        print("No image files found in tests/test_data/")
        print("Add some sample medical document images and try again.")
        return

    try:
        medipulse = MediPulse()

        for image_file in image_files[:2]:  # Process first 2 files
            print(f"\nProcessing: {image_file.name}")
            result = medipulse.process_document_from_file(str(image_file))

            if result['success']:
                print(f"✅ {image_file.name} processed successfully!")
                doc_type = result.get('doc_classification', {}).get('doc_type', 'Unknown')
                confidence = result.get('doc_classification', {}).get('confidence', 'N/A')
                print(f"   Document Type: {doc_type}")
                print(f"   Confidence: {confidence}")
            else:
                print(f"❌ Failed to process {image_file.name}: {result['error_message']}")

    except Exception as e:
        print(f"File processing demo failed: {str(e)}")

def demo_custom_config():
    """Demo using custom configuration"""
    print("\n" + "="*60)
    print("DEMO: Custom Configuration")
    print("="*60)

    try:
        # Create custom configuration
        config = MediPulseConfig()
        # You could modify config here, e.g.:
        # config.model = "gpt-4o-mini"  # Use a different model

        medipulse = MediPulse(config)

        print("✅ MediPulse initialized with custom configuration")
        print(f"Model: {config.model}")
        print(f"API Key configured: {'Yes' if config.openai_api_key else 'No'}")

    except Exception as e:
        print(f"Custom configuration demo failed: {str(e)}")

def main():
    """Run all demos"""
    print("MediPulse Demo Application")
    print("🏥 Medical Document Extraction Prototype")
    print("-" * 60)

    # Check if .env file exists
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print("⚠️  WARNING: No .env file found!")
        print("Please create a .env file with your OPENAI_API_KEY")
        print("You can copy .env.example and fill in your API key")
        print()

    # Run demos
    demo_custom_config()
    demo_lab_report()
    demo_file_processing()

    print("\n" + "="*60)
    print("Demo completed!")
    print("\nNext Steps:")
    print("1. Add real medical document images to tests/test_data/")
    print("2. Try processing your own medical documents")
    print("3. Explore the API documentation in docs/api.md")
    print("4. Contribute to the project on GitHub")

if __name__ == "__main__":
    main()
