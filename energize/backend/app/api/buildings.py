"""Buildings management endpoints."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_buildings():
    """List all buildings."""
    return [
        {
            "id": "building-1",
            "name": "Tower A",
            "address": "123 Tech Park, San Jose",
            "area_sqft": 45000,
            "type": "Office",
            "current_consumption": 2847
        },
        {
            "id": "building-2", 
            "name": "Tower B",
            "address": "124 Tech Park, San Jose",
            "area_sqft": 38000,
            "type": "Office",
            "current_consumption": 2156
        }
    ]