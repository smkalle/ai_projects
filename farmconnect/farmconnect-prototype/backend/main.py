
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from contextlib import asynccontextmanager
import asyncio
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import auth, farmers, products, price_comparison, orders
from app.services.scraper_service import ScraperService
from app.services.price_service import PriceService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
scraper_service = ScraperService()
price_service = PriceService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting FarmConnect API...")

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Start background tasks
    asyncio.create_task(scraper_service.start_periodic_scraping())

    yield

    # Shutdown
    logger.info("Shutting down FarmConnect API...")
    await scraper_service.stop()

# Create FastAPI app
app = FastAPI(
    title="FarmConnect API",
    description="AI-Powered Direct Farmer-to-Consumer Marketplace",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://farmconnect.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(farmers.router, prefix="/api/farmers", tags=["farmers"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(price_comparison.router, prefix="/api/price-comparison", tags=["price-comparison"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])

@app.get("/")
async def root():
    return {"message": "FarmConnect API v1.0.0", "status": "operational"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "scraper": await scraper_service.health_check(),
            "price_service": price_service.health_check()
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
