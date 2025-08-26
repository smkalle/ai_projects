# Architecture Documentation

## System Overview

Energy Document AI is a sophisticated RAG (Retrieval-Augmented Generation) system designed specifically for processing complex energy sector PDFs. It combines multiple AI technologies to extract, index, and query information from technical documents.

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                   (Streamlit / FastAPI)                      │
└────────────────────┬───────────────────┬────────────────────┘
                     │                   │
                     ▼                   ▼
┌────────────────────────┐    ┌────────────────────────┐
│   Document Upload      │    │    Query Interface      │
│      Controller        │    │      Controller         │
└──────────┬─────────────┘    └──────────┬──────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────────────────────────────────────┐
│                  Core Processing Layer                │
├──────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │PDF Processor │  │  RAG System  │  │   Agent    │ │
│  │ (pypdfium2)  │  │   (Qdrant)   │  │ (LangGraph)│ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
└──────────────────────────────────────────────────────┘
                     │                   │
                     ▼                   ▼
┌────────────────────────┐    ┌────────────────────────┐
│    GPT-4o OCR API      │    │  OpenAI Embeddings     │
└────────────────────────┘    └────────────────────────┘
```

## Component Details

### 1. PDF Processor (`pdf_processor.py`)

**Purpose**: Convert PDF documents to searchable text using visual OCR.

**Key Features**:
- High-resolution rendering (configurable DPI, default 300)
- Page-by-page processing
- Energy sector context prompts
- Preserves tables, figures, and technical diagrams

**Workflow**:
1. Load PDF using pypdfium2
2. Render each page to high-resolution image
3. Convert image to base64
4. Send to GPT-4o with specialized prompts
5. Extract structured text with markdown formatting

**Class Structure**:
```python
class EnergyPDFProcessor:
    - __init__(openai_api_key, dpi)
    - render_page_to_image(pdf_path, page_num) -> Image
    - image_to_base64(image) -> str
    - ocr_page_with_gpt4o(base64_image, page_context) -> str
    - extract_text_from_pdf(pdf_path, document_type) -> Dict
```

### 2. RAG System (`rag_system.py`)

**Purpose**: Manage vector storage and retrieval of document chunks.

**Key Features**:
- Text chunking with configurable overlap
- OpenAI embeddings (text-embedding-3-small)
- Qdrant vector database integration
- Metadata-based filtering
- Document type classification

**Storage Schema**:
```json
{
  "id": "uuid",
  "vector": [0.1, 0.2, ...],
  "payload": {
    "document_name": "string",
    "document_type": "string",
    "chunk_index": "number",
    "chunk_text": "string",
    "timestamp": "ISO 8601",
    "text_length": "number"
  }
}
```

### 3. Agent Workflow (`agent_workflow.py`)

**Purpose**: Orchestrate intelligent query processing with adaptive retrieval.

**State Machine**:
```
START → Retrieve → Evaluate → Decision
                              ↙        ↘
                        Rewrite    Generate Answer
                            ↓            ↓
                        Retrieve        END
```

**Agent State**:
- `query`: Current query being processed
- `original_query`: User's original input
- `retrieved_docs`: Documents from vector search
- `relevance_score`: Quality metric (0.0-1.0)
- `iteration_count`: Rewrite attempts
- `document_type`: Classified category

**Decision Logic**:
- If relevance >= 0.75: Generate answer
- If relevance < 0.75 and iterations < max: Rewrite query
- If max iterations reached: Generate with available context

## Data Flow

### Document Processing Flow

1. **Upload**: User uploads PDF via UI
2. **Validation**: Check file type and size
3. **Processing**:
   - Extract metadata
   - Render pages with pypdfium2
   - OCR with GPT-4o
   - Chunk text
4. **Indexing**:
   - Generate embeddings
   - Store in Qdrant
   - Update document registry
5. **Confirmation**: Return success status

### Query Processing Flow

1. **Input**: User submits natural language query
2. **Classification**: Determine document type focus
3. **Retrieval**: Vector similarity search
4. **Evaluation**: Assess relevance of results
5. **Adaptation** (if needed):
   - Rewrite query for better results
   - Re-retrieve with new query
6. **Generation**: Create answer with context
7. **Response**: Return formatted answer with sources

## API Design

### REST Endpoints

```
POST /documents/upload
  - Multipart form upload
  - Returns: document_id, status

POST /query
  - JSON: {"query": "string"}
  - Returns: answer, sources, confidence

GET /documents
  - Returns: list of documents

DELETE /documents/{id}
  - Returns: deletion status

GET /health
  - Returns: system status
```

### WebSocket Events

```
document:processing - Processing status updates
query:progress - Query execution updates
error:system - System error notifications
```

## Security Considerations

1. **API Key Management**:
   - Environment variables for secrets
   - Never logged or exposed in UI

2. **Input Validation**:
   - File type restrictions
   - Size limitations
   - Query sanitization

3. **Rate Limiting**:
   - Request throttling
   - Cost management for API calls

4. **Data Privacy**:
   - Local vector storage option
   - No data persistence without consent

## Performance Optimization

### Caching Strategy
- Document embeddings cached
- Query results cached for 15 minutes
- Page renders cached during session

### Batch Processing
- Multiple pages processed concurrently
- Bulk embedding generation
- Parallel vector searches

### Resource Management
- Configurable DPI for memory/quality tradeoff
- Chunk size optimization
- Connection pooling for database

## Scalability Patterns

### Horizontal Scaling
- Stateless API servers
- Distributed Qdrant clusters
- Load balancer ready

### Vertical Scaling
- GPU acceleration for embeddings
- Increased memory for larger PDFs
- Higher DPI for better accuracy

## Error Handling

### Retry Logic
- Exponential backoff for API calls
- Automatic fallback for OCR failures
- Circuit breaker pattern

### Graceful Degradation
- Fallback to basic text extraction
- Cached responses when APIs unavailable
- Partial results on timeout

## Monitoring Points

- API call latency
- OCR accuracy metrics
- Query relevance scores
- Document processing times
- Vector search performance
- Memory usage patterns

## Configuration

Key settings in `config.py`:
- `PDF_DPI`: OCR quality (300 default)
- `CHUNK_SIZE`: Text splitting (800 chars)
- `MAX_ITERATIONS`: Query rewrites (3)
- `RELEVANCE_THRESHOLD`: Quality bar (0.75)
- `LLM_MODEL`: GPT model selection
- `EMBEDDING_MODEL`: Vector model