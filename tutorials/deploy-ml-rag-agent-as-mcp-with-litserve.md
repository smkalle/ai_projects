
# Deploy **Any ML Model, RAG, or Agent** as an **MCP Server** with **LitServe** (10‑Line Core)

A hands‑on, production‑minded tutorial for AI engineers. You’ll stand up:
- a 10‑line LitServe API,
- a practical RAG service,
- a simple Agent service,
- and expose any of them as an **MCP server** (Claude, Cursor, Copilot Studio, etc.).

> **Why this works:** LitServe is a flexible, FastAPI‑based serving engine with batching/streaming/GPU autoscaling and **OpenAI‑compatible** endpoints. Recent updates add **MCP support**, so any LitServe API can be consumed by MCP clients with minimal glue.

---

## Table of Contents
1. [Prereqs & Install](#prereqs--install)
2. [The 10‑Line Core](#the-10line-core)
3. [Example A — Minimal Inference API](#example-a--minimal-inference-api)
4. [Example B — RAG API (Chroma + OpenAI)](#example-b--rag-api-chroma--openai)
5. [Example C — Agent API (News summarizer)](#example-c--agent-api-news-summarizer)
6. [Expose Your LitServe API as an MCP Server](#expose-your-litserve-api-as-an-mcp-server)
7. [OpenAI‑Compatible Endpoint (Optional)](#openaicompatible-endpoint-optional)
8. [Docker & Cloud Run](#docker--cloud-run)
9. [Testing & Health Checks](#testing--health-checks)
10. [Performance Tips](#performance-tips)
11. [Security Notes (MCP 2025‑06‑18)](#security-notes-mcp-20250618)
12. [References](#references)

---

## Prereqs & Install

```bash
# Python 3.9+ recommended
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install litserve requests
# For examples that use OpenAI & RAG:
pip install openai langchain chromadb sentence-transformers
```

> If you will run GPU models, also install the appropriate CUDA/PyTorch wheels.

---

## The 10‑Line Core

Below is the **entire core** you need for a LitServe API. Substitute your own logic inside `predict`:

```python
# server_minimal.py
import litserve as ls

class Minimal(ls.LitAPI):
    def predict(self, request):
        x = request["input"]
        return {"output": x**2}

if __name__ == "__main__":
    ls.LitServer(Minimal()).run(port=8000)
```

Run it:

```bash
python server_minimal.py
curl -X POST localhost:8000/predict -H "content-type: application/json" -d '{"input": 4}'
```

---

## Example A — Minimal Inference API

Use two tiny “models” to show multi‑component logic in one endpoint.

```python
# server_pipeline.py
import litserve as ls

class InferencePipeline(ls.LitAPI):
    def setup(self, device):
        self.square = lambda v: v**2
        self.cube = lambda v: v**3

    def predict(self, request):
        v = float(request["input"])
        return {"sum_sq_cu": self.square(v) + self.cube(v)}

if __name__ == "__main__":
    ls.LitServer(InferencePipeline(), accelerator="auto").run(port=8000)
```

Test:

```bash
python server_pipeline.py
curl -X POST localhost:8000/predict -H "content-type: application/json" -d '{"input": 3}'
```

---

## Example B — RAG API (Chroma + OpenAI)

This example persists a local vector DB and answers questions from it.

**Step 1: Ingest local docs**

```python
# ingest_docs.py
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)  # Put your .txt/.md/.pdf (text‑extracted) here

texts = []
for p in DOCS_DIR.rglob("*"):
    if p.suffix.lower() in {".txt", ".md"}:
        texts.append(p.read_text(encoding="utf-8", errors="ignore"))

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents(texts)

emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
Chroma.from_documents(chunks, emb, persist_directory="chroma_db").persist()
print("✅ Ingested", len(chunks), "chunks into ./chroma_db")
```

**Step 2: Serve RAG**

```python
# server_rag.py
import os
import litserve as ls
from typing import Dict, Any
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class RAGAPI(ls.LitAPI):
    def setup(self, device):
        self.emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vs = Chroma(persist_directory="chroma_db", embedding_function=self.emb)
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def predict(self, request: Dict[str, Any]):
        query = request.get("query", "")
        k = int(request.get("top_k", 3))
        docs = self.vs.similarity_search(query, k=k)
        context = "\n\n".join(d.page_content for d in docs)

        resp = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Answer using the provided context. If insufficient, say so."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ],
            temperature=0.2,
        )
        return {
            "answer": resp.choices[0].message.content,
            "sources": [d.metadata for d in docs],
        }

if __name__ == "__main__":
    ls.LitServer(RAGAPI()).run(port=8001)
```

Run it:

```bash
python ingest_docs.py
OPENAI_API_KEY=sk-... python server_rag.py
curl -X POST localhost:8001/predict -H "content-type: application/json" -d '{"query":"What do the docs say about onboarding?"}'
```

---

## Example C — Agent API (News summarizer)

A tiny “agent” that fetches a page and asks an LLM to summarize it.

```python
# server_agent.py
import os, re, requests, litserve as ls
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class NewsAgent(ls.LitAPI):
    def setup(self, device):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def predict(self, request):
        url = request.get("url", "https://text.npr.org/")
        html = requests.get(url, timeout=10).text
        text = re.sub(r"<[^>]+>", " ", html)[:4000]

        resp = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the main stories and any notable trends."},
                {"role": "user", "content": text}
            ],
            max_tokens=400,
            temperature=0.3,
        )
        return {"summary": resp.choices[0].message.content.strip(), "source": url}

if __name__ == "__main__":
    ls.LitServer(NewsAgent()).run(port=8002)
```

Test:

```bash
OPENAI_API_KEY=sk-... python server_agent.py
curl -X POST localhost:8002/predict -H "content-type: application/json" -d '{"url":"https://www.reuters.com/"}'
```

> **Note:** Always follow the target site’s terms of use when fetching content.

---

## Expose Your LitServe API as an MCP Server

There are two common patterns:

### 1) **Built‑in MCP endpoint in LitServe** (zero glue)

Recent versions of LitServe add a **dedicated `/mcp/` endpoint**, allowing MCP clients (Claude Desktop, Cursor, etc.) to discover and call your server as an MCP tool with minimal setup.

```python
# server_minimal_mcp.py
import litserve as ls

class Minimal(ls.LitAPI):
    def predict(self, request):
        return {"output": float(request["input"])**2}

if __name__ == "__main__":
    server = ls.LitServer(Minimal())
    # 👇 enable the MCP endpoint
    server.run(port=8000, enable_mcp=True)  # exposes /mcp/ for MCP clients
```

Configure **Claude Desktop** (macOS path shown) to load your server:

```jsonc
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "litserve-minimal": {
      "command": "python",
      "args": ["server_minimal_mcp.py"]
    }
  }
}
```

Restart Claude Desktop; your **litserve-minimal** tool should appear.

### 2) **MCP bridge** using the official Python SDK (full control)

If you need custom auth, routing or multiple LitServe backends, build a tiny MCP server that **forwards tool calls** to your LitServe `/predict`.

```python
# mcp_bridge.py
import json, httpx
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP

LITSERVE_URL = "http://127.0.0.1:8000"

mcp = FastMCP("litserve-bridge")

@mcp.tool()
def call_predict(payload: Dict[str, Any]) -> str:
    """Call the LitServe /predict endpoint with a JSON payload.
    Args:
        payload: Arbitrary JSON that your LitServe API expects.
    """
    r = httpx.post(f"{LITSERVE_URL}/predict", json=payload, timeout=30.0)
    r.raise_for_status()
    return json.dumps(r.json())

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Claude Desktop config for the bridge:

```jsonc
{
  "mcpServers": {
    "litserve-bridge": {
      "command": "python",
      "args": ["mcp_bridge.py"]
    }
  }
}
```

---

## OpenAI‑Compatible Endpoint (Optional)

Expose `/v1/chat/completions` so existing SDKs and tools “just work”:

```python
# server_openai_compat.py
import litserve as ls

class YourAPI(ls.LitAPI):
    def predict(self, req):
        # convert OpenAI-style messages to your logic and return a 'choices' structure
        msg = req["messages"][-1]["content"]
        return {"choices":[{"message":{"content":f"You said: {msg}"}}]}

server = ls.LitServer(YourAPI(), spec=ls.OpenAISpec())
server.run(port=8003)
```

Test with curl (or any OpenAI‑compatible client):

```bash
curl http://localhost:8003/v1/chat/completions   -H "content-type: application/json"   -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hello!"}]}' 
```

---

## Docker & Cloud Run

**Dockerfile**

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "server_minimal.py"]
```

**requirements.txt**

```text
litserve
requests
openai
langchain
chromadb
sentence-transformers
```

**Build & run locally**

```bash
docker build -t litserve-mcp .
docker run --rm -p 8000:8000 litserve-mcp
```

**Deploy to Google Cloud Run**

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/litserve-mcp
gcloud run deploy litserve-mcp   --image gcr.io/PROJECT_ID/litserve-mcp   --platform managed   --port 8000   --memory 2Gi   --cpu 2
```

---

## Testing & Health Checks

```bash
# Basic predict
curl -X POST localhost:8000/predict   -H "content-type: application/json"   -d '{"input": 5}'

# Liveness (FastAPI-style)
curl localhost:8000/healthz || true
```

Add logging and request timing as needed inside your `predict` implementation.

---

## Performance Tips

- Prefer **batching** when requests are small but frequent: `ls.LitServer(YourAPI(), max_batch_size=32, batch_timeout=0.05)`
- Enable **GPU** and **multiple workers** to saturate hardware: `accelerator="cuda", workers_per_device=2`
- Use **streaming** for LLM token generation to reduce tail latency.
- Keep model weights on device in `setup()`; avoid reloading on each request.

---

## Security Notes (MCP 2025‑06‑18)

- Newer MCP spec clarifies **authn/authz**, including separation of auth server and resource server and guidance for **remote HTTP/SSE** transports.
- When exposing remote MCP endpoints, prefer **OAuth2/OIDC** and scope tokens by resource indicator.
- For local stdio servers, redirect logs to **stderr** (never stdout) to avoid corrupting JSON‑RPC traffic.

---

## References

- LitServe GitHub: https://github.com/Lightning-AI/LitServe  
- LitServe docs (APIs, features like **OpenAISpec**, **LitServer**, **benchmarks**): https://lightning.ai/docs/litserve/  
- LitServe “2× faster than FastAPI” claim (README/benchmarks): https://github.com/Lightning-AI/LitServe#performance  
- MCP Quickstart (Python, FastMCP): https://modelcontextprotocol.io/quickstart/server  
- MCP Spec (2025‑06‑18): https://modelcontextprotocol.io/specification/2025-06-18  
- Blog: *Deploy any ML model, RAG or Agent as an MCP server* (LitServe `/mcp/` endpoint overview): https://blog.dailydoseofds.com/p/deploy-any-ml-model-rag-or-agent

---

**License:** MIT for this tutorial text. Code snippets are provided AS‑IS; review licenses of upstream dependencies before distribution.
