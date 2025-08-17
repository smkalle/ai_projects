# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MediPulse is an agentic AI workflow system for extracting structured data from medical documents using LangGraph and OpenAI's GPT-4o vision model. It implements conditional routing based on document type and includes validation, adaptive reasoning, and schema-based extraction.

## Development Commands

### Setup
```bash
# Install dependencies
make install

# Install in development mode
make install-dev

# Set up environment
cp .env.example .env
# Add OPENAI_API_KEY to .env file
```

### Testing
```bash
# Run full test suite
make test

# Run specific test
python -m pytest tests/test_medipulse.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=xml
```

### Code Quality
```bash
# Lint code
make lint

# Format code  
make format

# Check formatting (CI validation)
black --check .
```

### Running the Application
```bash
# Run demo
make demo

# Direct execution
python src/medipulse.py

# Process a document
python examples/demo.py
```

## Architecture

### Core Components

1. **MediPulse Class** (`src/medipulse.py`): Main orchestrator using LangGraph StateGraph for workflow management. Key methods:
   - `process_document()`: Entry point for document processing
   - `_build_workflow()`: Constructs the agentic workflow graph
   - Nodes: document_classification, structure_extraction, adaptive_reasoning, schema_validation

2. **State Management**: Uses `MediState` TypedDict to track:
   - `image_base64`: Input document
   - `doc_classification`: Document type and confidence
   - `extracted_data`: Structured medical data
   - `validation_result`: Schema validation results
   - `processing_steps`: Audit trail

3. **Schema Models** (Pydantic):
   - `DocumentType`: Classification results
   - `ExtractedData`: Medical data structure
   - `ValidationResult`: Data quality metrics

### Workflow Flow
```
Start → Document Classification → Structure Extraction → Adaptive Reasoning → Schema Validation → End
                ↓ (if unsupported)
            Handle Other → End
```

### Document Types Supported
- `lab_report`: Laboratory test results
- `patient_intake`: Registration and demographics
- `prescription`: Medication orders
- `discharge_summary`: Hospital discharge documentation

## Key Dependencies

- **langgraph**: Workflow orchestration
- **langchain-openai**: OpenAI integration
- **pydantic**: Data validation and schemas
- **python-dotenv**: Environment management
- **pillow/pdf2image**: Image processing

## Environment Configuration

Required environment variables in `.env`:
- `OPENAI_API_KEY`: OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4o)
- `DEBUG`: Debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)

## MVP Considerations

The MVP specification (`MVP_SPEC.md`) outlines enterprise requirements including:
- HIPAA compliance measures
- Human-in-the-loop verification
- RESTful API with FastAPI
- PostgreSQL for data storage
- React/Next.js frontend
- Docker containerization
- OAuth 2.0/JWT authentication

Current implementation is a prototype focused on core extraction logic. Enterprise features (authentication, API endpoints, frontend) are planned for MVP development.

## Testing Strategy

- Unit tests in `tests/test_medipulse.py`
- Test data generation: `examples/create_test_documents.py`
- CI/CD via GitHub Actions (`.github/workflows/ci.yml`)
- Multi-Python version testing (3.8-3.11)
- Coverage reporting with Codecov

## Important Notes

- Prototype implementation - not production-ready without HIPAA compliance additions
- Requires active internet connection for OpenAI API
- Image inputs only (PDFs must be converted using pdf2image)
- Processing time varies based on document complexity