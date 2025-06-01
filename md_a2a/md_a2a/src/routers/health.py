"""Health check router for Medical AI Assistant MVP."""

import logging
import time
from datetime import datetime
from typing import Any, Dict

from openai import AsyncOpenAI
from fastapi import APIRouter, HTTPException

from ..config import settings
from ..database import DatabaseManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize OpenAI client for health checks
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint."""
    start_time = time.time()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": {}
    }
    
    # Database health check
    try:
        DatabaseManager.health_check()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}"
        }
    
    # AI service health check
    if settings.ai_fallback_enabled and not settings.dev_mock_ai:
        try:
            ai_start = time.time()
            response = await openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": "health check"}],
                max_tokens=1,
                timeout=5  # Short timeout for health check
            )
            ai_latency = (time.time() - ai_start) * 1000
            
            health_status["checks"]["ai_service"] = {
                "status": "healthy",
                "message": "AI service responding",
                "latency_ms": round(ai_latency, 2),
                "model": settings.openai_model
            }
        except Exception as e:
            health_status["checks"]["ai_service"] = {
                "status": "degraded",
                "message": f"AI service error: {str(e)}",
                "fallback_available": True
            }
    else:
        health_status["checks"]["ai_service"] = {
            "status": "disabled",
            "message": "AI service disabled or in mock mode",
            "fallback_available": True
        }
    
    # Configuration health check
    try:
        config_issues = []
        
        # Check critical settings
        if not settings.openai_api_key or settings.openai_api_key == "sk-your-openai-api-key-here":
            config_issues.append("OpenAI API key not configured")
        
        if settings.is_production and settings.debug:
            config_issues.append("Debug mode enabled in production")
        
        if config_issues:
            health_status["checks"]["configuration"] = {
                "status": "warning",
                "message": f"Configuration issues: {'; '.join(config_issues)}"
            }
        else:
            health_status["checks"]["configuration"] = {
                "status": "healthy",
                "message": "Configuration valid"
            }
    except Exception as e:
        health_status["checks"]["configuration"] = {
            "status": "unhealthy",
            "message": f"Configuration error: {str(e)}"
        }
    
    # Overall response time
    total_time = (time.time() - start_time) * 1000
    health_status["response_time_ms"] = round(total_time, 2)
    
    # Determine overall status
    check_statuses = [check["status"] for check in health_status["checks"].values()]
    if "unhealthy" in check_statuses:
        health_status["status"] = "unhealthy"
    elif "degraded" in check_statuses:
        health_status["status"] = "degraded"
    
    logger.info(f"Health check completed in {total_time:.0f}ms - Status: {health_status['status']}")
    
    return health_status


@router.get("/health/ready")
async def readiness_probe() -> Dict[str, Any]:
    """Kubernetes readiness probe - checks if service can handle requests."""
    try:
        # Check database connectivity
        DatabaseManager.health_check()
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Service ready to handle requests"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Service not ready: {str(e)}"
            }
        )


@router.get("/health/live")
async def liveness_probe() -> Dict[str, Any]:
    """Kubernetes liveness probe - checks if service is alive."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time(),
        "version": settings.app_version
    }


@router.get("/health/ai")
async def ai_health_check() -> Dict[str, Any]:
    """Detailed AI service health check."""
    if settings.dev_mock_ai:
        return {
            "status": "mocked",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "AI service is mocked for development",
            "fallback_available": True
        }
    
    if not settings.ai_fallback_enabled:
        return {
            "status": "disabled",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "AI service is disabled",
            "fallback_available": True
        }
    
    try:
        start_time = time.time()
        
        # Test AI service with a simple request
        response = await openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a health check assistant."},
                {"role": "user", "content": "Respond with 'OK' if you are working."}
            ],
            max_tokens=5,
            temperature=0,
            timeout=settings.openai_timeout
        )
        
        latency = (time.time() - start_time) * 1000
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "latency_ms": round(latency, 2),
            "model": settings.openai_model,
            "response": response.choices[0].message.content.strip(),
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
        }
        
    except Exception as e:
        if "rate" in str(e).lower():
            return {
                "status": "rate_limited",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "AI service rate limited",
                "error": str(e),
                "fallback_available": True
            }
        elif "timeout" in str(e).lower():
            return {
                "status": "timeout",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "AI service timeout",
                "error": str(e),
                "fallback_available": True
            }
        else:
            logger.error(f"AI health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "AI service error",
                "error": str(e),
                "fallback_available": True
            }


@router.get("/health/metrics")
async def health_metrics() -> Dict[str, Any]:
    """Health metrics for monitoring."""
    try:
        # Get database metrics
        db_stats = DatabaseManager.get_stats()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "total_cases": db_stats.get("total_cases", 0),
                "cases_today": db_stats.get("cases_today", 0),
                "pending_reviews": db_stats.get("pending_reviews", 0)
            },
            "ai_service": {
                "enabled": settings.ai_fallback_enabled,
                "model": settings.openai_model,
                "fallback_enabled": settings.ai_fallback_enabled,
                "cost_optimization": settings.ai_cost_optimization,
                "safety_mode": settings.ai_safety_mode
            },
            "configuration": {
                "environment": settings.environment,
                "debug": settings.debug,
                "version": settings.app_version,
                "cache_enabled": settings.enable_assessment_cache
            }
        }
    except Exception as e:
        logger.error(f"Error getting health metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get health metrics: {str(e)}"
        )
