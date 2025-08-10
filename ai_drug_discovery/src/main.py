"""
FastAPI Backend for Rare Disease Drug Repurposing AI System
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from src.config import settings
from src.api.routes import router as api_router
from src.core.database import DatabaseManager
from src.agents.coordinator import CoordinatorAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
db_manager = None
coordinator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global db_manager, coordinator

    # Startup
    logger.info("🚀 Starting Rare Disease Drug Repurposing AI System...")

    try:
        # Initialize database connections
        db_manager = DatabaseManager()
        await db_manager.initialize()

        # Initialize AI coordinator
        coordinator = CoordinatorAgent()
        await coordinator.initialize()

        logger.info("✅ System initialization completed successfully")

        yield

    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {e}")
        raise

    # Shutdown
    logger.info("🛑 Shutting down system...")
    if db_manager:
        await db_manager.close()
    if coordinator:
        await coordinator.cleanup()
    logger.info("✅ Shutdown completed")

# Create FastAPI app
app = FastAPI(
    title="Rare Disease Drug Repurposing AI",
    description="AI-powered drug repurposing system for rare diseases with citation-verified recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Rare Disease Drug Repurposing AI System",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connectivity
        db_status = "healthy" if db_manager and await db_manager.health_check() else "unhealthy"

        # Check AI coordinator
        coordinator_status = "healthy" if coordinator and coordinator.is_ready() else "unhealthy"

        overall_status = "healthy" if all([
            db_status == "healthy",
            coordinator_status == "healthy"
        ]) else "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": db_status,
                "coordinator": coordinator_status,
                "api": "healthy"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )