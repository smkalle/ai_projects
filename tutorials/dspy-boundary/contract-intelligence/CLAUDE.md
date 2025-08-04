# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Contract Intelligence Platform - An AI-powered contract analysis system built with Streamlit and DSPy for legal document processing, risk assessment, and compliance checking.

## Key Commands

### Development Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Copy environment file
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Running the Application
```bash
# Run Streamlit app
streamlit run app/main.py

# Run with specific port
streamlit run app/main.py --server.port 8501

# Run tests
pytest

# Run specific test category
pytest -m unit
pytest -m integration

# Format code
black .
ruff check .

# Type checking
mypy app core services models
```

## Architecture

### Directory Structure
- `app/` - Streamlit frontend application
  - `main.py` - Entry point with home page
  - `pages/` - Multi-page app structure (numbered for ordering)
  - `components/` - Reusable UI components
- `core/` - Business logic and DSPy modules
  - `modules/` - DSPy modules for contract analysis
  - `signatures/` - DSPy signatures for prompts
- `services/` - Service layer (storage, auth, LLM, cache)
- `models/` - Data models and schemas
- `config/` - Configuration and settings
- `tests/` - Test suite organized by type

### Key Technologies
- **Frontend**: Streamlit for rapid UI development
- **AI Framework**: DSPy for structured LLM interactions
- **Document Processing**: PyMuPDF, python-docx, pytesseract
- **Database**: SQLAlchemy + PostgreSQL/SQLite
- **Caching**: Redis for performance
- **Authentication**: JWT tokens with python-jose

### DSPy Module Pattern
```python
class ContractAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought("document -> analysis")
    
    def forward(self, document: str):
        return self.prog(document=document)
```

### Session State Management
- Use `st.session_state` for cross-page data persistence
- Key states: `authenticated`, `user_id`, `uploaded_files`, `analysis_results`

## Development Workflow

### Adding New Features
1. Update todo list in implementation_checklist.md
2. Create feature branch
3. Implement backend logic in `core/` first
4. Add service layer in `services/`
5. Create UI in `app/pages/`
6. Write tests in `tests/`
7. Update documentation

### Testing Strategy
- Unit tests for DSPy modules and services
- Integration tests for workflows
- Use fixtures for contract samples
- Mock LLM calls in tests

### Performance Considerations
- Use Redis caching for LLM responses
- Implement async processing for large documents
- Stream responses for better UX
- Paginate large result sets

## Common Tasks

### Creating a New DSPy Module
1. Create module in `core/modules/`
2. Define signature in `core/signatures/`
3. Add prompts to `config/prompts.yaml`
4. Create service wrapper in `services/`
5. Add tests

### Adding a New Page
1. Create numbered file in `app/pages/` (e.g., `6_📊_New_Feature.py`)
2. Use consistent page structure with st.set_page_config
3. Check session state for required data
4. Add navigation in main.py if needed

### Handling File Uploads
- Validate file type and size in UI
- Process in service layer
- Store in configured storage (local/S3)
- Track in session state

## Important Notes

- Always check `settings.enable_*` flags before using features
- Use structured logging with loguru
- Follow type hints for better code clarity
- Keep UI responsive with progress indicators
- Handle errors gracefully with user-friendly messages

## Environment Variables

Critical variables that must be set:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - For LLM operations
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - For session security
- `JWT_SECRET_KEY` - For authentication

## Deployment

- Use Docker for containerization (Dockerfile in docker/)
- Configure reverse proxy for production
- Set up SSL certificates
- Enable monitoring with prometheus metrics
- Use environment-specific .env files