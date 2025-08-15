# MCP AI Agent Tutorial: Complete Guide with Streamlit & FastAPI

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)

A comprehensive, hands-on tutorial for AI engineers to build custom AI agents using the Model Context Protocol (MCP) with Streamlit frontend and FastAPI backend.

## 🌟 Features

- **Complete MCP Integration**: Connect any LLM to any MCP server
- **Modern Architecture**: FastAPI backend + Streamlit frontend
- **New Web UI**: Tailwind CSS + Preline static app under `web/` (served at `/app`)
- **Production Ready**: Docker support, testing, CI/CD
- **Extensible**: Modular design for easy customization
- **Educational**: Step-by-step tutorial with detailed explanations
- **Open Source**: MIT licensed, community-driven

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/mcp-ai-agent-tutorial.git
cd mcp-ai-agent-tutorial

# Install dependencies
pip install -r requirements.txt

# Run the development environment
./scripts/run_dev.sh
```

## 🔧 Configuration

- Environment file: copy `.env.example` to `.env` and adjust values.
- Key variables:
  - `API_PORT`: Backend port (default `8000`).
  - `UI_PORT`: Frontend port (default `8501`).
  - `API_BASE_URL`: UI backend URL (e.g., `http://localhost:8000`).
  - `FRONTEND_URL` / `ALLOWED_ORIGINS`: CORS allowlist for the API.
- Sync from your shell: `./scripts/sync_env.sh` will copy common keys from `~/.bashrc` into `.env`.
- Start with env: `./scripts/run_dev.sh` loads `.env` and uses `API_PORT`/`UI_PORT`.
  - New web UI (optional): `cd web && npm install && npm run dev` then open `http://localhost:5173`.
    - Ensure API CORS allows this origin (set `ALLOWED_ORIGINS` or `FRONTEND_URL`).
  - Quick access (no Node build): open `http://localhost:8000/app` (served by FastAPI using Tailwind/Preline CDN).
  - To auto-start the local Tavily search server during dev, set `START_SEARCH_SERVER=true` in `.env` before running.

### MCP Servers (Tools)

- Example config at `configs/mcp_config.json` defines two servers:
  - `search`: HTTP connector at `http://localhost:8765`
  - `file-manager`: stdio to `@modelcontextprotocol/server-filesystem` with read-only access in the current dir
- To enable tools, set in `.env`:
  - `MCP_CONFIG_PATH=$(pwd)/configs/mcp_config.json`
- Then restart the backend. The UI “Available Tools” panel will populate if servers are reachable.

#### Helper script

- Use `./scripts/run_tools.sh` to:
  - Ensure `@modelcontextprotocol/server-filesystem` is available via `npx` (the API will spawn it when needed)
  - Update `configs/mcp_config.json` with `SEARCH_SERVER_URL` from `.env` (if `jq` is installed)
  - Check that the search server URL responds over HTTP

### Search Server (Tavily) — No Docker

- Prereqs: Node.js (with `npx`) and a Tavily API key.
- Configure `.env`:
  - `TAVILY_API_KEY=...`
  - `SEARCH_PORT=8765` (optional)
  - `SEARCH_SERVER_URL=http://localhost:8765`
- Start the server:
  - `./scripts/run_search_server.sh start`
  - Status/stop: `./scripts/run_search_server.sh status|stop`
- Optional: auto-start during tooling prep by setting `START_SEARCH_SERVER=true` and running `./scripts/run_tools.sh`.
  - You can also set `START_SEARCH_SERVER=true` and run `./scripts/run_dev.sh` to auto-start it when launching the app.

## 📖 Tutorial Structure

### Phase 1: Foundations
- Understanding MCP Protocol
- Setting up the development environment
- Basic agent creation

### Phase 2: Backend Development
- FastAPI server implementation
- MCP server integration
- API design and testing

### Phase 3: Frontend Development
- Streamlit application
- User interface components
- Real-time interactions

### Phase 4: Production Deployment
- Docker containerization
- Cloud deployment strategies
- Monitoring and scaling

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  FastAPI Server │────│   MCP Servers   │
│                 │    │                 │    │                 │
│ - Chat Interface│    │ - Agent Logic   │    │ - Web Browsing  │
│ - Config Panel  │    │ - MCP Client    │    │ - File Ops      │
│ - Monitoring    │    │ - API Endpoints │    │ - External APIs │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📚 Documentation

- [Complete Tutorial](docs/TUTORIAL.md) - Step-by-step guide
- [API Reference](docs/API_REFERENCE.md) - FastAPI endpoints
- [Deployment Guide](docs/DEPLOYMENT.md) - Production setup
- [Repository Guidelines](AGENTS.md) - Contributor guide

## 🛠️ Tech Stack

- **Backend**: FastAPI, Pydantic, MCP-Use
- **Frontend**: Streamlit, Plotly, Tailwind CSS + Preline (web/)
- **AI/ML**: OpenAI, Anthropic, Local LLMs
- **Infrastructure**: Docker, PostgreSQL, Redis
- **Testing**: Pytest, FastAPI TestClient

## 📝 Examples

### Basic Agent
```python
from mcp_agent import MCPAgent

agent = MCPAgent(
    model="gpt-4",
    mcp_servers=["web-browser", "file-manager"]
)

response = agent.run("Search for Python tutorials and save them to a file")
print(response)
```

### Web Search Agent
```python
agent = MCPAgent(
    model="claude-3-sonnet",
    tools=["web_search", "summarize"]
)

result = agent.search_and_summarize("Latest AI research papers 2025")
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test category
pytest tests/test_api.py -v
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:8501
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🚢 Publish Checklist (GitHub)

- Update `.env.example` if env keys changed (API_BASE_URL, ports, MCP settings).
- Verify local run:
  - `./scripts/run_dev.sh` (API + Streamlit, optional Tavily server)
  - Open `http://localhost:8000/app` for the new Tailwind/Preline UI
- Run tests and linters:
  - `pytest -q` and `pytest --cov=src`
  - `black src tests && isort src tests && flake8 && mypy src`
- Ensure `.gitignore` excludes build artifacts (`.logs/`, `web/node_modules/`, `web/dist/`).
- Update docs if APIs/UX changed; link to `AGENTS.md`.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MCP-Use](https://github.com/mcp-use/mcp-use) - Core MCP functionality
- [Anthropic](https://www.anthropic.com) - Model Context Protocol
- [Streamlit](https://streamlit.io) - Frontend framework
- [FastAPI](https://fastapi.tiangolo.com) - Backend framework

## 📧 Contact

For questions and support:
- Create an [Issue](https://github.com/your-username/mcp-ai-agent-tutorial/issues)
- Join our [Discord](https://discord.gg/your-server)
- Follow [@your_handle](https://twitter.com/your_handle) for updates

---

⭐ **Star this repository if you find it helpful!**
