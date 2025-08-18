# ⚡ Energize - Smart Building Energy Analytics Platform

A comprehensive SaaS platform for real-time energy monitoring, optimization, and analytics for smart buildings.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL with TimescaleDB extension
- Redis
- Node.js 18+ (for React frontend)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/energize.git
cd energize
```

2. **Set up environment variables**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

The platform will be available at:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- Streamlit Dashboard: http://localhost:8501
- React Frontend: http://localhost:3000

### Demo Credentials
- Email: `demo@energize.io`
- Password: `demo123`

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI (Python 3.11)
- PostgreSQL + TimescaleDB
- Redis for caching
- SQLAlchemy ORM
- Pydantic for validation

**Frontend:**
- Streamlit (rapid prototyping)
- React.js with TypeScript
- Tailwind CSS
- Recharts for visualizations

**Infrastructure:**
- Docker containerization
- Kubernetes ready
- GitHub Actions CI/CD

## 📊 Features

### MVP Features (Current Release)
- ✅ Real-time energy monitoring
- ✅ AI-powered optimization with LangGraph agents
- ✅ Multi-tenant architecture
- ✅ Anomaly detection algorithms
- ✅ Alert management system
- ✅ Interactive dashboards with Streamlit
- ✅ RESTful API with FastAPI
- ✅ GPT-4o-mini integration for intelligent insights

### Future Roadmap
- 🔄 V1: Advanced ML optimization & Demand Response
- 🔄 V2: Cybersecurity for Energy Infrastructure
- 🔄 V3: Unified Energy Intelligence Platform

## 🛠️ Development

### Backend Development

```bash
cd backend
uv pip install -e .[dev]
uv run uvicorn app.main:app --reload
```

### Running Tests

```bash
cd backend
uv run pytest tests/ -v
uv run pytest tests/ --cov=app
```

### Code Quality

```bash
uv run ruff check .
uv run ruff format .
uv run mypy app/
```

### Database Migrations

```bash
# Initialize database
psql -U postgres -f backend/scripts/init_db.sql

# Run Alembic migrations
cd backend
uv run alembic upgrade head
```

## 📚 API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Key Endpoints

```http
POST   /api/v1/auth/login              # User authentication
GET    /api/v1/buildings               # List buildings
GET    /api/v1/buildings/{id}/energy   # Get energy data
POST   /api/v1/sensors/readings        # Submit sensor data
GET    /api/v1/alerts                  # Get alerts
GET    /api/v1/reports/energy          # Generate reports
```

## 🔧 Configuration

Key configuration options in `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/energize
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

## 📈 Performance Targets

- **Data Ingestion**: 1,000+ readings/second
- **API Response**: <200ms (p95)
- **Dashboard Load**: <2 seconds
- **Concurrent Users**: 100+
- **Uptime SLA**: 99.5%

## 🔒 Security

- JWT-based authentication
- Row-level security for multi-tenancy
- Rate limiting (100 req/min)
- Input validation with Pydantic
- SQL injection prevention
- HTTPS in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Contact: support@energize.io

## 🎯 Project Status

**Current Phase**: MVP Complete
**Status**: Ready for community contributions
**Mission**: Save the planet through intelligent energy management 🌍

---

Built with ❤️ for a sustainable future