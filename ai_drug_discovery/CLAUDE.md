# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a production-ready AI-powered drug repurposing system for rare diseases, using LangChain for orchestration and providing citation-verified recommendations. The system consists of a FastAPI backend, Streamlit frontend, and multiple AI agents that coordinate biomedical research, analysis, and safety evaluation.

## Development Commands

### Package Management
This project uses **uv** exclusively (no pip). All dependencies are defined in `pyproject.toml`.

```bash
# Install/update dependencies
uv sync --dev

# Run backend server
uv run python scripts/run_backend.py

# Run frontend (in separate terminal)
uv run python scripts/run_frontend.py

# Run tests
uv run pytest -q

# Run specific test file
uv run pytest tests/test_api.py -v

# Format code
uv run black .

# Lint code
uv run flake8

# Type checking
uv run mypy src
```

### Server Access
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture & Key Components

### Core Architecture Pattern
The system follows a multi-agent orchestration pattern with clear separation of concerns:

```
Frontend (Streamlit) → Backend (FastAPI) → Coordinator Agent → Specialized Agents
                                                ↓
                                    [Research, Analysis, Citation, Safety Agents]
```

### Key Directories
- `src/agents/` - AI agent implementations using LangChain
  - `coordinator.py` - Main orchestrator that manages workflow
  - `researcher.py` - Handles biomedical database queries
  - `analyzer.py` - Performs molecular/pathway analysis
  - `citation_agent.py` - Verifies sources and formats citations
  
- `src/api/` - FastAPI endpoints and dependencies
  - `routes.py` - API route definitions
  - `schemas.py` - Pydantic models for request/response validation
  
- `src/frontend/` - Streamlit UI components
  - `app.py` - Main Streamlit application
  - `components/` - Reusable UI components
  
- `src/tools/` - External API integrations
  - `drugbank_tool.py` - DrugBank API wrapper
  - `pubmed_tool.py` - PubMed search integration
  - `pubchem_tool.py` - PubChem data retrieval

### Data Models
All data models are defined in `src/models.py` using Pydantic for strict validation:
- `Drug` - Drug information with DrugBank ID, names, mechanism
- `Disease` - Disease entity with OMIM ID and characteristics
- `DrugCandidate` - Complete repurposing candidate with analysis
- `RepurposingAnalysis` - Confidence scores and mechanism details
- `SafetyProfile` - Side effects, contraindications, monitoring
- `Citation` - Evidence sources with study type and relevance

### Agent Coordination Flow
1. **CoordinatorAgent** receives disease query from API
2. Orchestrates parallel execution of specialized agents
3. **ResearcherAgent** queries biomedical databases (PubMed, DrugBank)
4. **AnalyzerAgent** performs molecular pathway analysis
5. **CitationAgent** verifies all sources and formats citations
6. Results are aggregated with confidence scoring
7. Final report includes all citations with evidence levels

### Demo Mode
The system runs in demo mode by default (`DEMO_MODE=true` in config):
- Returns realistic mock data without external API calls
- Sample diseases and drugs are predefined
- Useful for development and testing without API keys

### Configuration
Settings are managed in `src/config.py`:
- Environment variables loaded from `.env`
- Demo mode toggle
- API host/port configuration
- Database connection settings
- LLM provider settings (OpenAI, Anthropic)

## Testing Strategy

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test categories
uv run pytest tests/test_agents.py  # Agent logic tests
uv run pytest tests/test_api.py     # API endpoint tests
uv run pytest tests/test_tools.py   # External tool tests
```

## Key Design Principles

1. **Evidence-First**: Every recommendation must have verifiable citations
2. **Structured Outputs**: Pydantic schemas enforce consistent data structures
3. **Parallel Processing**: Agents execute concurrently where possible
4. **Safety Checks**: Contraindications and monitoring requirements are always included
5. **Provenance Tracking**: All data transformations are logged with sources

## Common Tasks

### Adding a New Agent
1. Create agent class in `src/agents/`
2. Inherit from base agent pattern in existing agents
3. Register with CoordinatorAgent in `coordinator.py`
4. Add corresponding tests in `tests/test_agents.py`

### Adding API Endpoints
1. Define Pydantic schemas in `src/api/schemas.py`
2. Add route handler in `src/api/routes.py`
3. Use dependency injection for database/agent access
4. Add API tests in `tests/test_api.py`

### Integrating New Data Sources
1. Create tool wrapper in `src/tools/`
2. Implement async methods for data retrieval
3. Add error handling and retry logic
4. Mock responses for demo mode in tool implementation