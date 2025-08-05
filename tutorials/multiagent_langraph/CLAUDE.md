# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based multi-agent AI system tutorial using LangGraph and FastAPI. The project demonstrates building a production-ready environmental health monitoring system called GreenGuard.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI application
uvicorn greenguard.main:app --reload

# Test the system
curl -X POST http://127.0.0.1:8000/trigger-check -H "Content-Type: application/json" -d '{"location": "San Francisco, CA"}'
```

## Architecture

### Core Components

1. **Multi-Agent System** (`greenguard/main.py`):
   - **DataScout**: Gathers environmental hazard data using Tavily search
   - **RiskAssessor**: Analyzes data and assesses health risks  
   - **Communicaid**: Generates public health alerts
   - **Dispatch**: Sends alerts to communities
   - **Supervisor**: Manages agent flow through conditional routing

2. **State Management**:
   - Uses LangGraph's `StateGraph` with `GreenGuardState` TypedDict
   - State includes: location, hazard_data, health_risk_assessment, public_alert, messages

3. **API Layer**:
   - FastAPI endpoint at `/trigger-check`
   - Accepts location parameter and returns complete execution state

### Key Technologies

- **LangGraph**: For multi-agent orchestration and state management
- **OpenAI GPT-4**: LLM for agent intelligence
- **Tavily**: Web search capabilities for DataScout agent
- **FastAPI/Uvicorn**: REST API server
- **Redis**: Configured for distributed state (not actively implemented)

### Important Patterns

- Supervisor pattern for agent coordination with conditional edges
- State-driven workflow execution
- Error handling for missing API keys
- Each agent has specific prompts and responsibilities defined in `create_agent()` calls

## Environment Setup

Required environment variables in `.env`:
- `OPENAI_API_KEY`: For GPT-4 access
- `TAVILY_API_KEY`: For web search capabilities

## Reference Documentation

The `multiagent_langgraph.md` file contains comprehensive tutorial documentation covering:
- LangGraph concepts and patterns
- Production deployment considerations
- Testing frameworks
- Advanced monitoring and logging setup
- Complete implementation examples