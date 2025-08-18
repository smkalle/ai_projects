#!/usr/bin/env python3
"""
Setup script for NGO Medical AI Assistant
Helps with initial project setup and configuration
"""

import os
import sys
import shutil
from pathlib import Path

def setup_environment():
    """Set up the development environment"""
    print("🏥 Setting up NGO Medical AI Assistant...")

    # Create .env file from example if it doesn't exist
    env_file = Path("config/.env")
    env_example = Path("config/.env.example")

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created config/.env from template")
        print("⚠️  Please edit config/.env to add your API keys")

    # Create data directories
    data_dirs = [
        "data/raw",
        "data/processed", 
        "data/medical_images",
        "logs",
        "models"
    ]

    for dir_path in data_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    print("✅ Created data directories")

    # Create sample data files
    sample_readme = """# Medical Data Directory

This directory contains medical data files for the AI assistant.

## Structure:
- `raw/`: Raw medical images and data
- `processed/`: Processed data ready for AI models
- `medical_images/`: Medical imaging files (X-rays, CT scans, etc.)

## Privacy Notice:
⚠️ Never commit real patient data to version control.
Only use anonymized, synthetic, or publicly available medical data.
"""

    with open("data/README.md", "w") as f:
        f.write(sample_readme)

    print("✅ Setup complete!")
    print()
    print("Next steps:")
    print("1. Edit config/.env to add your API keys")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the app: python src/main.py")
    print("4. Or try the Gradio demo: python src/gradio_demo.py")

if __name__ == "__main__":
    setup_environment()
