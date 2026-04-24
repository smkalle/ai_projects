"""
Flask app exposing Gemini API endpoints for Cloud Run deployment.

Routes:
  GET  /           — serve the demo UI
  POST /api/generate — proxy to Gemini generateContent
  POST /api/embed    — proxy to Gemini text embeddings

Environment variables:
  GOOGLE_API_KEY          — Gemini API key (direct mode)
  GOOGLE_GENAI_USE_VERTEXAI — set to "true" to use Vertex AI / Agent Platform
  GOOGLE_CLOUD_PROJECT    — GCP project when using Vertex AI
  GOOGLE_CLOUD_LOCATION   — region when using Vertex AI (default: "global")
  PORT                    — HTTP port (default: 8080, set by Cloud Run)
"""

import os
import sys

from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

PORT = int(os.getenv("PORT", 8080))
HOST = "0.0.0.0"

app = Flask(__name__, template_folder="templates")


# ---------------------------------------------------------------------------
# Gemini client (lazy-init so tests can patch before first request)
# ---------------------------------------------------------------------------

def get_genai_client():
    """Return a google.genai.Client, picking up auth from env automatically."""
    from google import genai
    return genai.Client()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    """
    Proxy to Gemini generateContent.

    Body (JSON):
      prompt   — string, required
      model    — string, optional  (default: gemini-3-flash-preview)
      max_tokens — int, optional
      temperature — float, optional

    Returns:
      200 {text: "...", model: "...", usage: {...}}
      400 {error: "..."}
      500 {error: "..."}
    """
    body = request.get_json(silent=True) or {}

    prompt = body.get("prompt", "").strip()
    if not prompt:
        return jsonify(error="prompt is required"), 400

    model = body.get("model", "gemini-3-flash-preview")
    max_tokens = body.get("max_tokens")
    temperature = body.get("temperature")

    try:
        from google.genai import types
        config_params = {}
        if max_tokens is not None:
            config_params["max_output_tokens"] = max_tokens
        if temperature is not None:
            config_params["temperature"] = temperature

        config = types.GenerateContentConfig(**config_params) if config_params else None

        client = get_genai_client()
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        usage = {}
        if hasattr(response, "usage_metadata"):
            um = response.usage_metadata
            usage = {
                "prompt_tokens": getattr(um, "prompt_token_count", None),
                "candidates_tokens": getattr(um, "candidates_token_count", None),
                "total_tokens": getattr(um, "total_token_count", None),
            }

        return jsonify(
            text=response.text,
            model=model,
            usage=usage,
        )

    except Exception as exc:  # noqa: BLE001
        return jsonify(error=str(exc)), 500


@app.route("/api/embed", methods=["POST"])
def embed():
    """
    Proxy to Gemini text embeddings.

    Body (JSON):
      texts    — list[str], required
      model    — string, optional (default: gemini-embedding-001)
      task_type — string, optional (default: RETRIEVAL_DOCUMENT)

    Returns:
      200 {embeddings: [[float, ...], ...]}
      400 {error: "..."}
      500 {error: "..."}
    """
    body = request.get_json(silent=True) or {}

    texts = body.get("texts")
    if not texts:
        return jsonify(error="texts (list of strings) is required"), 400
    if isinstance(texts, str):
        texts = [texts]

    model = body.get("model", "gemini-embedding-001")
    task_type = body.get("task_type", "RETRIEVAL_DOCUMENT")

    try:
        from google.genai import types
        client = get_genai_client()
        response = client.models.embed_content(
            model=model,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type=task_type,
            ),
        )
        embeddings = [e.values for e in response.embeddings]
        return jsonify(embeddings=embeddings)

    except Exception as exc:  # noqa: BLE001
        return jsonify(error=str(exc)), 500


# ---------------------------------------------------------------------------
# WSGI entry point (used by gunicorn in production)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)
