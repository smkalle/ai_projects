"""Alerts endpoints."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_alerts():
    """Get alerts."""
    return []