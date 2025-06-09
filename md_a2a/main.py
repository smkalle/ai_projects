"""Main FastAPI application for Medical AI Assistant MVP."""

import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from .config import settings
from .database import init_database
from .routers import cases, health, photos, analytics, patients

# Configure logging based on settings
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create directories if they don't exist
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Medical AI Assistant MVP")

    # Initialize database
    await init_database()

    # Create necessary directories
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    if settings.backup_enabled:
        Path(settings.backup_dir).mkdir(parents=True, exist_ok=True)
    if settings.log_file:
        Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Medical AI Assistant MVP")


# Create FastAPI application
app = FastAPI(
    title="Medical AI Assistant MVP",
    description="AI-powered medical triage and first-aid guidance for remote healthcare",
    version="0.2.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(health.router)
app.include_router(cases.router)
app.include_router(photos.router)
app.include_router(analytics.router)
app.include_router(patients.router)

# Web interface routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/assess", response_class=HTMLResponse)
async def assess_page(request: Request):
    """Assessment page."""
    return templates.TemplateResponse("assess.html", {"request": request})

@app.get("/dosage", response_class=HTMLResponse)
async def dosage_page(request: Request):
    """Dosage calculator page."""
    return templates.TemplateResponse("dosage.html", {"request": request})

@app.get("/cases", response_class=HTMLResponse)
async def cases_page(request: Request):
    """Cases management page."""
    return templates.TemplateResponse("cases.html", {"request": request})

@app.get("/photos")
async def photos_page(request: Request):
    """Photo upload and analysis page."""
    return templates.TemplateResponse("photos.html", {"request": request})

@app.get("/analytics")
async def analytics_page(request: Request):
    """Analytics dashboard page."""
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/patients")
async def patients_page(request: Request):
    """Patient management page."""
    return templates.TemplateResponse("patients.html", {"request": request})

# Print configuration on startup
if __name__ == "__main__":
    print("\nMedical AI Assistant MVP - Configuration Summary")
    print("=" * 48)
    print(f"Environment: {settings.environment}")
    print(f"Debug Mode: {settings.debug}")
    print(f"AI Model: {settings.openai_model}")
    print(f"AI Fallback: {settings.ai_fallback_enabled}")
    print(f"AI Mock Mode: {settings.dev_mock_ai}")
    print(f"Cost Optimization: {settings.ai_cost_optimization}")
    print(f"API Host: {settings.api_host}:{settings.api_port}")
    print(f"Database: {settings.database_url}")
    print(f"Upload Directory: {settings.upload_dir}")
    print(f"Log Level: {settings.log_level}")
    print("=" * 48)

    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
