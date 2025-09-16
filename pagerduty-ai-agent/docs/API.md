# PagerDuty AI Agent API Documentation

This document provides comprehensive information about the PagerDuty AI Agent's architecture, components, and usage patterns.

## Overview

The PagerDuty AI Agent is a sophisticated incident management system built using LangChain, LangGraph, and OpenAI's GPT-4 omini. It provides natural language interaction with incident data, replacing traditional dashboard navigation with conversational analytics.

## Architecture

### Core Components

1. **Streamlit Frontend** (`app.py`)
   - Web-based chat interface
   - Real-time conversation with AI agent
   - Sidebar with statistics and quick actions

2. **LangGraph Workflow** (`src/agents/workflow.py`)
   - Stateful conversation management
   - Tool orchestration and routing
   - Error handling and recovery

3. **Database Layer** (`src/data/`)
   - SQLAlchemy models for incidents and services
   - Database manager for CRUD operations
   - SQLite backend (easily replaceable with PostgreSQL)

4. **Tool System** (`src/tools/`)
   - Database interaction tools
   - Analytics and reporting tools
   - LangChain-compatible tool interfaces

## Database Schema

### Tables

#### Services
```sql
CREATE TABLE services (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
```

#### Incidents
```sql
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'triggered',
    urgency VARCHAR(20) NOT NULL DEFAULT 'medium',
    service_id INTEGER NOT NULL,
    created_at DATETIME,
    acknowledged_at DATETIME,
    resolved_at DATETIME,
    updated_at DATETIME,
    assigned_to VARCHAR(100),
    escalation_level INTEGER DEFAULT 1,
    FOREIGN KEY (service_id) REFERENCES services(id)
);
```

## Agent Tools

### Database Tools (`src/tools/database_tools.py`)

- `get_incident_count()` - Count incidents with optional filters
- `get_incident_stats()` - Comprehensive incident statistics
- `search_incidents()` - Search incidents by title or description
- `get_service_statistics()` - Service-level metrics
- `get_recent_incidents()` - Time-based incident filtering
- `calculate_resolution_metrics()` - Resolution time analysis
- `update_incident_status()` - Status management

### Analytics Tools (`src/tools/analytics_tools.py`)

- `analyze_incident_trends()` - Trend analysis over time
- `compare_service_performance()` - Service comparison
- `identify_problem_patterns()` - Problem detection
- `generate_incident_report()` - Comprehensive reporting

## Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.0

# Database Configuration  
DATABASE_URL=sqlite:///incidents.db

# Application Configuration
APP_NAME=PagerDuty AI Agent
DEBUG=false
LOG_LEVEL=INFO
```

## Usage Patterns

### Basic Queries
- "How many high priority incidents are open?"
- "Show me incidents from the last 24 hours"
- "What's the average resolution time for database incidents?"

### Analytics Queries
- "Analyze incident trends for the past month"
- "Compare service performance across all services"
- "What problem patterns can you identify?"

## Deployment

### Local Development
```bash
# 1. Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Initialize database
python scripts/init_database.py

# 4. Run application
streamlit run app.py
```

### Production Considerations

1. **Database**: Replace SQLite with PostgreSQL for production
2. **Authentication**: Add user authentication and session management  
3. **Monitoring**: Implement application monitoring and alerting
4. **Scaling**: Consider containerization and load balancing
5. **Security**: Implement input validation and rate limiting