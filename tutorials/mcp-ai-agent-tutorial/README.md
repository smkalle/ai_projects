# MCP AI Agent Tutorial: Complete Guide with Streamlit & FastAPI

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)

A comprehensive, hands-on tutorial for AI engineers to build custom AI agents using the Model Context Protocol (MCP) with Streamlit frontend and FastAPI backend.

## 🌟 Features

- **Complete MCP Integration**: Connect any LLM to any MCP server
- **Modern Architecture**: FastAPI backend + Streamlit frontend
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

## 🛠️ Tech Stack

- **Backend**: FastAPI, Pydantic, MCP-Use
- **Frontend**: Streamlit, Plotly
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
