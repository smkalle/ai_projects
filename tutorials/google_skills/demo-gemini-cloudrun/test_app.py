"""
Tests for the Flask demo app.
Uses mocked genai client so tests run without credentials.
"""

import json
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

# Ensure the app module is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


# ---------------------------------------------------------------------------
# Install mock google/genai stubs before any real import can happen
# This prevents "No module named 'google'" errors in route handlers.
# ---------------------------------------------------------------------------

_mock_types = MagicMock()
_mock_genai_module = MagicMock(types=_mock_types)


@pytest.fixture(autouse=True)
def mock_genai_modules():
    """Pre-populate sys.modules so any code that imports google.genai gets stubs."""
    import sys
    google_mod = MagicMock()
    google_mod.genai = _mock_genai_module
    google_mod.genai.types = _mock_types
    google_mod.genai.Client = MagicMock
    sys.modules["google"] = google_mod
    sys.modules["google.genai"] = _mock_genai_module
    sys.modules["google.genai.types"] = _mock_types
    yield
    for key in ["google", "google.genai", "google.genai.types"]:
        sys.modules.pop(key, None)


@pytest.fixture
def mock_genai_response():
    """Pre-configured mock for client.models.generate_content."""
    mock_response = MagicMock()
    mock_response.text = "Gemini says: test response"
    mock_response.usage_metadata = MagicMock(
        prompt_token_count=10,
        candidates_token_count=8,
        total_token_count=18,
    )
    return mock_response


@pytest.fixture
def app():
    os.environ.pop("GOOGLE_API_KEY", None)
    os.environ.pop("GOOGLE_GENAI_USE_VERTEXAI", None)
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def mock_client(mock_genai_response):
    """Pre-configured mock genai Client that returns mock_genai_response."""
    mock = MagicMock()
    mock.models.generate_content.return_value = mock_genai_response
    return mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_health_check(app):
    """GET / returns 200 and renders the UI."""
    response = app.get("/")
    assert response.status_code == 200
    assert b"Gemini API Demo" in response.data


def test_generate_missing_prompt(app):
    """POST /api/generate with no prompt returns 400."""
    response = app.post(
        "/api/generate",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "prompt" in data["error"].lower()


def test_generate_success(app, mock_client, mock_genai_response):
    """POST /api/generate with valid prompt returns 200 and text."""
    with patch("app.get_genai_client", return_value=mock_client):
        response = app.post(
            "/api/generate",
            data=json.dumps({"prompt": "Hello, Gemini!"}),
            content_type="application/json",
        )

    assert response.status_code == 200
    data = response.get_json()
    assert "text" in data
    assert data["text"] == "Gemini says: test response"
    assert "model" in data
    assert "usage" in data


def test_generate_with_model_override(app, mock_client, mock_genai_response):
    """model field in request body is passed through to the SDK."""
    with patch("app.get_genai_client", return_value=mock_client):
        response = app.post(
            "/api/generate",
            data=json.dumps({"prompt": "Hi", "model": "gemini-3.1-pro-preview"}),
            content_type="application/json",
        )

    assert response.status_code == 200
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == "gemini-3.1-pro-preview"


def test_generate_with_config_params(app, mock_client, mock_genai_response):
    """max_tokens and temperature are passed as GenerateContentConfig."""
    _mock_types.GenerateContentConfig.reset_mock()
    with patch("app.get_genai_client", return_value=mock_client):
        response = app.post(
            "/api/generate",
            data=json.dumps({
                "prompt": "Hi",
                "max_tokens": 256,
                "temperature": 0.7,
            }),
            content_type="application/json",
        )

    assert response.status_code == 200
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    config = call_kwargs["config"]
    # config is a MagicMock for types.GenerateContentConfig — verify it exists
    # and is not None (proving GenerateContentConfig was called with the right params)
    assert config is not None
    _mock_types.GenerateContentConfig.assert_called_with(max_output_tokens=256, temperature=0.7)


def test_generate_internal_error(app, mock_client):
    """SDK exceptions return 500 with error message."""
    mock_client.models.generate_content.side_effect = RuntimeError("model overloaded")
    with patch("app.get_genai_client", return_value=mock_client):
        response = app.post(
            "/api/generate",
            data=json.dumps({"prompt": "Hi"}),
            content_type="application/json",
        )

    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "model overloaded" in data["error"]


def test_embed_success(app):
    """POST /api/embed returns embedding arrays."""
    mock_response = MagicMock()
    mock_response.embeddings = [
        MagicMock(values=[0.1, 0.2, 0.3]),
        MagicMock(values=[0.4, 0.5, 0.6]),
    ]
    mock_client = MagicMock()
    mock_client.models.embed_content.return_value = mock_response

    with patch("app.get_genai_client", return_value=mock_client):
        response = app.post(
            "/api/embed",
            data=json.dumps({"texts": ["hello world", "goodbye world"]}),
            content_type="application/json",
        )

    assert response.status_code == 200
    data = response.get_json()
    assert "embeddings" in data
    assert len(data["embeddings"]) == 2
    assert data["embeddings"][0] == [0.1, 0.2, 0.3]


def test_embed_missing_texts(app):
    """POST /api/embed with no texts returns 400."""
    response = app.post(
        "/api/embed",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_embed_single_string_normalized_to_list(app):
    """A single string for texts is accepted as [string]."""
    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.1, 0.2])]
    mock_client = MagicMock()
    mock_client.models.embed_content.return_value = mock_response

    with patch("app.get_genai_client", return_value=mock_client):
        response = app.post(
            "/api/embed",
            data=json.dumps({"texts": "single text query"}),
            content_type="application/json",
        )

    assert response.status_code == 200
    call_kwargs = mock_client.models.embed_content.call_args.kwargs
    assert call_kwargs["contents"] == ["single text query"]
