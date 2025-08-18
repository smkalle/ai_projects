"""Energy data endpoints."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_energy_data():
    """Get energy consumption data."""
    return []