# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NGO Medical AI Assistant - A multimodal medical AI application for underserved communities. Built with FastAPI, Gradio, and OpenAI GPT-4o for medical image analysis and diagnostic reasoning.

## Architecture

- **Backend**: FastAPI application (`src/main.py`) with medical AI analysis endpoints
- **Demo Interface**: Gradio interface (`src/gradio_demo.py`) for rapid prototyping
- **Models**: Medical knowledge base and confidence calculators in `src/models/`
- **Deployment**: Docker Compose stack with Redis caching and Nginx reverse proxy
- **Frontend**: HTML templates with Tailwind CSS in `frontend/` directory

## Key Development Commands

### Setup & Installation

```bash
# Create virtual environment and install dependencies
python -m venv medai-env
source medai-env/bin/activate  # On Windows: medai-env\Scripts\activate
pip install -r requirements.txt

# For minimal Gradio demo
pip install -r requirements-gradio.txt

# Configure environment
cp config/.env.example config/.env
# Edit config/.env with API keys
```

### Run Application

```bash
# FastAPI server (production-ready)
python src/main.py
# Access at http://localhost:8000

# Gradio demo (rapid prototyping)
python src/gradio_demo.py
# Access at http://localhost:7860

# Docker deployment
docker-compose up --build
# Access at http://localhost:8000
```

### Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/ --cov-report=xml

# Run specific test file
pytest tests/test_main.py

# Run with verbose output
pytest -v tests/
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking
mypy src/
```

## API Structure

The FastAPI application exposes these key endpoints:

- `POST /analyze`: Multimodal medical image analysis
- `POST /triage`: Emergency triage assessment
- `GET /health`: Health check endpoint
- `POST /chat`: Medical Q&A chat interface

## Configuration

- **Environment Variables**: Set in `config/.env` (copy from `.env.example`)
  - `OPENAI_API_KEY`: Required for GPT-4o vision
  - `HUGGINGFACE_API_TOKEN`: For fallback models
  - `DEBUG`: Enable debug mode
  - `LOG_LEVEL`: Logging verbosity

- **Model Configuration**: `config/model_config.yaml` contains AI model settings
  - Primary model: GPT-4o
  - Fallback: LLaVA-Med
  - Confidence thresholds and safety settings

## Medical AI Components

- **Multimodal Analysis**: Combines image + text for diagnostic insights
- **Chain-of-Thought**: Step-by-step medical reasoning in `src/models/`
- **Confidence Scoring**: Uncertainty quantification in `src/utils/confidence_calculator.py`
- **Medical Knowledge Base**: Domain-specific knowledge in `src/models/medical_knowledge_base.py`

## Docker Deployment

The project uses Docker Compose with three services:
1. `medai-app`: Main FastAPI application
2. `redis`: Caching layer for performance
3. `nginx`: Reverse proxy and static file serving

## Testing Strategy

- Unit tests for medical reasoning logic
- Integration tests for API endpoints
- Mock external API calls for reliability
- Test medical edge cases and safety features

## Important Constraints

1. **Medical Ethics**: Always include disclaimers; never provide definitive diagnoses
2. **Data Privacy**: No patient data should be logged or stored without encryption
3. **API Rate Limits**: Implement caching to minimize API calls
4. **Image Processing**: Limit image size to 512x512 for performance
5. **Confidence Thresholds**: Require 70%+ confidence for any medical insights

## Common Development Tasks

### Add New Medical Analysis Feature
1. Create model in `src/models/`
2. Add API endpoint in `src/api/`
3. Update Gradio interface if needed
4. Write tests in `tests/`
5. Update Docker configuration if dependencies change

### Debug Medical Reasoning
1. Check logs in `logs/` directory
2. Enable DEBUG mode in `.env`
3. Use Gradio interface for interactive testing
4. Review chain-of-thought steps in API response

### Deploy to Production
1. Run tests: `pytest tests/`
2. Build Docker image: `docker build -t medai-assistant .`
3. Deploy with Docker Compose: `docker-compose up -d`
4. Monitor health endpoint: `/health`