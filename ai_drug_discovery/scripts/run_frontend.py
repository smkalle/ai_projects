#!/usr/bin/env python3
"""
Script to run the Streamlit frontend
"""
import subprocess
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Run the Streamlit frontend"""
    print("🎨 Starting Rare Disease Drug Repurposing AI Frontend...")
    print("   Access the app at: http://localhost:8501")
    print("   Make sure the backend is running at: http://localhost:8000")
    print()

    try:
        # Change to project root directory
        os.chdir(project_root)

        # Run Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "src/frontend/app.py",
            "--server.address", "0.0.0.0",
            "--server.port", "8501",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]

        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        print("\n👋 Shutting down frontend server...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()