#!/usr/bin/env python3
"""
Setup script for Custom RAG System
"""
import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, find_packages

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["data", "data/lancedb"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Created necessary directories")

def check_requirements():
    """Check if requirements.txt exists"""
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found in current directory")
        return False
    print("✅ requirements.txt found")
    return True

def install_dependencies():
    """Install Python dependencies"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def check_environment():
    """Check if OpenAI API key is set"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OpenAI API key not set. LLM synthesis will not work.")
        print("   Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    print("✅ OpenAI API key is configured")
    return True

def test_installation():
    """Test if the installation works"""
    print("🧪 Testing installation...")
    try:
        # Test imports
        import streamlit
        import sentence_transformers
        import faiss
        import pandas
        import numpy
        
        # Try importing LanceDB
        try:
            import lancedb
            print("✅ LanceDB backend available")
        except ImportError:
            print("⚠️  LanceDB backend not available (install with: pip install lancedb)")
        
        print("✅ All core dependencies can be imported")
        return True
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Custom RAG System\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check requirements file
    if not check_requirements():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please check your internet connection and try again.")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed. Please check the error messages above.")
        sys.exit(1)
    
    # Check environment
    api_key_configured = check_environment()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set OpenAI API key (if not already done):")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    print("\n2. Run the application:")
    print("   streamlit run app.py")
    print("\n3. Open your browser to http://localhost:8501")
    print("\n4. Upload sample_document.txt and start asking questions!")
    
    if not api_key_configured:
        print("\n⚠️  Note: Without OpenAI API key, you'll only get basic retrieval results.")

setup(
    name="custom_rag",
    version="0.1.0",
    packages=find_packages(),
)

if __name__ == "__main__":
    main() 