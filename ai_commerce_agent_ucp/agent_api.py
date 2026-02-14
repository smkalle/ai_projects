"""FastAPI application exposing the AI Commerce Agent as an HTTP API.

Provides endpoints for chat interaction, product browsing, and session management.
Also serves the web UI and runs the merchant server in-process.
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import sys
import time as _time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Resolve paths once at module level (absolute, no os.chdir needed)
BASE_DIR = Path(__file__).parent.resolve()
PRODUCTS_PATH = BASE_DIR / "data" / "products.json"

# --- Lifespan: initialize RAG + Merchant Server on startup ---

_merchant_process: subprocess.Popen | None = None


async def _wait_for_merchant(max_attempts: int = 20) -> bool:
    """Wait for the merchant server with exponential backoff."""
    delay = 0.2
    async with httpx.AsyncClient() as client:
        for attempt in range(1, max_attempts + 1):
            try:
                resp = await client.get(f"{settings.merchant_base_url}/health", timeout=2)
                if resp.status_code == 200:
                    logger.info("Merchant server healthy: %s", resp.json())
                    return True
            except (httpx.ConnectError, httpx.TimeoutException):
                pass

            logger.info(
                "Waiting for merchant server (attempt %d/%d, %.1fs)...",
                attempt, max_attempts, delay,
            )
            await asyncio.sleep(delay)
            delay = min(delay * 2, 3.0)

    logger.error("Merchant server failed to become healthy after %d attempts", max_attempts)
    return False


def _terminate_merchant() -> None:
    """Gracefully stop the merchant server subprocess with SIGKILL fallback."""
    global _merchant_process
    if _merchant_process is None:
        return

    try:
        _merchant_process.terminate()
        try:
            _merchant_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Merchant server did not stop gracefully, sending SIGKILL")
            _merchant_process.kill()
            _merchant_process.wait(timeout=3)
    except Exception as e:
        logger.error("Error stopping merchant server: %s", e)
    finally:
        _merchant_process = None
        logger.info("Merchant server stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global _merchant_process

    try:
        # Start merchant server with minimal environment
        merchant_env = {
            "PYTHONPATH": str(BASE_DIR),
            "PATH": os.environ.get("PATH", ""),
        }
        if os.environ.get("OPENAI_API_KEY"):
            merchant_env["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]

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
            cwd=str(BASE_DIR),
            env=merchant_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Async exponential backoff health check
        merchant_ok = await _wait_for_merchant()
        if not merchant_ok:
            logger.warning("Continuing without confirmed merchant server health")

        # Initialize RAG (uses absolute paths, no chdir needed)
        try:
            from agent.rag import initialize_rag

            initialize_rag(str(PRODUCTS_PATH))
            logger.info("RAG system initialized with products from %s", PRODUCTS_PATH)
        except Exception as e:
            logger.warning("RAG initialization failed (set OPENAI_API_KEY to enable): %s", e)

        yield

    finally:
        _terminate_merchant()


# --- FastAPI App ---

app = FastAPI(
    title="AI Commerce Agent",
    description="AI-powered shopping agent using UCP, LangGraph, and RAG",
    version="1.0.0",
    lifespan=lifespan,
)

# Static files and templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "ui" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "ui" / "templates"))


# --- Session Management ---

MAX_SESSIONS = 1000
SESSION_TTL_SECONDS = 3600  # 1 hour

_sessions: dict[str, dict[str, Any]] = {}


def _prune_expired_sessions() -> None:
    """Remove sessions older than SESSION_TTL_SECONDS."""
    now = _time.time()
    expired = [
        sid for sid, s in _sessions.items()
        if now - s.get("created_at", 0) > SESSION_TTL_SECONDS
    ]
    for sid in expired:
        del _sessions[sid]


def get_session(session_id: str) -> dict[str, Any]:
    """Get or create a session."""
    if len(_sessions) >= MAX_SESSIONS:
        _prune_expired_sessions()
    if len(_sessions) >= MAX_SESSIONS:
        oldest_id = min(_sessions, key=lambda s: _sessions[s].get("created_at", 0))
        del _sessions[oldest_id]

    if session_id not in _sessions:
        _sessions[session_id] = {
            "cart_id": "",
            "checkout_id": "",
            "history": [],
            "created_at": _time.time(),
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
        conversation_history=session.get("history", []),
    )

    # Update session state
    if result.get("cart_id"):
        session["cart_id"] = result["cart_id"]
    if result.get("checkout_id"):
        session["checkout_id"] = result["checkout_id"]

    session["history"].append({"role": "user", "content": request.query})
    session["history"].append({"role": "assistant", "content": result.get("response", "")})

    # Keep only last 20 messages (10 turns)
    if len(session["history"]) > 20:
        session["history"] = session["history"][-20:]

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
