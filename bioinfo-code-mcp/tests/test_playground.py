"""Tests for the playground web application."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from playground.app import STARTER_PROJECTS, CATEGORIES, app

# Only run if fastapi is installed
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


class TestPlaygroundRoutes:
    """Test the playground web routes."""

    def test_index_page(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Bioinformatics Playground" in resp.text
        assert "CodeMirror" in resp.text

    def test_list_templates(self, client):
        resp = client.get("/api/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == len(STARTER_PROJECTS)
        assert len(data["categories"]) > 0

    def test_get_template(self, client):
        resp = client.get("/api/template/gene-lookup")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "gene-lookup"
        assert data["title"] == "Gene Lookup"
        assert "code" in data
        assert len(data["code"]) > 0

    def test_get_template_not_found(self, client):
        resp = client.get("/api/template/nonexistent")
        assert resp.status_code == 404

    def test_list_modules(self, client):
        resp = client.get("/api/modules")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["modules"]) > 0
        assert len(data["tags"]) > 0

    def test_search_operations(self, client):
        resp = client.get("/api/search?query=gene+lookup")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] > 0

    def test_search_by_module(self, client):
        resp = client.get("/api/search?module=ncbi")
        assert resp.status_code == 200
        data = resp.json()
        assert all(r["module"] == "ncbi" for r in data["results"])

    def test_execute_code(self, client):
        resp = client.post("/api/execute", json={
            "session_id": "test-session",
            "code": "return 42",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "42" in data["result"]

    def test_execute_with_state(self, client):
        # Set state
        resp = client.post("/api/execute", json={
            "session_id": "state-test",
            "code": 'state["x"] = 99\nreturn state["x"]',
        })
        assert resp.json()["success"] is True

        # Read state
        resp = client.post("/api/execute", json={
            "session_id": "state-test",
            "code": 'return state.get("x")',
        })
        data = resp.json()
        assert data["success"] is True
        assert "99" in data["result"]

    def test_reset_state(self, client):
        # Set state
        client.post("/api/execute", json={
            "session_id": "reset-test",
            "code": 'state["val"] = 123',
        })
        # Reset
        resp = client.post("/api/reset", json={"session_id": "reset-test"})
        assert resp.json()["success"] is True

        # Verify cleared
        resp = client.post("/api/execute", json={
            "session_id": "reset-test",
            "code": 'return state.get("val", "gone")',
        })
        assert "gone" in resp.json()["result"]

    def test_execute_error(self, client):
        resp = client.post("/api/execute", json={
            "session_id": "err-test",
            "code": "return 1/0",
        })
        data = resp.json()
        assert data["success"] is False
        assert "ZeroDivisionError" in data["result"]

    def test_execute_seq_utils(self, client):
        resp = client.post("/api/execute", json={
            "session_id": "util-test",
            "code": 'return seq_utils.gc_content("ATGCGC")',
        })
        data = resp.json()
        assert data["success"] is True


class TestStarterProjects:
    """Test starter project template content."""

    def test_all_templates_have_required_fields(self):
        for proj in STARTER_PROJECTS:
            assert "id" in proj, f"Missing id: {proj.get('title')}"
            assert "title" in proj
            assert "category" in proj
            assert "difficulty" in proj
            assert "description" in proj
            assert "code" in proj
            assert len(proj["code"]) > 50, f"Code too short: {proj['title']}"

    def test_unique_ids(self):
        ids = [p["id"] for p in STARTER_PROJECTS]
        assert len(ids) == len(set(ids)), "Duplicate template IDs found"

    def test_valid_difficulties(self):
        valid = {"Beginner", "Intermediate", "Advanced"}
        for proj in STARTER_PROJECTS:
            assert proj["difficulty"] in valid, f"Invalid difficulty: {proj['difficulty']}"

    def test_at_least_10_templates(self):
        assert len(STARTER_PROJECTS) >= 10

    def test_categories_not_empty(self):
        for cat, projects in CATEGORIES.items():
            assert len(projects) > 0, f"Empty category: {cat}"

    def test_template_code_is_valid_python(self):
        """Check that each template's code parses as valid Python."""
        for proj in STARTER_PROJECTS:
            # Wrap like the sandbox does
            indented = "\n".join(f"    {line}" for line in proj["code"].splitlines())
            wrapped = f"async def __test__():\n{indented}"
            try:
                compile(wrapped, f"<{proj['id']}>", "exec")
            except SyntaxError as e:
                pytest.fail(f"Template '{proj['title']}' has syntax error: {e}")
