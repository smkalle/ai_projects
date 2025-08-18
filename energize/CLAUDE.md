# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Energize is a comprehensive SaaS Energy Tech Platform that evolves through four major versions:
- **MVP**: Smart Building Energy Analytics
- **V1**: Energy Optimization & Demand Response Platform  
- **V2**: Cybersecurity Platform for Energy & EV Networks
- **V3**: Unified Energy Intelligence Platform

## Development Guidelines

### Technology Stack Requirements

**Backend:**
- Use FastAPI for all Python-based API development (lightweight, performant)
- Package management: Use `uv` exclusively (NO pip, NO poetry)
- Database: PostgreSQL + TimescaleDB for time-series data
- Real-time processing: Apache Kafka, Redis
- ML/AI: Use lightweight implementations with MLflow for model management

**Frontend:**
- Use Streamlit for rapid prototyping and dashboard development
- Production UI: React.js with TypeScript
- Styling: Tailwind CSS for all UI components
- Ensure Silicon Valley standards for UX (suitable for Series C funding)

**Infrastructure:**
- Microservices architecture with clear service boundaries
- Use Kubernetes for orchestration in V1+
- API-first design with comprehensive documentation

### Development Commands

```bash
# Package management (use uv)
uv pip install <package>
uv run <script.py>
uv pip list

# Run FastAPI server (background)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# Run Streamlit dashboard  
uv run streamlit run app/dashboard.py --server.port 8501 &

# Database migrations
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "description"

# Testing
uv run pytest tests/ -v
uv run pytest tests/integration/ --cov=app

# Code quality
uv run ruff check .
uv run ruff format .
uv run mypy app/
```

## Architecture Overview

### MVP Architecture (Current Phase)
- Monolithic FastAPI application with modular structure
- PostgreSQL + TimescaleDB for data storage
- REST API with JWT authentication
- Streamlit dashboard for quick prototyping
- React.js production dashboard with Tailwind CSS

### Key Directories Structure
```
energize/
├── app/
│   ├── api/           # FastAPI routes and endpoints
│   ├── core/          # Core configuration and security
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic layer
│   ├── ml/            # ML models and predictions
│   └── dashboard/     # Streamlit dashboards
├── frontend/          # React.js application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/      # Page components
│   │   ├── services/   # API client services
│   │   └── styles/     # Tailwind CSS styles
├── tests/             # Test suites
├── migrations/        # Alembic migrations
└── scripts/           # Utility scripts
```

## Implementation Phases

Each feature implementation MUST follow these phases:

1. **Phase 1: Tech Spec & UX Design**
   - Create detailed technical specification
   - Design UI/UX mockups (Silicon Valley standards)
   - Define API contracts

2. **Phase 2: Backend Implementation**  
   - Implement database models
   - Create API endpoints with FastAPI
   - Add unit tests and integration tests
   - API integration signoff required

3. **Phase 3: Frontend Implementation**
   - Build Streamlit prototype for rapid iteration
   - Implement production React components with Tailwind
   - Ensure responsive design
   - UI verification via HTTP URL (e.g., http://localhost:8501)
   - Human signoff required

4. **Phase 4: Integration & Testing**
   - End-to-end testing
   - Performance optimization
   - Security testing
   - Final human signoff

## Database Schema

Core tables for energy management:
- `buildings`: Building information and metadata
- `sensors`: IoT sensor registry
- `energy_readings`: Time-series energy data (TimescaleDB hypertable)
- `alerts`: System-generated alerts
- `users`: User authentication and profiles  
- `tenants`: Multi-tenant organization data

## API Design Patterns

All APIs follow RESTful conventions:
- Authentication: JWT tokens via `/api/auth/*`
- Resource endpoints: `/api/v1/{resource}`
- Pagination: `?page=1&limit=20`
- Filtering: Query parameters
- Response format: JSON with consistent structure

## Performance Requirements

- API response time: <200ms for dashboard queries
- Data ingestion: 1000+ readings/second
- Concurrent users: 100+ (MVP), scaling to 100,000+ (V3)
- Database queries: Use indexes and TimescaleDB continuous aggregates
- Caching: Redis for frequently accessed data

## Security Requirements

- All endpoints require authentication except health checks
- Role-based access control (RBAC)
- Multi-tenant data isolation
- Input validation on all user inputs
- SQL injection prevention via parameterized queries
- Rate limiting on all API endpoints

## Testing Requirements

- Unit test coverage: >80%
- Integration tests for all API endpoints
- Performance tests for critical paths
- Security testing for authentication and authorization
- Always run tests before marking features complete

## Deployment Considerations

- Use environment variables for configuration
- Never commit secrets or API keys
- Background services should auto-restart
- Health check endpoints at `/health`
- Monitoring with structured logging
- all pip and python commands in venv mandatory