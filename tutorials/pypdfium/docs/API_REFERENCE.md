# API Reference

## FastAPI Endpoints

Base URL: `http://localhost:8000`

### Authentication

Currently, the API uses API key authentication via environment variables. Future versions will support OAuth2.

---

### Document Management

#### Upload Document

```http
POST /documents/upload
```

Uploads a PDF document for processing.

**Request**:
- Content-Type: `multipart/form-data`
- Body:
  - `file`: PDF file (required)
  - `document_type`: String enum (optional)
    - Values: `regulatory`, `technical`, `environmental`, `grid`, `renewable`, `efficiency`, `market`, `policy`

**Response** (200 OK):
```json
{
  "document_id": "uuid-string",
  "filename": "document.pdf",
  "status": "processing",
  "document_type": "technical",
  "pages": 10,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Errors**:
- 400: Invalid file format
- 413: File too large (>50MB)
- 500: Processing error

**Example**:
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@solar_panel_specs.pdf" \
     -F "document_type=technical"
```

---

#### List Documents

```http
GET /documents
```

Returns all processed documents.

**Query Parameters**:
- `document_type`: Filter by type (optional)
- `limit`: Max results (default: 100)
- `offset`: Pagination offset (default: 0)

**Response** (200 OK):
```json
{
  "documents": [
    {
      "document_id": "uuid-string",
      "filename": "document.pdf",
      "document_type": "technical",
      "pages": 10,
      "chunks": 45,
      "uploaded_at": "2024-01-01T00:00:00Z",
      "status": "indexed"
    }
  ],
  "total": 15,
  "limit": 100,
  "offset": 0
}
```

---

#### Get Document Details

```http
GET /documents/{document_id}
```

Returns detailed information about a specific document.

**Response** (200 OK):
```json
{
  "document_id": "uuid-string",
  "filename": "document.pdf",
  "document_type": "technical",
  "pages": 10,
  "chunks": 45,
  "metadata": {
    "title": "Solar Panel Installation Guide",
    "processing_time": 28.5,
    "ocr_confidence": 0.95
  },
  "status": "indexed",
  "uploaded_at": "2024-01-01T00:00:00Z"
}
```

---

#### Delete Document

```http
DELETE /documents/{document_id}
```

Removes a document and its vectors from the system.

**Response** (200 OK):
```json
{
  "message": "Document deleted successfully",
  "document_id": "uuid-string"
}
```

---

### Query Interface

#### Query Documents

```http
POST /query
```

Performs intelligent search across indexed documents.

**Request Body**:
```json
{
  "query": "What are the safety requirements for solar panel installation?",
  "document_types": ["technical", "regulatory"],  // optional
  "max_results": 5,  // optional, default: 5
  "include_sources": true  // optional, default: true
}
```

**Response** (200 OK):
```json
{
  "answer": "According to the documents, solar panel installation requires...",
  "confidence": 0.92,
  "sources": [
    {
      "document_id": "uuid-string",
      "document_name": "solar_installation.pdf",
      "page_number": 15,
      "relevance_score": 0.95,
      "excerpt": "Safety requirements include..."
    }
  ],
  "metadata": {
    "query_time": 2.3,
    "iterations": 1,
    "rewritten_query": null,
    "document_type_detected": "technical"
  }
}
```

---

#### Advanced Query

```http
POST /query/advanced
```

Performs query with additional control parameters.

**Request Body**:
```json
{
  "query": "Compare wind turbine efficiency across different manufacturers",
  "filters": {
    "document_types": ["technical", "market"],
    "date_range": {
      "start": "2023-01-01",
      "end": "2024-12-31"
    }
  },
  "options": {
    "relevance_threshold": 0.8,
    "max_iterations": 5,
    "enable_rewriting": true,
    "return_embeddings": false
  }
}
```

---

### System Endpoints

#### Health Check

```http
GET /health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "qdrant": "connected",
    "openai": "connected"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

#### Statistics

```http
GET /stats
```

Returns system usage statistics.

**Response** (200 OK):
```json
{
  "documents": {
    "total": 150,
    "by_type": {
      "technical": 45,
      "regulatory": 30,
      "environmental": 25
    }
  },
  "queries": {
    "total": 1250,
    "today": 45,
    "average_response_time": 2.8
  },
  "storage": {
    "vectors": 6750,
    "size_mb": 128.5
  }
}
```

---

## WebSocket API

Connect to: `ws://localhost:8000/ws`

### Events

#### Document Processing Status

```json
{
  "event": "document:processing",
  "data": {
    "document_id": "uuid-string",
    "status": "ocr_in_progress",
    "progress": 45,
    "current_page": 5,
    "total_pages": 10
  }
}
```

#### Query Progress

```json
{
  "event": "query:progress",
  "data": {
    "stage": "retrieving",
    "message": "Searching relevant documents...",
    "progress": 30
  }
}
```

---

## Python Client SDK

### Installation

```bash
pip install energy-document-ai-client
```

### Usage

```python
from energy_doc_ai import Client

# Initialize client
client = Client(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Upload document
doc_id = client.upload_document(
    file_path="solar_specs.pdf",
    document_type="technical"
)

# Query documents
response = client.query(
    "What are the maintenance requirements?",
    document_types=["technical"]
)

print(response.answer)
for source in response.sources:
    print(f"- {source.document_name}: {source.excerpt}")

# Advanced query with options
response = client.advanced_query(
    query="Compare efficiency metrics",
    relevance_threshold=0.8,
    max_iterations=3
)
```

---

## Rate Limits

- Document uploads: 10 per minute
- Queries: 100 per minute
- Document listings: 200 per minute

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid API key |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource doesn't exist |
| 413 | Payload Too Large - File exceeds limit |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Dependency down |

## Pagination

All list endpoints support pagination:

```http
GET /endpoint?limit=20&offset=40
```

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 40,
    "has_more": true
  }
}
```