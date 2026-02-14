# AI Commerce Agent - UCP + LangGraph + RAG

An end-to-end AI-powered commerce agent integrating Google's **Universal Commerce Protocol (UCP)** with **LangGraph** for multi-step agent workflows and **RAG** (Retrieval-Augmented Generation) for context-aware product retrieval.

## Architecture

```
User Query
    |
    v
[Intent Detection] -- LLM classifies: search / buy / cart / checkout / general
    |
    v
[RAG Retrieval] -- Semantic search via ChromaDB vector store
    |
    v
[UCP Actions] -- Cart management, checkout via UCP merchant server
    |
    v
[LLM Response] -- Context-aware response generation
```

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Merchant Server | FastAPI | UCP-compliant product catalog, cart, checkout |
| RAG Engine | ChromaDB + OpenAI Embeddings | Semantic product search |
| Agent Workflow | LangGraph (StateGraph) | Multi-step orchestration |
| Agent API | FastAPI | HTTP API + Web UI serving |
| Web UI | HTML/CSS/JS | Interactive chat interface |

## Project Structure

```
ai_commerce_agent_ucp/
├── agent/
│   ├── graph.py          # LangGraph workflow (intent -> retrieve -> act -> respond)
│   ├── rag.py            # RAG setup with ChromaDB
│   └── ucp_client.py     # HTTP client for UCP merchant server
├── merchant_server/
│   ├── models.py          # Pydantic models (Product, Cart, Checkout, UCP)
│   ├── server.py          # FastAPI merchant server with UCP endpoints
│   └── startup.py         # Lifespan handler for product loading
├── ui/
│   ├── templates/index.html
│   └── static/{css,js}/
├── data/
│   └── products.json      # Sample product catalog (12 items)
├── tests/
│   ├── test_merchant_server.py  # 20 tests for UCP endpoints
│   ├── test_models.py           # 10 tests for Pydantic models
│   └── test_agent_api.py        # 6 tests for agent API + UI
├── agent_api.py           # Main application entrypoint
├── config.py              # Settings via pydantic-settings
├── pyproject.toml
└── requirements.txt
```

## Setup

### Prerequisites

- Python 3.10+
- OpenAI API key

### Installation

```bash
cd ai_commerce_agent_ucp
pip install -e ".[dev]"
```

### Configuration

```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

### Running

```bash
# Start the full application (merchant server + agent API + web UI)
python agent_api.py
```

This starts:
- **Merchant Server** on port 8182 (UCP endpoints)
- **Agent API + Web UI** on port 8000

Open http://localhost:8000 in your browser.

### Running Tests

```bash
python -m pytest tests/ -v
```

## UCP Endpoints

The merchant server exposes these UCP-compliant endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/.well-known/ucp` | GET | UCP discovery manifest |
| `/products` | GET | List products with filters |
| `/products/search` | POST | Semantic product search |
| `/products/{id}` | GET | Get product details |
| `/cart` | POST | Create a new cart |
| `/cart/{id}/items` | POST | Add item to cart |
| `/checkout-sessions` | POST | Create checkout session |
| `/checkout-sessions/{id}/confirm` | POST | Confirm checkout |

## Agent API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send query through LangGraph agent |
| `/api/products` | GET | Browse products |
| `/api/ucp/discover` | GET | View UCP capabilities |
| `/api/session/{id}` | GET/DELETE | Session management |

## Example Queries

- "Show me headphones under $200"
- "What wireless accessories do you have?"
- "Buy the mechanical keyboard"
- "What's in my cart?"
- "Checkout"
