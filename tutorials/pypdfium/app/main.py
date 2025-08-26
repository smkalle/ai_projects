"""
Main application entry point for Energy Document AI
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from utils.config import settings
from utils.helpers import setup_logging

# Setup logging
setup_logging(settings.debug)

def run_streamlit():
    """Run the Streamlit application"""
    import subprocess

    streamlit_app_path = app_dir / "ui" / "streamlit_app.py"

    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(streamlit_app_path),
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ]

    subprocess.run(cmd)

def run_api():
    """Run the FastAPI application"""
    import uvicorn

    uvicorn.run(
        "api.endpoints:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Energy Document AI")
    parser.add_argument(
        "--mode", 
        choices=["ui", "api", "both"], 
        default="ui",
        help="Run mode: ui (Streamlit), api (FastAPI), both (both services)"
    )

    args = parser.parse_args()

    if args.mode == "ui":
        print("Starting Streamlit UI...")
        run_streamlit()
    elif args.mode == "api":
        print("Starting FastAPI server...")
        run_api()
    elif args.mode == "both":
        print("Starting both UI and API...")
        import threading

        # Start API in background thread
        api_thread = threading.Thread(target=run_api)
        api_thread.daemon = True
        api_thread.start()

        # Start Streamlit in main thread
        run_streamlit()
