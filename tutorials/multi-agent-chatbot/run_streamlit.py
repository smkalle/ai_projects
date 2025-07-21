#!/usr/bin/env python3
"""
Launch script for the Multi-Agent Chatbot Streamlit application
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Setup environment variables and check dependencies"""
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Check for .env file
    env_file = current_dir / ".env"
    env_example = current_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("⚠️  No .env file found. Creating from .env.example...")
        with open(env_example, 'r') as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print("📝 Please edit .env file with your API keys before running the app.")
    
    # Load environment variables
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'streamlit-chat', 
        'plotly',
        'pandas',
        'tiktoken',
        'aiohttp',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        print("\nOr install all requirements:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

def main():
    """Main launcher function"""
    print("🚀 Starting Multi-Agent Chatbot...")
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    check_dependencies()
    
    # Get the streamlit app path
    app_path = Path(__file__).parent / "streamlit_app" / "main.py"
    
    if not app_path.exists():
        print(f"❌ Streamlit app not found at {app_path}")
        sys.exit(1)
    
    # Launch Streamlit
    print(f"📱 Launching Streamlit app from {app_path}")
    print("🌐 The app will open in your browser automatically")
    print("🔗 If it doesn't open, go to: http://localhost:8501")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_path),
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--browser.serverAddress=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()