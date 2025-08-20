# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
FarmConnect is an AI-powered direct farmer-to-consumer marketplace that eliminates middlemen and provides real-time price intelligence. The application uses web scraping to monitor prices across major retail platforms (BigBasket, Zepto, Swiggy) and enables farmers to sell directly to consumers with 30-40% cost savings.

## Commands

### Development Environment Setup
```bash
# Quick start with Docker (recommended)
cd farmconnect-prototype
docker-compose up -d

# Backend development (FastAPI)
cd farmconnect-prototype/backend
uv pip install -r requirements.txt  # Use uv for package management
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend development (React)
cd farmconnect-prototype/frontend
npm install
npm start

# Run both services without Docker
# Terminal 1: Backend
cd farmconnect-prototype/backend && uv run uvicorn main:app --reload
# Terminal 2: Frontend  
cd farmconnect-prototype/frontend && npm start
```

### Testing & Quality
```bash
# Backend tests
cd farmconnect-prototype/backend
uv run pytest

# Frontend tests
cd farmconnect-prototype/frontend
npm test

# Linting
cd farmconnect-prototype/frontend
npm run lint
```

### Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database: PostgreSQL on localhost:5432
- Redis Cache: localhost:6379

## Architecture

### Technology Stack
- **Frontend**: React 18 + TypeScript + Material-UI + Tailwind CSS
- **Backend**: FastAPI (Python) + SQLAlchemy + PostgreSQL + Redis
- **AI/Scraping**: BeautifulSoup + aiohttp for asynchronous web scraping
- **Authentication**: JWT-based with role-based access control (farmers/consumers)
- **Deployment**: Docker Compose for development, ready for Kubernetes

### Key Components

#### Backend Services (farmconnect-prototype/backend/app/services/)
- `scraper_service.py`: AI-powered web scraping with product matching algorithms
- Real-time price monitoring with 5-minute refresh cycles
- Anti-detection mechanisms with rotating user agents

#### Frontend Structure (farmconnect-prototype/frontend/src/)
- `App.tsx`: Main application entry with routing
- `pages/PriceComparison.tsx`: Real-time price comparison dashboard
- React Query for server state management
- WebSocket integration for live updates

#### Database Design
- PostgreSQL with optimized schemas for farmers, products, and prices
- Redis for session management and price data caching
- Proper indexing for high-performance queries

### Business Logic
- **Price Intelligence**: Scrapes and compares prices across BigBasket, Zepto, Swiggy
- **Product Matching**: Smart algorithms to match farmer products with retail equivalents
- **User Roles**: Separate flows for farmers (sellers) and consumers (buyers)
- **Delivery Radius**: Location-based matching within farmer delivery zones

## Development Guidelines

### UI/UX Requirements
- Use Tailwind CSS for all new UI components
- Maintain Silicon Valley standards suitable for Series C funding
- Mobile-first responsive design
- Implement UI verification through HTTP server URLs before deployment

### Package Management
- Always use `uv` for Python package management and servers (no pip)
- Use npm for frontend packages
- Update requirements.txt and package.json when adding dependencies

### Server Management
- Don't assume servers are not running - check ports before starting
- Run servers in background when needed
- Use proper process management for long-running services

### Testing Workflow
1. Implement features in phases
2. Each phase MUST include unit tests and API integration tests
3. UI verification as HTTP URL with human signoff required
4. Use Streamlit for quick prototypes when appropriate

## Important Notes
- Market research data available in `/research/` directory
- Sample farmer database and price comparison analysis included
- Project targets ₹90.1B agricultural e-commerce market
- Focus on 30-40% consumer savings and 40% farmer profit increase
- Ready for hackathon submission with comprehensive documentation