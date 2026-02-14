"""FastAPI application exposing the AI Commerce Agent as an HTTP API.

Provides endpoints for chat interaction, product browsing, and session management.
Also serves the web UI and runs the merchant server in-process.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# --- Lifespan: initialize RAG + Merchant Server on startup ---

# Track whether the merchant server subprocess is running
_merchant_process = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    import subprocess
    import sys
    import time

    global _merchant_process

    # Resolve paths relative to this file
    base_dir = Path(__file__).parent.resolve()
    products_path = base_dir / "data" / "products.json"

    # Start merchant server as a subprocess
    merchant_env = os.environ.copy()
    merchant_env["PYTHONPATH"] = str(base_dir)

    logger.info("Starting UCP merchant server on port %d...", settings.merchant_server_port)
    _merchant_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "merchant_server.startup:create_merchant_app",
            "--factory",
            "--host",
            settings.merchant_server_host,
            "--port",
            str(settings.merchant_server_port),
        ],
        cwd=str(base_dir),
        env=merchant_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Give merchant server time to start
    time.sleep(2)

    # Load products into the merchant server
    import requests as req

    for attempt in range(5):
        try:
            # Load products into the merchant server via startup event
            # The merchant server loads products from its own startup
            health = req.get(f"{settings.merchant_base_url}/health", timeout=3)
            if health.status_code == 200:
                logger.info("Merchant server is healthy: %s", health.json())
                break
        except req.ConnectionError:
            logger.info("Waiting for merchant server (attempt %d)...", attempt + 1)
            time.sleep(1)

    # Initialize RAG
    os.chdir(str(base_dir))
    try:
        from agent.rag import initialize_rag

        rag = initialize_rag(str(products_path))
        logger.info("RAG system initialized with products from %s", products_path)
    except Exception as e:
        logger.warning("RAG initialization requires OpenAI API key: %s", e)
        logger.info("Set OPENAI_API_KEY environment variable to enable RAG features")

    yield

    # Shutdown
    if _merchant_process:
        _merchant_process.terminate()
        _merchant_process.wait(timeout=5)
        logger.info("Merchant server stopped")


# --- FastAPI App ---

app = FastAPI(
    title="AI Commerce Agent",
    description="AI-powered shopping agent using UCP, LangGraph, and RAG",
    version="1.0.0",
    lifespan=lifespan,
)

# Static files and templates
base_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(base_dir / "ui" / "static")), name="static")
templates = Jinja2Templates(directory=str(base_dir / "ui" / "templates"))


# --- Session Management ---

# Simple in-memory session store (use Redis/DB in production)
_sessions: dict[str, dict[str, Any]] = {}


def get_session(session_id: str) -> dict[str, Any]:
    """Get or create a session."""
    if session_id not in _sessions:
        _sessions[session_id] = {
            "cart_id": "",
            "checkout_id": "",
            "history": [],
        }
    return _sessions[session_id]


# --- Request/Response Models ---


class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    intent: str = ""
    products: list[dict[str, Any]] = Field(default_factory=list)
    cart_id: str = ""
    checkout_id: str = ""
    checkout_details: dict[str, Any] = Field(default_factory=dict)
    error: str = ""


class ProductListResponse(BaseModel):
    products: list[dict[str, Any]]
    total: int


# --- API Endpoints ---


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Main chat endpoint. Sends user query through the LangGraph agent pipeline."""
    from agent.graph import run_query

    session = get_session(request.session_id)

    result = run_query(
        query=request.query,
        cart_id=session.get("cart_id", ""),
        checkout_id=session.get("checkout_id", ""),
    )

    # Update session state
    if result.get("cart_id"):
        session["cart_id"] = result["cart_id"]
    if result.get("checkout_id"):
        session["checkout_id"] = result["checkout_id"]

    session["history"].append({"role": "user", "content": request.query})
    session["history"].append({"role": "assistant", "content": result.get("response", "")})

    return ChatResponse(
        response=result.get("response", "I couldn't process your request."),
        intent=result.get("intent", ""),
        products=result.get("product_results", []),
        cart_id=result.get("cart_id", ""),
        checkout_id=result.get("checkout_id", ""),
        checkout_details=result.get("checkout_details", {}),
        error=result.get("error", ""),
    )


@app.get("/api/products", response_model=ProductListResponse)
def get_products(category: str = "", limit: int = 50) -> ProductListResponse:
    """List products from the merchant server."""
    from agent.ucp_client import get_ucp_client

    client = get_ucp_client()
    try:
        data = client.list_products(category=category, limit=limit)
        return ProductListResponse(
            products=data.get("products", []),
            total=data.get("total", 0),
        )
    except Exception as e:
        logger.error("Failed to fetch products: %s", e)
        return ProductListResponse(products=[], total=0)


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict[str, Any]:
    """Get a single product."""
    from agent.ucp_client import get_ucp_client

    client = get_ucp_client()
    return client.get_product(product_id)


@app.get("/api/ucp/discover")
def ucp_discover() -> dict[str, Any]:
    """Discover UCP capabilities of the merchant server."""
    from agent.ucp_client import get_ucp_client

    client = get_ucp_client()
    return client.discover()


@app.get("/api/session/{session_id}")
def get_session_info(session_id: str) -> dict[str, Any]:
    """Get current session state."""
    session = get_session(session_id)
    return {
        "session_id": session_id,
        "cart_id": session.get("cart_id", ""),
        "checkout_id": session.get("checkout_id", ""),
        "history_length": len(session.get("history", [])),
    }


@app.delete("/api/session/{session_id}")
def clear_session(session_id: str) -> dict[str, str]:
    """Clear a session."""
    if session_id in _sessions:
        del _sessions[session_id]
    return {"status": "cleared", "session_id": session_id}


# --- Web UI ---


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Serve the main web UI."""
    return templates.TemplateResponse(request, "index.html")


# --- Entrypoint ---

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agent_api:app",
        host=settings.agent_api_host,
        port=settings.agent_api_port,
        reload=True,
    )
