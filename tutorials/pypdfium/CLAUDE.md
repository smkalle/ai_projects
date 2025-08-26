# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
# Install dependencies
make install          # Basic dependencies
make install-dev      # Include dev tools (pytest, black, flake8, mypy)

# Start Qdrant vector database (required)
make start-qdrant     # Or: docker run -d -p 6333:6333 -v ./qdrant_data:/qdrant/storage qdrant/qdrant

# Configure environment
cp .env.example .env
# Edit .env with OPENAI_API_KEY (required)
```

### Running the Application
```bash
# Run modes
make run-ui           # Streamlit UI only (port 8501)
make run-api          # FastAPI only (port 8000)
make run-both         # Both services

# Alternative: Direct Python
python app/main.py --mode ui/api/both
```

### Testing & Quality
```bash
make test             # Run all tests
pytest tests/test_rag.py -v  # Run specific test
make test-coverage    # Generate coverage report

make lint             # Run flake8 + mypy
make format           # Auto-format with black + isort
```

### Docker Operations
```bash
make docker-build     # Build images
make docker-run       # Start with docker-compose
make docker-stop      # Stop containers
```

### Cleanup
```bash
make clean            # Remove Python cache files
make clean-data       # Remove processed data and Qdrant storage
```

## Architecture Overview

### Core Processing Pipeline

This system implements a sophisticated RAG pipeline optimized for energy sector PDFs with figures and tables:

```
PDF → pypdfium2 Rendering → GPT-4o OCR → Text Chunks → Embeddings → Qdrant Storage
                                                                          ↓
User Query → LangGraph Agent → Retrieval → Relevance Check → Query Rewrite (if needed)
                                                ↓
                                        GPT-4o Answer Generation
```

### Key Components & Workflow

#### 1. PDF Processing (`app/models/pdf_processor.py`)
- **EnergyPDFProcessor**: Renders PDF pages at configurable DPI (default 300) using pypdfium2
- Sends base64-encoded images to GPT-4o with energy-specific prompts
- Preserves tables, figures, technical specifications, and regulatory references
- Critical methods: `render_page_to_image()`, `ocr_page_with_gpt4o()`, `extract_text_from_pdf()`

#### 2. Vector Storage (`app/models/rag_system.py`)
- **EnergyRAGSystem**: Manages Qdrant vector database operations
- Uses OpenAI text-embedding-3-small for embeddings
- Chunks text with RecursiveCharacterTextSplitter (800 chars, 100 overlap)
- Stores metadata: document_name, document_type, chunk_index, timestamp
- Key methods: `process_and_store_document()`, `similarity_search()` with filtering

#### 3. Agentic Workflow (`app/models/agent_workflow.py`)
- **EnergyDocumentAgent**: LangGraph state machine for adaptive retrieval
- States: retrieve → evaluate → rewrite/generate → summarize_context → answer
- Automatic query rewriting if relevance < 0.75 (max 3 iterations)
- Query classification for document type filtering (solar, wind, grid, regulatory, safety)
- Critical flow: `process_query()` orchestrates the entire workflow

#### 4. API Layer (`app/api/endpoints.py`)
- FastAPI endpoints for document upload and querying
- Handles multipart file uploads with background processing
- Document type classification on upload

#### 5. UI Layer (`app/ui/streamlit_app.py`)
- Streamlit interface for document upload and interactive querying
- Real-time processing status updates
- Document statistics display

### State Management

The LangGraph agent maintains state through `AgentState`:
- `query`, `original_query`, `rewritten_query`: Query evolution
- `retrieved_docs`: Vector search results
- `relevance_score`: Determines if rewrite needed (threshold: 0.75)
- `iteration_count`: Prevents infinite loops (max: 3)
- `document_type`: Classified category for filtering

### Energy Sector Optimizations

The system is specifically tuned for energy documents:
- **Document Types**: regulatory, technical, environmental, grid, renewable, efficiency, market, policy
- **Keyword Classification**: Maps queries to document types (see `ENERGY_KEYWORDS` in config.py)
- **OCR Prompts**: Energy-specific instructions for extracting technical specs, compliance requirements, safety protocols
- **Answer Generation**: Formatted for energy professionals with technical accuracy emphasis

### Configuration

Key settings in `.env` (see `app/utils/config.py`):
- `OPENAI_API_KEY`: Required for GPT-4o and embeddings
- `PDF_DPI`: OCR quality (higher = better but slower)
- `RELEVANCE_THRESHOLD`: Minimum score before query rewrite (0.6)
- `MAX_ITERATIONS`: Query rewrite attempts (3)
- `CHUNK_SIZE`/`CHUNK_OVERLAP`: Text splitting parameters

### Dependencies

Critical packages:
- **pypdfium2**: High-quality PDF rendering
- **langgraph**: State machine for agentic workflow
- **qdrant-client**: Vector database operations
- **langchain/langchain-openai**: RAG components
- **streamlit/fastapi**: UI and API frameworks