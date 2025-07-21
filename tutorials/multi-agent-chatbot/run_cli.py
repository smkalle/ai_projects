#!/usr/bin/env python3
"""
CLI Launcher for Multi-Agent Chatbot
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'rich',
        'aiohttp'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages for CLI:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print("   pip install rich aiohttp")
        print("\nOr install all requirements:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🚀 Starting Multi-Agent Chatbot CLI...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Get the CLI app path
    cli_path = Path(__file__).parent / "cli_app" / "main.py"
    
    if not cli_path.exists():
        print(f"❌ CLI app not found at {cli_path}")
        sys.exit(1)
    
    # Launch CLI
    print("🎯 Launching CLI interface...")
    print("💡 Tip: Type 'help' for available commands")
    print("")
    
    try:
        subprocess.run([sys.executable, str(cli_path)])
    except KeyboardInterrupt:
        print("\n👋 CLI closed by user")
    except Exception as e:
        print(f"❌ Error launching CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()