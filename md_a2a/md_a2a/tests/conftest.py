"""Pytest configuration and fixtures for Medical AI Assistant MVP."""

import asyncio
import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.database import init_database
from src.main import app


@pytest.fixture(scope="session")
def test_db() -> Generator[str, None, None]:
    """Create a temporary test database."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    # Set environment variable for test database
    original_db_path = getattr(init_database, "DB_PATH", None)

    # Patch the database path
    import src.database

    src.database.DB_PATH = Path(db_path)

    # Initialize test database (run async function)
    asyncio.run(init_database())

    yield db_path

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

    # Restore original database path
    if original_db_path:
        src.database.DB_PATH = original_db_path


@pytest.fixture
def client(test_db: str) -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_patient_data() -> dict:
    """Sample patient data for testing."""
    return {"name": "Test Patient", "age_years": 8, "weight_kg": 25.0, "gender": "male"}


@pytest.fixture
def sample_case_data(sample_patient_data: dict) -> dict:
    """Sample case data for testing."""
    return {
        "patient": sample_patient_data,
        "symptoms": "fever and headache",
        "severity": "medium",
        "volunteer_id": "test-volunteer-123",
    }


@pytest.fixture
def sample_doctor_review() -> dict:
    """Sample doctor review for testing."""
    return {
        "review": "Patient should rest and take fluids. Monitor temperature.",
        "doctor_id": "test-doctor-456",
    }
