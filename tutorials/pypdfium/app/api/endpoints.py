"""
FastAPI endpoints for Energy Document AI
REST API for document processing and querying
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import tempfile
import os
import logging
from datetime import datetime
import asyncio

from models.pdf_processor import EnergyPDFProcessor
from models.rag_system import EnergyRAGSystem
from models.agent_workflow import EnergyDocumentAgent
from utils.config import settings
from utils.helpers import validate_pdf_file, calculate_file_hash

logger = logging.getLogger(__name__)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    document_type: Optional[str] = None
    max_results: int = 5

class QueryResponse(BaseModel):
    query: str
    answer: str
    relevance_score: float
    retrieved_docs: List[Dict[str, Any]]
    iterations: int
    document_type: str
    timestamp: str
    processing_time_ms: int

class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[str] = None
    chunks_stored: Optional[int] = None
    processing_time_ms: Optional[int] = None

class SystemStatus(BaseModel):
    status: str
    version: str
    total_documents: int
    total_chunks: int
    uptime_seconds: float

# Global components
app = FastAPI(
    title="Energy Document AI API",
    description="Advanced AI-powered document analysis for energy sector professionals",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for components
rag_system: Optional[EnergyRAGSystem] = None
agent: Optional[EnergyDocumentAgent] = None
start_time = datetime.now()

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global rag_system, agent

    try:
        # Initialize RAG system
        rag_system = EnergyRAGSystem(
            qdrant_url=settings.qdrant_host,
            qdrant_port=settings.qdrant_port,
            openai_api_key=settings.openai_api_key,
            collection_name=settings.collection_name
        )

        # Initialize agent
        agent = EnergyDocumentAgent(
            rag_system=rag_system,
            openai_api_key=settings.openai_api_key,
            model=settings.llm_model,
            max_iterations=settings.max_iterations
        )

        logger.info("API components initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise

def get_agent() -> EnergyDocumentAgent:
    """Dependency to get agent instance"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    return agent

