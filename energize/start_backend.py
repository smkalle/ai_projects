#!/usr/bin/env python3
"""
Backend server for Energize AI platform demo.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Energize AI Platform",
    version="0.1.0",
    description="AI-powered energy optimization platform"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

# Auth endpoints
@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    if request.username == "demo@energize.io" and request.password == "demo123":
        return {
            "access_token": "demo-jwt-token",
            "token_type": "bearer",
            "user": {"email": request.username, "role": "admin"}
        }
    return {"error": "Invalid credentials"}

# Buildings endpoints  
@app.get("/api/v1/buildings")
async def list_buildings():
    return [
        {
            "id": "tower-a",
            "name": "Tower A", 
            "address": "123 Tech Park, San Jose",
            "current_consumption": 2847,
            "area_sqft": 45000
        },
        {
            "id": "tower-b",
            "name": "Tower B",
            "address": "124 Tech Park, San Jose", 
            "current_consumption": 2156,
            "area_sqft": 38000
        }
    ]

# AI Optimization endpoints
@app.post("/api/v1/ai/simulate-optimization")
async def simulate_optimization(building_id: str, consumption: float):
    """Simulate AI optimization results for demo."""
    baseline = consumption
    optimized = consumption * 0.7  # 30% reduction
    savings = baseline - optimized
    
    return {
        "building_id": building_id,
        "baseline_consumption": baseline,
        "optimized_consumption": optimized,
        "energy_saved": savings,
        "carbon_reduced": savings * 0.0005,  # kg CO2 per kWh
        "cost_savings": savings * 0.15,  # $0.15 per kWh
        "recommendations": [
            f"Reduce consumption by {savings:.0f} kWh daily",
            f"Save ${savings * 0.15:.0f} monthly cost", 
            f"Prevent {savings * 0.0005:.2f} kg CO2 emissions daily"
        ],
        "optimization_actions": [
            "🔧 Optimize HVAC scheduling (40% of savings)",
            "💡 Implement smart lighting controls",
            "📊 Enable demand response participation",
            "⏰ Schedule loads to off-peak hours"
        ]
    }

@app.post("/api/v1/ai/chat")
async def chat(request: dict):
    """AI chat assistant demo."""
    query = request.get("query", "").lower()
    
    responses = {
        "reduce": "To reduce energy consumption: 1) Optimize HVAC scheduling based on occupancy patterns, 2) Use smart lighting with motion sensors, 3) Implement demand response programs during peak hours, 4) Install energy-efficient equipment.",
        "cost": "Save costs by: 1) Shifting flexible loads to off-peak hours, 2) Implementing energy storage systems, 3) Participating in utility rebate programs, 4) Using predictive maintenance to avoid equipment failures.",
        "carbon": "Reduce carbon footprint: 1) Maximize renewable energy usage during high-generation periods, 2) Schedule energy-intensive tasks during low-carbon grid hours, 3) Improve building insulation, 4) Use electric heat pumps instead of gas heating.",
        "hvac": "HVAC optimization tips: 1) Use setback temperatures when unoccupied, 2) Implement zone-based controls, 3) Regular filter maintenance, 4) Smart thermostats with occupancy sensors."
    }
    
    response = "I can help optimize your building's energy usage! Focus on HVAC optimization (40% of energy use), smart lighting, and load scheduling for maximum impact. What specific area would you like to improve?"
    
    for keyword, answer in responses.items():
        if keyword in query:
            response = answer
            break
    
    return {"response": response}

@app.get("/api/v1/ai/status")
async def ai_status():
    return {
        "status": "operational",
        "agents_active": ["orchestrator", "optimizer", "forecaster", "carbon_reducer"],
        "optimization_score": 94,
        "energy_saved_today": 1247,
        "response_time_ms": 45
    }

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "energize-ai-platform"}

@app.get("/")
async def root():
    return {
        "name": "Energize AI Platform",
        "version": "0.1.0", 
        "status": "operational",
        "mission": "Save the planet through intelligent energy management 🌍",
        "docs": "/docs"
    }

if __name__ == "__main__":
    print("🚀 Starting Energize AI Backend...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🌍 Mission: Save the planet through intelligent energy optimization! 🌱")
    
    uvicorn.run(
        "start_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )