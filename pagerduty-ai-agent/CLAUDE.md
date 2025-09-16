# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_database.py
```

### Running the Application
```bash
# Start the Streamlit web application
streamlit run app.py
```

### Testing and Quality
```bash
# Run all tests
python -m pytest tests/ -v

# Code formatting
black . && isort .

# Linting
flake8
```

## Architecture Overview

This is a PagerDuty-inspired AI agent built with LangChain/LangGraph and Streamlit for incident management.

### Core Components

- **Frontend**: `app.py` - Streamlit web interface with session management
- **Agent Workflow**: `src/agents/workflow.py` - LangGraph-based conversational agent with state management
- **Database Layer**: `src/data/` - SQLAlchemy models and database management for incidents
- **Tools**: `src/tools/` - LangChain tools for database queries and analytics
- **Configuration**: `src/utils/` - Settings management and logging

### Key Architecture Patterns

1. **LangGraph Workflow**: The agent uses LangGraph's `StateGraph` for managing conversational state and tool execution
2. **Tool-based Architecture**: Database operations are exposed as LangChain tools that the LLM can call
3. **SQLAlchemy Models**: Incident data is modeled with enums for status, urgency, and service types
4. **Session Persistence**: Streamlit session state maintains conversation history and agent state

### Database Schema

- **Incidents**: Main entity with status (triggered/acknowledged/resolved), urgency levels, service associations
- **Services**: Service catalog for incident categorization
- **Memory**: LangChain memory storage for conversation persistence

### Environment Configuration

Required environment variables in `.env`:
- `OPENAI_API_KEY`: OpenAI API key for GPT-4
- `DATABASE_URL`: SQLite database URL (defaults to `sqlite:///incidents.db`)
- Optional: `LANGCHAIN_TRACING_V2` and `LANGCHAIN_API_KEY` for LangSmith observability

### Development Notes

- The codebase follows Black formatting (88 character line length)
- Type hints are used throughout
- All database operations go through the `DatabaseManager` class
- Tools are organized by domain (database operations, analytics)
- The agent supports natural language queries about incident data and analytics