def get_rag_system() -> EnergyRAGSystem:
    """Dependency to get RAG system instance"""
    if rag_system is None:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    return rag_system

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Energy Document AI API",
        "version": settings.app_version,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with component status"""
    try:
        # Check RAG system availability
        rag_status = "unknown"
        qdrant_status = "unknown"
        embeddings_status = "unknown"
        
        if rag_system:
            system_status = rag_system.get_status()
            qdrant_status = "connected" if system_status['qdrant_available'] else "disconnected"
            embeddings_status = "ready" if system_status['embeddings_available'] else "not_configured"
            rag_status = "operational" if system_status['fully_operational'] else "limited"
        
        # Check agent availability
        agent_status = "ready" if agent else "not_initialized"
        
        overall_status = "healthy" if (rag_status == "operational" and agent_status == "ready") else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "version": settings.app_version,
            "components": {
                "rag_system": rag_status,
                "qdrant_database": qdrant_status,
                "openai_embeddings": embeddings_status,
                "agent_workflow": agent_status
            },
            "capabilities": {
                "document_upload": rag_system is not None,
                "document_search": rag_system and rag_system.is_available(),
                "query_processing": agent is not None and rag_system and rag_system.is_available()
            }
        }
    except Exception as e:
        logger.error(f"Error in detailed health check: {e}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "version": settings.app_version,
            "error": str(e)
        }

@app.get("/status", response_model=SystemStatus)
async def get_system_status(rag: EnergyRAGSystem = Depends(get_rag_system)):
    """Get system status and statistics"""
    try:
        # Get system status first
        system_status = rag.get_status()
        stats = rag.get_document_stats()
        uptime = (datetime.now() - start_time).total_seconds()

        # Determine overall status
        if system_status['fully_operational']:
            status = "operational"
        elif system_status['qdrant_available'] and not system_status['embeddings_available']:
            status = "limited_no_embeddings"
        elif not system_status['qdrant_available'] and system_status['embeddings_available']:
            status = "limited_no_qdrant"
        else:
            status = "limited"

        return SystemStatus(
            status=status,
            version=settings.app_version,
            total_documents=stats.get('total_documents', 0),
            total_chunks=stats.get('total_points', 0),
            uptime_seconds=uptime
        )
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return SystemStatus(
            status="error",
            version=settings.app_version,
            total_documents=0,
            total_chunks=0,
            uptime_seconds=(datetime.now() - start_time).total_seconds()
        )

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: str = "energy",
    rag: EnergyRAGSystem = Depends(get_rag_system)
):
    """Upload and process a PDF document"""
    start_time = datetime.now()

    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Validate file
        is_valid, message = validate_pdf_file(tmp_file_path, settings.max_file_size_mb)
        if not is_valid:
            os.unlink(tmp_file_path)
            raise HTTPException(status_code=400, detail=f"Invalid file: {message}")

        # Calculate file hash for document ID
        document_id = calculate_file_hash(tmp_file_path)

        # Process document in background
        background_tasks.add_task(
            process_document_background,
            tmp_file_path,
            file.filename,
            document_type,
            document_id,
            rag
        )

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return DocumentUploadResponse(
            success=True,
            message=f"Document {file.filename} uploaded and queued for processing",
            document_id=document_id,
            processing_time_ms=int(processing_time)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

async def process_document_background(
    file_path: str, 
    filename: str, 
    document_type: str, 
    document_id: str,
    rag: EnergyRAGSystem
):
    """Background task for document processing"""
    try:
        # Initialize processor
        processor = EnergyPDFProcessor(
            openai_api_key=settings.openai_api_key,
            dpi=settings.pdf_dpi
        )

        # Extract text
        extracted_text = processor.extract_and_combine_text(file_path, document_type)

        # Store in RAG system
        chunks_stored = rag.process_and_store_document(
            text=extracted_text,
            document_name=filename,
            document_type=document_type,
            metadata={
                "document_id": document_id,
                "upload_timestamp": datetime.now().isoformat(),
                "file_size": os.path.getsize(file_path)
            }
        )

        logger.info(f"Successfully processed {filename}: {chunks_stored} chunks")

    except Exception as e:
        logger.error(f"Background processing failed for {filename}: {e}")
    finally:
        # Clean up temp file
        if os.path.exists(file_path):
            os.unlink(file_path)

@app.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    agent_instance: EnergyDocumentAgent = Depends(get_agent)
):
    """Process a query using the agentic RAG system"""
    start_time = datetime.now()

    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Check if system is fully operational
        rag_system = agent_instance.rag_system if agent_instance else None
        if rag_system and not rag_system.is_available():
            raise HTTPException(
                status_code=503, 
                detail="RAG system not fully operational. Check Qdrant database and OpenAI API configuration."
            )

        # Process query through agent
        result = agent_instance.process_query(request.query)

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return QueryResponse(
            query=request.query,
            answer=result['answer'],
            relevance_score=result['relevance_score'],
            retrieved_docs=result['retrieved_docs'],
            iterations=result['iterations'],
            document_type=result['document_type'],
            timestamp=result['timestamp'],
            processing_time_ms=int(processing_time)
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {e}")

@app.get("/documents/search")
async def search_documents(
    query: str,
    k: int = 5,
    document_type: Optional[str] = None,
    rag: EnergyRAGSystem = Depends(get_rag_system)
):
    """Search documents by similarity"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Check if system is available for search
        if not rag.is_available():
            raise HTTPException(
                status_code=503,
                detail="Search unavailable: RAG system not fully operational"
            )

        results = rag.similarity_search(
            query=query,
            k=k,
            document_type=document_type,
            score_threshold=0.5
        )

        return {
            "query": query,
            "results": results,
            "total_found": len(results),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

@app.get("/documents/stats")
async def get_document_statistics(rag: EnergyRAGSystem = Depends(get_rag_system)):
    """Get document collection statistics"""
    try:
        stats = rag.get_document_stats()
        return {
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {e}")

@app.get("/documents/types")
async def get_supported_document_types():
    """Get supported document types"""
    from ..utils.config import ENERGY_DOCUMENT_TYPES
    return {
        "document_types": ENERGY_DOCUMENT_TYPES,
        "default_type": "energy"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
