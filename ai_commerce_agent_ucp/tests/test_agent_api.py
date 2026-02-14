"""Tests for the agent API endpoints (non-LLM functionality)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_lifespan():
    """Mock the lifespan to avoid starting merchant server subprocess."""
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def noop_lifespan(app):
        yield

    return noop_lifespan


@pytest.fixture
def client(mock_lifespan):
    """Create a test client with mocked lifespan."""
    from agent_api import app

    app.router.lifespan_context = mock_lifespan
    return TestClient(app)


class TestSessionManagement:
    def test_get_session_creates_new(self, client):
        resp = client.get("/api/session/test-session-123")
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == "test-session-123"
        assert data["cart_id"] == ""
        assert data["checkout_id"] == ""
        assert data["history_length"] == 0

    def test_clear_session(self, client):
        # Create a session
        client.get("/api/session/to-delete")

        # Clear it
        resp = client.delete("/api/session/to-delete")
        assert resp.status_code == 200
        assert resp.json()["status"] == "cleared"

    def test_clear_nonexistent_session(self, client):
        resp = client.delete("/api/session/nonexistent")
        assert resp.status_code == 200


class TestWebUI:
    def test_index_page(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "AI Commerce Agent" in resp.text
        assert "text/html" in resp.headers["content-type"]

    def test_static_css(self, client):
        resp = client.get("/static/css/style.css")
        assert resp.status_code == 200

    def test_static_js(self, client):
        resp = client.get("/static/js/app.js")
        assert resp.status_code == 200
