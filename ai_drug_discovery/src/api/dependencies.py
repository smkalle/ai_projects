"""
FastAPI dependencies for authentication, database, and services
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from src.core.database import get_database
from src.agents.coordinator import get_coordinator

# Security scheme (optional for demo)
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Get current user from API token (optional for demo mode)
    In production, implement proper JWT validation
    """
    # In demo mode, allow anonymous access
    return {"user_id": "demo_user", "permissions": ["read", "write"]}

async def require_auth(user = Depends(get_current_user)):
    """
    Require authentication (disabled in demo mode)
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Export commonly used dependencies
__all__ = ["get_database", "get_coordinator", "get_current_user", "require_auth"]