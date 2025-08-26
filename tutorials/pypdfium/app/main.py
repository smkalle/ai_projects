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

def run_api_subprocess():
    """Run the FastAPI application as subprocess"""
    import subprocess
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "api.endpoints:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]
    
    if settings.debug:
        cmd.extend(["--reload", "--log-level", "debug"])
    else:
        cmd.extend(["--log-level", "info"])
    
    subprocess.run(cmd)

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
        import subprocess
        import signal
        import time

        # Initialize process variables
        api_process = None
        streamlit_process = None

        # Signal handler for graceful shutdown
        def signal_handler(sig, frame):
            print("\nShutting down services...")
            try:
                if api_process:
                    api_process.terminate()
                if streamlit_process:
                    streamlit_process.terminate()
            except:
                pass
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start API server as subprocess
        api_cmd = [
            sys.executable, "-m", "uvicorn",
            "api.endpoints:app",
            "--host", "0.0.0.0",
            "--port", "8000"
        ]
        
        if settings.debug:
            api_cmd.extend(["--reload", "--log-level", "debug"])
        else:
            api_cmd.extend(["--log-level", "info"])

        # Start Streamlit as subprocess
        streamlit_app_path = app_dir / "ui" / "streamlit_app.py"
        streamlit_cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_app_path),
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ]

        try:
            print("Starting FastAPI server...")
            api_process = subprocess.Popen(api_cmd, cwd=app_dir)
            time.sleep(2)  # Give API time to start
            
            print("Starting Streamlit UI...")
            streamlit_process = subprocess.Popen(streamlit_cmd, cwd=app_dir)
            
            # Wait for both processes
            while True:
                api_status = api_process.poll()
                streamlit_status = streamlit_process.poll()
                
                if api_status is not None:
                    print(f"FastAPI server exited with code {api_status}")
                    if streamlit_process:
                        streamlit_process.terminate()
                    break
                    
                if streamlit_status is not None:
                    print(f"Streamlit UI exited with code {streamlit_status}")
                    if api_process:
                        api_process.terminate()
                    break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nShutting down services...")
            try:
                if api_process:
                    api_process.terminate()
                if streamlit_process:
                    streamlit_process.terminate()
            except:
                pass
