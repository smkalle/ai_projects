# Building Temporal Knowledge Graphs with Graphiti (Zep) — A Hands‑On Guide for AI Engineers

This GitHub-style tutorial is based on the Zep/Graphiti project: https://github.com/getzep/graphiti

Zep equips AI agents with human-like memory using a three-level organization:
- Level 1: Raw data (episodes)
- Level 2: Entities and relationships
- Level 3: Clusters with summaries

Benchmarks show up to 18.5% accuracy improvement and 90% latency reduction compared to traditional systems like MemGPT. Zep addresses RAG’s limitations (staleness, slow updates, weak structure) with a temporally-aware knowledge graph that tracks changes over time. This aligns with 2024 research on temporal knowledge graphs emphasizing time dynamics in knowledge representation.

## Table of Contents
- Introduction
- Prerequisites
- Installation
- Environment Setup
- Initialize Graphiti
- Build the Graph: Add Episodes
- Query the Graph
- Advanced Features
- Benchmarks & Comparisons
- Troubleshooting & Best Practices
- Next Steps

## Introduction

Graphiti (the engine behind Zep) builds a bi-temporal knowledge graph: it records both when facts happened (event time) and when they were learned (ingest time). It ingests unstructured text, chat messages, or structured JSON as episodes and derives entities and relationships that evolve over time. This enables point-in-time queries, contradiction handling via edge invalidation, and hybrid retrieval that blends semantic search with keyword and graph traversal.

Key capabilities:
- Real-time incremental updates without full reprocessing
- Hybrid retrieval (embeddings + BM25 + graph distance)
- Temporal awareness (valid-from/valid-until edges)
- Scales to large corpora with concurrent ingestion

Backends: Neo4j or FalkorDB. LLM providers: OpenAI, Gemini, Anthropic, Groq, and more (for extraction and embeddings).

## Prerequisites

- Python 3.10+
- One graph backend:
  - Neo4j 5.26+ (Desktop or Docker)
  - FalkorDB 1.1.2+ (Docker: `docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest`)
- One LLM/embedding provider API key (e.g., OpenAI)
- Basic familiarity with asyncio and graph concepts

Optional:
- `python-dotenv` for `.env` loading
- Accounts for Gemini/Anthropic/Groq

## Installation

Install Graphiti core:

```bash
pip install graphiti-core
```

Optional extras:

```bash
# FalkorDB support
pip install "graphiti-core[falkordb]"

# Anthropic and Groq clients
pip install "graphiti-core[anthropic,groq]"
```

Alternative (UV):

```bash
uv add graphiti-core
```

Note: Use models that support structured outputs (e.g., GPT-4o, Gemini 1.5). Small models may fail to extract reliable entities/relations.

## Environment Setup

Create a `.env` file:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=your_openai_api_key
# Optional tuning
SEMAPHORE_LIMIT=10
USE_PARALLEL_RUNTIME=false
GRAPHITI_TELEMETRY_ENABLED=false
```

Minimal logging setup:

```python
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("graphiti_tutorial")
load_dotenv()
```

## Initialize Graphiti

```python
import os
import asyncio
from graphiti_core import Graphiti

neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
neo4j_user = os.getenv("NEO4J_USER", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD")

async def init_graph():
    graph = await Graphiti.build(neo4j_uri, neo4j_user, neo4j_password)
    return graph

graph = asyncio.run(init_graph())
```

Graphiti creates indices/constraints on first run for efficient queries.

## Build the Graph: Add Episodes

Episodes are timestamped inputs (text, messages, JSON). Graphiti extracts entities and relations, tracks lifecycles, and invalidates outdated edges when contradictions appear.

```python
from datetime import datetime, timezone
from graphiti_core.nodes import EpisodeType

async def add_text_episode(graph):
    await graph.add_episode(
        name="User_Feedback_1",
        episode_body=(
            "Alice bought Allbirds Wool Runners. She loves the comfort but "
            "complains about durability after 3 months."
        ),
        source=EpisodeType.text,
        source_description="User review from forum",
        reference_time=datetime(2025, 1, 15, 10, 0, tzinfo=timezone.utc),
    )

async def add_message_episode(graph):
    await graph.add_episode(
        name="Support_Chat_1",
        episode_body=(
            "Alice: My Allbirds shoes are falling apart.\n"
            "Support: Sorry, Alice. We'll send a replacement."
        ),
        source=EpisodeType.message,
        source_description="Customer support transcript",
        reference_time=datetime(2025, 2, 20, 14, 30, tzinfo=timezone.utc),
    )

async def add_json_episode(graph):
    product_data = {
        "id": "PROD001",
        "name": "Allbirds Wool Runners",
        "material": "Merino Wool",
        "price": 120.00,
        "in_stock": True,
        "last_updated": "2025-03-01T12:00:00Z",
    }
    await graph.add_episode(
        name="Product_Update_1",
        episode_body=product_data,
        source=EpisodeType.json,
        source_description="Product catalog update",
        reference_time=datetime.now(tz=timezone.utc),
    )
```

Bulk ingestion for initial loads (skips edge invalidation):

```python
async def add_bulk(graph):
    episodes = [
        {
            "name": "Batch_Episode_1",
            "episode_body": "Batch text about product X.",
            "source": EpisodeType.text,
            "reference_time": datetime.now(tz=timezone.utc),
        },
        # more episodes ...
    ]
    await graph.add_episode_bulk(episodes)
```

## Query the Graph

Search edges (relationships) with a hybrid strategy and time filter:

```python
from graphiti_core.search.search_config import EdgeSearchConfig

async def search_edges(graph):
    results = await graph.search_edges(
        query="User complaints about Allbirds durability",
        config=EdgeSearchConfig(
            max_results=10,
            search_type="hybrid",
            since=datetime(2025, 1, 1, tzinfo=timezone.utc),
        ),
    )
    return results
```

Search nodes (entities) with a prebuilt recipe:

```python
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

async def search_nodes(graph):
    results = await graph.search_nodes(
        query="Products loved by Alice",
        config=NODE_HYBRID_SEARCH_RRF(max_results=5),
    )
    return results
```

Tips:
- Rerank by graph distance to a focal node for context-aware results.
- Use `since`/`until` for historical point-in-time queries.

## Advanced Features

- Custom types: Model domain-specific entities/edges with Pydantic and register them (helps schema clarity and precision).
- Alternative LLMs/embedders:

```python
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig

llm = GeminiClient(LLMConfig(model="gemini-1.5-pro"))
embedder = GeminiEmbedder(GeminiEmbedderConfig(model="text-embedding-004"))
# graph = await Graphiti.build(..., llm_client=llm, embedder=embedder)
```

- Service mode: Run as a REST/MCP server and integrate with tools.
- Provenance: Track source descriptions per episode for audits.

## Benchmarks & Comparisons

- Accuracy: Up to 18.5% improvement on agent memory tasks.
- Latency: ~90% reduction by combining hybrid retrieval with structured memory instead of on-the-fly summarization.
- Compared to traditional RAG/GraphRAG: Graphiti’s bi-temporal tracking and incremental updates excel when knowledge changes frequently.

Reproduce: Ingest ~1k episodes and measure query latency before/after enabling hybrid search and graph reranking.

## Troubleshooting & Best Practices

- Rate limits: Lower `SEMAPHORE_LIMIT`; consider higher-throughput providers (e.g., Groq) for extraction/embeddings.
- Ingestion failures: Prefer models with structured outputs; verify API keys and model names.
- Performance: Keep episodes small and coherent; use bulk only for initial backfills.
- Observability: Enable INFO logs; inspect results in Neo4j Browser/Falkor UI.
- Data quality: Define custom entity/edge types early to avoid ontology drift.

## Next Steps

- Explore Graphiti examples in the upstream repo
- Integrate with Zep’s platform features (sessions, memory APIs)
- Add domain-specific entity/edge schemas and evaluators
- Build evaluation harnesses to quantify recall/latency on your data

Notes:
- API/package names may vary across versions; consult the upstream docs for the exact signatures in your installed version.

***

If you want, run the companion notebook `graphiti_zep_tutorial.ipynb` for an end-to-end, runnable walkthrough.

