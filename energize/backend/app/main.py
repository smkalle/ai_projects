"""Main FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.config import get_settings
from app.database import init_db, close_db
from app.api import auth, buildings, sensors, energy, alerts, reports
from app.core.middleware import RateLimitMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting Energize backend...")
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Energize backend...")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["auth"])
app.include_router(buildings.router, prefix=f"{settings.api_v1_prefix}/buildings", tags=["buildings"])
app.include_router(sensors.router, prefix=f"{settings.api_v1_prefix}/sensors", tags=["sensors"])
app.include_router(energy.router, prefix=f"{settings.api_v1_prefix}/energy", tags=["energy"])
app.include_router(alerts.router, prefix=f"{settings.api_v1_prefix}/alerts", tags=["alerts"])
app.include_router(reports.router, prefix=f"{settings.api_v1_prefix}/reports", tags=["reports"])

# AI-powered endpoints
from app.api import ai
app.include_router(ai.router, prefix=f"{settings.api_v1_prefix}/ai", tags=["ai"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
        }
    )