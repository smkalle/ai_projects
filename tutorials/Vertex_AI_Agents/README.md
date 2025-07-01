# Vertex AI Multi‑Agent Financial Research Assistant

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)  
**Cut fundamental company research from days to minutes** by recreating the Google Cloud × Schroders prototype with Vertex AI **Agent Builder**, **Agent Development Kit (ADK)**, and **LangGraph**.

_Last updated: 2025-07-01_

## 🚀 Quickstart

```bash
git clone https://github.com/YOUR_GH_HANDLE/vertexai-multi-agent-finance.git
cd vertexai-multi-agent-finance

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
jupyter lab notebook/vertex_ai_multi_agent_tutorial.ipynb
```

## 🧠 Components
- `document_search_agent` → Vertex AI Search
- `bigquery_agent` → BigQuery data
- `web_search_agent` → Google Search API
- `router_agent` → routes tasks using LangGraph

## 📦 Deployment
Deploy the orchestrated agent to Vertex AI Agent Engine for production use.

## 🧪 Evaluation
Use Vertex AI Generative AI Evaluation for benchmarking accuracy, latency, and tool usage.

## 📝 License
Apache 2.0 — see [LICENSE](LICENSE)
