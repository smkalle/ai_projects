"""Pytest fixtures — loads .env and provides a real Gemini client for integration tests."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from google import genai

# Load .env from the project root (two levels up from this file)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: mark test as calling real external APIs")


@pytest.fixture(scope="session")
def api_key() -> str:
    """Return the Gemini API key from environment."""
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        pytest.skip("Set GOOGLE_API_KEY or GEMINI_API_KEY in .env — skipping integration tests")
    return key


@pytest.fixture(scope="session")
def genai_client(api_key: str) -> genai.Client:
    """Return a real google-genai Client (session-scoped for reuse)."""
    return genai.Client(api_key=api_key)


@pytest.fixture(autouse=True)
def _rate_limit_delay(request):
    """Sleep 15s between integration tests to stay under free-tier RPM."""
    if request.node.get_closest_marker("integration"):
        import time
        time.sleep(15)
