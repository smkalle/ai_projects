"""AI-powered energy optimization endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.ai.orchestrator import EnergyOrchestrator
from app.ai.config import AIConfig
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class OptimizationRequest(BaseModel):
    building_id: str
    current_consumption: float
    target_reduction: Optional[float] = 30.0

class ChatRequest(BaseModel):
    query: str
    building_id: Optional[str] = None

class OptimizationResponse(BaseModel):
    status: str
    building_id: str
    optimization_score: float
    recommendations: list
    anomalies_detected: int
    carbon_footprint: float
    actions: Dict[str, Any]
    error: Optional[str] = None

# Initialize AI components
ai_config = AIConfig()
orchestrator = EnergyOrchestrator(ai_config)

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_building_energy(request: OptimizationRequest):
    """
    Trigger AI optimization for a building.
    
    This endpoint uses LangGraph agents with GPT-4o-mini to:
    - Analyze current consumption patterns
    - Detect anomalies and inefficiencies
    - Generate optimization recommendations
    - Calculate carbon footprint reduction
    - Provide actionable insights
    """
    try:
        logger.info(f"Starting AI optimization for building {request.building_id}")
        
        result = await orchestrator.optimize_building(
            building_id=request.building_id,
            current_consumption=request.current_consumption
        )
        
        return OptimizationResponse(**result)
        
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI optimization failed: {str(e)}"
        )

@router.get("/insights/{building_id}")
async def get_ai_insights(building_id: str):
    """Get real-time AI insights for a building."""
    try:
        # Simulate real-time insights
        insights = {
            "building_id": building_id,
            "current_status": "optimized",
            "energy_score": 87,
            "recent_savings": "$1,247",
            "carbon_reduction": "2.3 tons",
            "active_optimizations": [
                "Smart HVAC scheduling active",
                "Peak shaving in progress",
                "Renewable energy maximized"
            ],
            "next_recommendations": [
                "Schedule equipment maintenance",
                "Install additional smart sensors",
                "Implement demand response program"
            ],
            "efficiency_trends": {
                "last_hour": "+12%",
                "last_day": "+8%",
                "last_week": "+15%"
            }
        }
        
        return insights
        
    except Exception as e:
        logger.error(f"Failed to get insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get AI insights: {str(e)}"
        )

@router.post("/chat")
async def energy_assistant(request: ChatRequest):
    """
    Chat with the AI energy assistant powered by GPT-4o-mini.
    
    The assistant can help with:
    - Energy optimization questions
    - Building efficiency analysis
    - Carbon footprint reduction
    - Equipment recommendations
    """
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model=ai_config.openai_model,
            temperature=0.1,
            max_tokens=500
        )
        
        # Enhanced prompt for energy expertise
        system_prompt = """
        You are an expert AI energy advisor for the Energize platform. You help users:
        - Optimize building energy consumption
        - Reduce carbon footprint
        - Save costs through smart energy management
        - Understand energy patterns and anomalies
        
        Provide practical, actionable advice focused on sustainability and cost savings.
        Keep responses concise but informative.
        """
        
        full_prompt = f"{system_prompt}\n\nUser Question: {request.query}"
        
        if request.building_id:
            full_prompt += f"\nBuilding Context: {request.building_id}"
        
        response = await llm.ainvoke(full_prompt)
        
        return {
            "response": response.content,
            "building_id": request.building_id,
            "query": request.query
        }
        
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI assistant unavailable: {str(e)}"
        )

@router.get("/status")
async def ai_system_status():
    """Get AI system status and health metrics."""
    return {
        "status": "operational",
        "model": ai_config.openai_model,
        "agents_active": [
            "energy_orchestrator",
            "anomaly_detector", 
            "optimizer",
            "forecaster",
            "carbon_reducer"
        ],
        "optimization_target": f"{ai_config.target_energy_reduction}%",
        "last_updated": "2024-01-15T10:30:00Z"
    }

@router.post("/simulate-optimization")
async def simulate_optimization(building_id: str, consumption: float):
    """Simulate optimization results for demo purposes."""
    try:
        # Quick simulation for demo
        baseline_consumption = consumption
        optimized_consumption = consumption * 0.7  # 30% reduction
        savings = baseline_consumption - optimized_consumption
        carbon_saved = savings * 0.0005  # kg CO2 per kWh
        
        return {
            "building_id": building_id,
            "baseline_consumption": baseline_consumption,
            "optimized_consumption": optimized_consumption,
            "energy_saved": savings,
            "carbon_reduced": carbon_saved,
            "cost_savings": savings * 0.15,  # $0.15 per kWh
            "recommendations": [
                f"Reduce consumption by {savings:.0f} kWh",
                f"Save ${savings * 0.15:.0f} monthly",
                f"Prevent {carbon_saved:.2f} kg CO2 emissions"
            ],
            "optimization_actions": [
                "Optimize HVAC scheduling",
                "Implement smart lighting",
                "Enable demand response",
                "Schedule loads to off-peak hours"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simulation failed: {str(e)}"
        )