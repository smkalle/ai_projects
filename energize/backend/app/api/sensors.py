"""Sensors endpoints."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_sensors():
    """List all sensors."""
    return []