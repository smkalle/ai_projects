# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent content search system built with LangGraph that implements Agent-to-Agent (A2A) handoffs. The system demonstrates a decentralized approach where specialized agents (Publishing, Broadcasting, News) collaborate without a central supervisor.

## Development Commands

```bash
# Testing
pytest                    # Run all tests
pytest --cov=src         # Run tests with coverage report
pytest tests/test_specific.py::test_function  # Run a single test

# Code Quality
black src tests agents   # Format code
flake8 src tests agents  # Lint code  
mypy src agents          # Type checking

# Running the Application
python app.py                                    # CLI version
uvicorn server.main:app --reload --port 8000    # API server (FastAPI)
streamlit run streamlit_app.py                   # Web UI (Streamlit)
```

## Architecture

### Multi-Agent System
The system uses three specialized agents that can hand off conversations:

- **Publishing Agent** (`agents/publishing.py`) - Handles book-related queries
- **Broadcasting Agent** (`agents/broadcasting.py`) - Handles TV/films/documentaries
- **News Agent** (`agents/news.py`) - Handles journalism and news content

### Core Components

1. **State Graph** (`graph.py`): Defines the LangGraph state machine with agent nodes and transitions
2. **Handoff Mechanism** (`agents/tools.py`): Implements `Command(goto=next_agent)` for peer-to-peer handoffs
3. **Entry Points**:
   - `app.py` - Direct CLI execution
   - `server/main.py` - FastAPI REST API
   - `streamlit_app.py` - Web interface

### Agent Implementation Pattern
Each agent follows this structure:
- Uses `MessagesState` for shared conversation state
- Has access to domain-specific tools (e.g., `search_books`, `search_tv`)
- Can decide autonomously when to hand off to another agent
- Returns either a message response or a `Command` object for handoff

### Environment Setup
The project requires an OpenAI API key. Set it as:
```bash
export OPENAI_API_KEY="your-api-key"
```

## Key Dependencies
- `langgraph` - State graph framework for multi-agent systems
- `langchain-openai` - OpenAI integration (default model: gpt-4o-mini)
- `fastapi` - Backend API server
- `streamlit` - Web UI framework

## Current Implementation Notes
- Search tools currently return mock data - designed to be swapped with real APIs
- The system starts with the Publishing agent by default
- CORS is enabled on the FastAPI server for frontend integration