"""Authentication endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    """User login endpoint."""
    # Demo authentication
    if request.username == "demo@energize.io" and request.password == "demo123":
        return {
            "access_token": "demo-jwt-token",
            "token_type": "bearer",
            "user": {
                "email": request.username,
                "role": "admin"
            }
        }
    return {"error": "Invalid credentials"}