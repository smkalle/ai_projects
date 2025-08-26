"""
Pydantic schemas for Energy Document AI API
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class DocumentMetadata(BaseModel):
    """Document metadata schema"""
    name: str
    type: str
    size_bytes: int
    upload_timestamp: str
    document_id: str
    chunks_count: Optional[int] = None

class QueryRequest(BaseModel):
    """Query request schema"""
    query: str = Field(..., min_length=1, max_length=1000, description="The question to ask")
    document_type: Optional[str] = Field(None, description="Filter by document type")
    max_results: int = Field(5, ge=1, le=20, description="Maximum number of results")
    include_metadata: bool = Field(False, description="Include detailed metadata in response")

class RetrievedDocument(BaseModel):
    """Retrieved document schema"""
    content: str
    score: float
    document_name: str
    document_type: str
    chunk_index: int
    metadata: Dict[str, Any]

class QueryResponse(BaseModel):
    """Query response schema"""
    query: str
    answer: str
    relevance_score: float
    retrieved_docs: List[RetrievedDocument]
    iterations: int
    document_type: str
    timestamp: str
    processing_time_ms: int
    confidence: Optional[str] = None

class DocumentUploadRequest(BaseModel):
    """Document upload request schema"""
    document_type: str = Field("energy", description="Type/category of the document")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class DocumentUploadResponse(BaseModel):
    """Document upload response schema"""
    success: bool
    message: str
    document_id: Optional[str] = None
    chunks_stored: Optional[int] = None
    processing_time_ms: Optional[int] = None
    estimated_cost: Optional[float] = None

class SearchRequest(BaseModel):
    """Search request schema"""
    query: str = Field(..., min_length=1, description="Search query")
    k: int = Field(5, ge=1, le=50, description="Number of results to return")
    document_type: Optional[str] = Field(None, description="Filter by document type")
    score_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum similarity score")

class SearchResponse(BaseModel):
    """Search response schema"""
    query: str
    results: List[RetrievedDocument]
    total_found: int
    timestamp: str
    search_time_ms: int

class SystemStats(BaseModel):
    """System statistics schema"""
    total_documents: int
    total_chunks: int
    document_types: Dict[str, int]
    collection_status: str
    last_updated: str

class SystemStatus(BaseModel):
    """System status schema"""
    status: str
    version: str
    uptime_seconds: float
    qdrant_connected: bool
    openai_connected: bool
    stats: SystemStats

class HealthCheck(BaseModel):
    """Health check schema"""
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    status_code: int
    timestamp: str
    details: Optional[str] = None

class ProcessingStatus(BaseModel):
    """Document processing status schema"""
    document_id: str
    status: str  # "queued", "processing", "completed", "failed"
    progress: float  # 0.0 to 1.0
    message: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

class BatchQueryRequest(BaseModel):
    """Batch query request schema"""
    queries: List[str] = Field(..., min_items=1, max_items=10)
    document_type: Optional[str] = None
    max_results_per_query: int = Field(5, ge=1, le=20)

class BatchQueryResponse(BaseModel):
    """Batch query response schema"""
    results: List[QueryResponse]
    total_queries: int
    successful_queries: int
    failed_queries: int
    total_processing_time_ms: int
