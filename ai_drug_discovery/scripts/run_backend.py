#!/usr/bin/env python3
"""
Script to run the FastAPI backend server
"""
import uvicorn
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings

def main():
    """Run the FastAPI backend server"""
    print("🚀 Starting Rare Disease Drug Repurposing AI Backend...")
    print(f"   Environment: {settings.environment}")
    print(f"   Debug Mode: {settings.debug}")
    print(f"   Demo Mode: {settings.demo_mode}")
    print(f"   Host: {settings.api_host}:{settings.api_port}")
    print()

    try:
        uvicorn.run(
            "src.main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.debug,
            log_level="info" if not settings.debug else "debug",
            reload_dirs=["src"] if settings.debug else None
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down backend server...")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()