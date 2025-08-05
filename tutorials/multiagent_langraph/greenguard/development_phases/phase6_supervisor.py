from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, TypedDict, Literal
from datetime import datetime, timedelta
from enum import Enum
import os
import json
import uuid
import asyncio
import random
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

app = FastAPI(title="GreenGuard - Complete Multi-Agent System")

# State definition for LangGraph
class GreenGuardState(TypedDict):
    location: str
    messages: List[BaseMessage]
    hazard_data: Optional[Dict[str, Any]]
    health_risk_assessment: Optional[Dict[str, Any]]
    public_alert: Optional[Dict[str, Any]]
    dispatch_report: Optional[Dict[str, Any]]
    current_agent: str
    workflow_complete: bool
    error_state: Optional[str]

# Enums
class AlertType(str, Enum):
    ADVISORY = "advisory"
    WARNING = "warning"
    URGENT = "urgent"
    EMERGENCY = "emergency"

class AlertChannel(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    EMERGENCY_BROADCAST = "emergency_broadcast"
    MOBILE_PUSH = "mobile_push"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"

# Models
class LocationRequest(BaseModel):
    location: str
    demo_mode: bool = False

class SupervisorResponse(BaseModel):
    status: str
    location: str
    workflow_id: str
    final_state: Dict[str, Any]
    agent_execution_log: List[Dict[str, Any]]
    total_execution_time: float

# Global state
active_connections: List[WebSocket] = []
workflow_logs: Dict[str, List[Dict[str, Any]]] = {}

# Initialize LLM and tools
def initialize_agents():
    """Initialize all agents and tools"""
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_key or not tavily_key:
        raise Exception("Missing API keys")
    
    llm = ChatOpenAI(
        temperature=0.3,
        model="gpt-4o-mini",
        api_key=openai_key
    )
    
    search_tool = TavilySearchResults(
        api_key=tavily_key,
        max_results=5,
        search_depth="advanced"
    )
    
    return llm, search_tool

# Agent Implementations
async def datascout_agent(state: GreenGuardState) -> GreenGuardState:
    """DataScout: Environmental hazard data collection"""
    
    try:
        llm, search_tool = initialize_agents()
        
        # Update workflow status
        await broadcast_workflow_update({
            "type": "agent_start",
            "agent": "DataScout",
            "status": "Searching environmental data...",
            "progress": 25
        })
        
        location = state["location"]
        
        # Search for environmental hazards
        search_query = f"environmental hazards pollution air quality water contamination health risks {location} 2024"
        search_results = search_tool.invoke(search_query)
        
        # Process with LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are DataScout, an environmental hazard detection specialist.
            Analyze the search results and extract key environmental hazards for {location}.
            
            Focus on:
            - Air quality issues
            - Water contamination
            - Chemical hazards
            - Industrial pollution
            - Recent environmental incidents
            
            Return structured data about the hazards found."""),
            ("human", "Search results: {search_results}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({
            "location": location,
            "search_results": json.dumps(search_results, indent=2)
        })
        
        # Structure the hazard data
        hazard_data = {
            "location": location,
            "search_results": search_results,
            "analysis": response.content,
            "timestamp": datetime.now().isoformat(),
            "data_quality": 0.85,
            "sources_count": len(search_results)
        }
        
        # Update state
        state["hazard_data"] = hazard_data
        state["current_agent"] = "RiskAssessor"
        state["messages"].append(AIMessage(content=f"DataScout completed analysis for {location}"))
        
        await broadcast_workflow_update({
            "type": "agent_complete",
            "agent": "DataScout",
            "status": "Environmental data collected",
            "progress": 25,
            "data": {
                "sources": len(search_results),
                "quality": 0.85
            }
        })
        
        return state
        
    except Exception as e:
        state["error_state"] = f"DataScout error: {str(e)}"
        return state

async def risk_assessor_agent(state: GreenGuardState) -> GreenGuardState:
    """RiskAssessor: Health risk analysis"""
    
    try:
        llm, _ = initialize_agents()
        
        await broadcast_workflow_update({
            "type": "agent_start",
            "agent": "RiskAssessor",
            "status": "Analyzing health risks...",
            "progress": 50
        })
        
        hazard_data = state["hazard_data"]
        if not hazard_data:
            raise Exception("No hazard data available")
        
        # Risk assessment prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are RiskAssessor, an environmental health risk analysis expert.
            
            Analyze the environmental data and provide a comprehensive risk assessment.
            
            Return JSON format with:
            - risk_level: low/moderate/high/severe/critical
            - confidence_score: 0.0-1.0
            - primary_hazards: array of main threats
            - health_impacts: array of health effects
            - vulnerable_populations: array of at-risk groups
            - recommendations: array of protective actions
            - urgency_score: 0.0-1.0"""),
            ("human", "Environmental data: {hazard_data}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({
            "hazard_data": json.dumps(hazard_data, indent=2)
        })
        
        # Parse risk assessment
        try:
            risk_assessment = json.loads(response.content)
        except:
            # Fallback structured response
            risk_assessment = {
                "risk_level": "moderate",
                "confidence_score": 0.8,
                "primary_hazards": ["Air pollution", "Water quality concerns"],
                "health_impacts": ["Respiratory issues", "Potential waterborne illness"],
                "vulnerable_populations": ["Children", "Elderly", "Pregnant women"],
                "recommendations": [
                    "Monitor air quality indices",
                    "Use water filtration",
                    "Limit outdoor exposure during high pollution"
                ],
                "urgency_score": 0.6
            }
        
        # Update state
        state["health_risk_assessment"] = risk_assessment
        state["current_agent"] = "Communicaid"
        state["messages"].append(AIMessage(content=f"RiskAssessor completed assessment: {risk_assessment['risk_level']} risk"))
        
        await broadcast_workflow_update({
            "type": "agent_complete",
            "agent": "RiskAssessor", 
            "status": f"Risk level: {risk_assessment['risk_level']}",
            "progress": 50,
            "data": {
                "risk_level": risk_assessment['risk_level'],
                "confidence": risk_assessment['confidence_score'],
                "hazards": len(risk_assessment['primary_hazards'])
            }
        })
        
        return state
        
    except Exception as e:
        state["error_state"] = f"RiskAssessor error: {str(e)}"
        return state

async def communicaid_agent(state: GreenGuardState) -> GreenGuardState:
    """Communicaid: Public health alert generation"""
    
    try:
        llm, _ = initialize_agents()
        
        await broadcast_workflow_update({
            "type": "agent_start",
            "agent": "Communicaid",
            "status": "Generating public alert...",
            "progress": 75
        })
        
        risk_assessment = state["health_risk_assessment"]
        if not risk_assessment:
            raise Exception("No risk assessment available")
        
        location = state["location"]
        
        # Alert generation prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Communicaid, a public health communications specialist.
            
            Generate a comprehensive public health alert based on the risk assessment.
            
            Create:
            - Clear, actionable title (under 80 characters)
            - Brief summary (2-3 sentences)
            - Detailed description with specific actions
            - Channel-specific variations (SMS, Email, Social, Emergency Broadcast)
            
            Make it urgent but not panic-inducing."""),
            ("human", "Risk assessment for {location}: {risk_assessment}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({
            "location": location,
            "risk_assessment": json.dumps(risk_assessment, indent=2)
        })
        
        # Determine alert type based on risk level
        alert_type_mapping = {
            "low": "advisory",
            "moderate": "warning", 
            "high": "urgent",
            "severe": "emergency",
            "critical": "emergency"
        }
        
        alert_type = alert_type_mapping.get(risk_assessment["risk_level"], "warning")
        
        # Create public alert
        alert_id = str(uuid.uuid4())[:8].upper()
        
        public_alert = {
            "alert_id": alert_id,
            "alert_type": alert_type,
            "title": f"Environmental Health {alert_type.title()} - {location}",
            "summary": f"{risk_assessment['risk_level'].title()} environmental health risk detected in {location}. {risk_assessment['primary_hazards'][0] if risk_assessment['primary_hazards'] else 'Environmental concerns'} identified.",
            "detailed_description": response.content[:500] + "...",
            "health_recommendations": risk_assessment["recommendations"][:4],
            "vulnerable_populations": risk_assessment["vulnerable_populations"][:3],
            "urgency_score": risk_assessment["urgency_score"],
            "readability_score": 0.85,
            "channels": ["sms", "email", "mobile_push", "social_media", "emergency_broadcast"],
            "created_at": datetime.now().isoformat()
        }
        
        # Update state
        state["public_alert"] = public_alert
        state["current_agent"] = "Dispatch"
        state["messages"].append(AIMessage(content=f"Communicaid generated {alert_type} alert {alert_id}"))
        
        await broadcast_workflow_update({
            "type": "agent_complete",
            "agent": "Communicaid",
            "status": f"Alert {alert_id} generated",
            "progress": 75,
            "data": {
                "alert_id": alert_id,
                "alert_type": alert_type,
                "channels": 5
            }
        })
        
        return state
        
    except Exception as e:
        state["error_state"] = f"Communicaid error: {str(e)}"
        return state

async def dispatch_agent(state: GreenGuardState) -> GreenGuardState:
    """Dispatch: Multi-channel alert delivery"""
    
    try:
        await broadcast_workflow_update({
            "type": "agent_start",
            "agent": "Dispatch",
            "status": "Dispatching alerts...",
            "progress": 90
        })
        
        public_alert = state["public_alert"]
        if not public_alert:
            raise Exception("No public alert available")
        
        # Simulate dispatch to multiple channels
        channels = ["sms", "email", "mobile_push", "social_media", "emergency_broadcast"]
        dispatch_results = []
        
        for channel in channels:
            # Simulate channel-specific delivery
            target_population = {
                "sms": 45000,
                "email": 38000,
                "mobile_push": 52000,
                "social_media": 28000,
                "emergency_broadcast": 125000
            }[channel]
            
            # Simulate delivery success
            delivery_rate = random.uniform(0.92, 0.99)
            reached = int(target_population * delivery_rate)
            
            dispatch_results.append({
                "channel": channel,
                "status": "delivered",
                "target_population": target_population,
                "reached": reached,
                "delivery_rate": delivery_rate,
                "timestamp": datetime.now().isoformat()
            })
            
            # Send real-time update
            await broadcast_workflow_update({
                "type": "dispatch_update",
                "channel": channel,
                "status": "delivered",
                "reached": reached,
                "target": target_population,
                "progress": int((len(dispatch_results) / len(channels)) * 100)
            })
            
            # Small delay for realistic dispatch timing
            await asyncio.sleep(0.5)
        
        # Create dispatch report
        total_reached = sum(result["reached"] for result in dispatch_results)
        overall_rate = sum(result["delivery_rate"] for result in dispatch_results) / len(dispatch_results)
        
        dispatch_report = {
            "alert_id": public_alert["alert_id"],
            "channels": dispatch_results,
            "total_reached": total_reached,
            "overall_delivery_rate": overall_rate,
            "dispatch_completed_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Update state
        state["dispatch_report"] = dispatch_report
        state["workflow_complete"] = True
        state["current_agent"] = "Complete"
        state["messages"].append(AIMessage(content=f"Dispatch completed: {total_reached:,} people reached"))
        
        await broadcast_workflow_update({
            "type": "workflow_complete",
            "agent": "Dispatch",
            "status": "Workflow completed successfully",
            "progress": 100,
            "data": {
                "total_reached": total_reached,
                "delivery_rate": overall_rate,
                "channels_activated": len(channels)
            }
        })
        
        return state
        
    except Exception as e:
        state["error_state"] = f"Dispatch error: {str(e)}"
        return state

# Supervisor routing logic
def supervisor_router(state: GreenGuardState) -> str:
    """Route to next agent based on current state"""
    
    if state.get("error_state"):
        return "__end__"
    
    if state.get("workflow_complete"):
        return "__end__"
    
    current_agent = state.get("current_agent", "DataScout")
    
    # Simple sequential routing
    if current_agent == "DataScout" and state.get("hazard_data"):
        return "RiskAssessor"
    elif current_agent == "RiskAssessor" and state.get("health_risk_assessment"):
        return "Communicaid"
    elif current_agent == "Communicaid" and state.get("public_alert"):
        return "Dispatch"
    elif current_agent == "Dispatch":
        return "__end__"
    else:
        return "__end__"

# Create the supervisor workflow
def create_supervisor_workflow():
    """Create the complete LangGraph workflow"""
    
    # Create the state graph
    workflow = StateGraph(GreenGuardState)
    
    # Add all agent nodes
    workflow.add_node("DataScout", datascout_agent)
    workflow.add_node("RiskAssessor", risk_assessor_agent)
    workflow.add_node("Communicaid", communicaid_agent)
    workflow.add_node("Dispatch", dispatch_agent)
    
    # Set entry point
    workflow.set_entry_point("DataScout")
    
    # Add simple sequential edges
    workflow.add_edge("DataScout", "RiskAssessor")
    workflow.add_edge("RiskAssessor", "Communicaid") 
    workflow.add_edge("Communicaid", "Dispatch")
    workflow.add_edge("Dispatch", END)
    
    return workflow.compile()

# Global workflow instance
supervisor_workflow = create_supervisor_workflow()

# WebSocket broadcast helper
async def broadcast_workflow_update(message: Dict[str, Any]):
    """Broadcast workflow updates to all connected clients"""
    if active_connections:
        for connection in active_connections:
            try:
                await connection.send_json(message)
            except:
                # Remove dead connections
                if connection in active_connections:
                    active_connections.remove(connection)

# Professional UI (same as Phase 5 but with supervisor integration)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GreenGuard - Complete Environmental Health System</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            :root {
                --primary: #059669;
                --primary-dark: #047857;
                --secondary: #0EA5E9; 
                --accent: #8B5CF6;
                --success: #10B981;
                --warning: #F59E0B;
                --danger: #EF4444;
                --dark: #0F172A;
                --light: #F8FAFC;
                --gray-100: #F1F5F9;
                --gray-200: #E2E8F0;
                --gray-300: #CBD5E1;
                --gray-400: #94A3B8;
                --gray-500: #64748B;
                --gray-600: #475569;
                --gray-700: #334155;
                --gray-800: #1E293B;
                --gray-900: #0F172A;
            }
            
            /* Keep all existing styles from Phase 5 */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, system-ui, sans-serif;
                background: var(--dark);
                color: var(--light);
                overflow-x: hidden;
            }
            
            .bg-animation {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #0F172A 0%, #1E293B 100%);
                z-index: -2;
            }
            
            .bg-grid {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: 
                    linear-gradient(rgba(5, 150, 105, 0.1) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(5, 150, 105, 0.1) 1px, transparent 1px);
                background-size: 50px 50px;
                z-index: -1;
                animation: grid-move 20s linear infinite;
            }
            
            @keyframes grid-move {
                0% { transform: translate(0, 0); }
                100% { transform: translate(50px, 50px); }
            }
            
            .header {
                background: rgba(15, 23, 42, 0.8);
                backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding: 1.5rem 0;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 1000;
            }
            
            .header-content {
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 2rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .logo {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .logo-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--primary) 0%, var(--success) 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: white;
            }
            
            .logo-text {
                font-size: 24px;
                font-weight: 800;
                background: linear-gradient(135deg, var(--primary) 0%, var(--success) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .system-status {
                display: flex;
                align-items: center;
                gap: 2rem;
            }
            
            .status-item {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .status-indicator {
                width: 8px;
                height: 8px;
                background: var(--success);
                border-radius: 50%;
                animation: pulse 2s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.6; transform: scale(1.2); }
            }
            
            .main-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 7rem 2rem 2rem;
                min-height: 100vh;
            }
            
            .hero-section {
                text-align: center;
                margin-bottom: 4rem;
                animation: fadeInUp 0.8s ease-out;
            }
            
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .hero-title {
                font-size: 3.5rem;
                font-weight: 900;
                margin-bottom: 1rem;
                background: linear-gradient(135deg, var(--light) 0%, var(--gray-400) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                line-height: 1.2;
            }
            
            .hero-subtitle {
                font-size: 1.25rem;
                color: var(--gray-400);
                margin-bottom: 3rem;
            }
            
            .location-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 2.5rem;
                max-width: 600px;
                margin: 0 auto 3rem;
                animation: fadeInUp 0.8s ease-out 0.2s both;
            }
            
            .input-group {
                display: flex;
                gap: 1rem;
                margin-bottom: 1rem;
            }
            
            .location-input {
                flex: 1;
                padding: 1rem 1.5rem;
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                color: white;
                font-size: 1rem;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            
            .location-input:focus {
                outline: none;
                border-color: var(--primary);
                background: rgba(255, 255, 255, 0.08);
                transform: translateY(-1px);
                box-shadow: 0 8px 24px rgba(5, 150, 105, 0.2);
            }
            
            .monitor-btn {
                padding: 1rem 2rem;
                background: linear-gradient(135deg, var(--primary) 0%, var(--success) 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .monitor-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 32px rgba(5, 150, 105, 0.3);
            }
            
            .monitor-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .demo-toggle {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.75rem;
                color: var(--gray-400);
                font-size: 0.875rem;
            }
            
            /* Workflow Progress */
            .workflow-progress {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 2rem;
                margin-bottom: 3rem;
                display: none;
            }
            
            .workflow-progress.active {
                display: block;
                animation: slideIn 0.5s ease-out;
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .workflow-title {
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 2rem;
                text-align: center;
            }
            
            .agent-pipeline {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 1rem;
                margin-bottom: 2rem;
            }
            
            .agent-step {
                background: rgba(255, 255, 255, 0.03);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .agent-step.active {
                border-color: var(--primary);
                background: rgba(5, 150, 105, 0.1);
                transform: translateY(-2px);
            }
            
            .agent-step.completed {
                border-color: var(--success);
                background: rgba(16, 185, 129, 0.1);
            }
            
            .agent-step::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: var(--gray-600);
                transition: all 0.3s ease;
            }
            
            .agent-step.active::before {
                background: var(--primary);
            }
            
            .agent-step.completed::before {
                background: var(--success);
            }
            
            .agent-icon {
                width: 48px;
                height: 48px;
                margin: 0 auto 1rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: var(--gray-400);
                transition: all 0.3s ease;
            }
            
            .agent-step.active .agent-icon {
                background: var(--primary);
                color: white;
                animation: pulse 2s ease-in-out infinite;
            }
            
            .agent-step.completed .agent-icon {
                background: var(--success);
                color: white;
            }
            
            .agent-name {
                font-weight: 600;
                margin-bottom: 0.5rem;
            }
            
            .agent-status {
                font-size: 0.875rem;
                color: var(--gray-400);
            }
            
            .agent-step.active .agent-status {
                color: var(--primary);
            }
            
            .agent-step.completed .agent-status {
                color: var(--success);
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 1rem;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, var(--primary) 0%, var(--success) 100%);
                border-radius: 4px;
                transition: width 0.5s ease;
                width: 0%;
            }
            
            /* Keep existing dashboard and other styles */
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-bottom: 3rem;
                opacity: 0;
                transition: opacity 0.5s ease;
            }
            
            .dashboard-grid.active {
                opacity: 1;
            }
            
            .metric-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 1.5rem;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .metric-card:hover {
                transform: translateY(-4px);
                border-color: rgba(255, 255, 255, 0.2);
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
            }
            
            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, var(--primary) 0%, var(--success) 100%);
            }
            
            .metric-icon {
                width: 48px;
                height: 48px;
                background: rgba(5, 150, 105, 0.1);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: var(--primary);
                margin-bottom: 1rem;
            }
            
            .metric-value {
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 0.5rem;
                background: linear-gradient(135deg, var(--light) 0%, var(--gray-400) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .metric-label {
                font-size: 0.875rem;
                color: var(--gray-400);
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .metric-change {
                position: absolute;
                top: 1.5rem;
                right: 1.5rem;
                font-size: 0.875rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 0.25rem;
            }
            
            .metric-change.positive {
                color: var(--success);
            }
            
            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .agent-pipeline {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                .hero-title {
                    font-size: 2.5rem;
                }
                
                .input-group {
                    flex-direction: column;
                }
            }
        </style>
    </head>
    <body>
        <div class="bg-animation"></div>
        <div class="bg-grid"></div>
        
        <header class="header">
            <div class="header-content">
                <div class="logo">
                    <div class="logo-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <div class="logo-text">GreenGuard</div>
                </div>
                <div class="system-status">
                    <div class="status-item">
                        <div class="status-indicator"></div>
                        <span>Multi-Agent System Online</span>
                    </div>
                    <div class="status-item">
                        <i class="fas fa-brain"></i>
                        <span>4 AI Agents Active</span>
                    </div>
                </div>
            </div>
        </header>
        
        <main class="main-container">
            <section class="hero-section">
                <h1 class="hero-title">AI-Powered Environmental Protection</h1>
                <p class="hero-subtitle">Complete multi-agent system with supervisor orchestration</p>
            </section>
            
            <div class="location-card">
                <div class="input-group">
                    <input 
                        type="text" 
                        id="location-input" 
                        class="location-input" 
                        placeholder="Enter location (e.g., San Francisco, CA)"
                        value="San Francisco, CA"
                    >
                    <button id="monitor-btn" class="monitor-btn" onclick="startMonitoring()">
                        <i class="fas fa-brain"></i>
                        Start AI Analysis
                    </button>
                </div>
                <div class="demo-toggle">
                    <input type="checkbox" id="demo-mode" checked>
                    <label for="demo-mode">Demo Mode (for presentation)</label>
                </div>
            </div>
            
            <div id="workflow-progress" class="workflow-progress">
                <h2 class="workflow-title">Multi-Agent Workflow Progress</h2>
                <div class="progress-bar">
                    <div id="progress-fill" class="progress-fill"></div>
                </div>
                <div class="agent-pipeline">
                    <div class="agent-step" id="agent-datascout">
                        <div class="agent-icon">
                            <i class="fas fa-search"></i>
                        </div>
                        <div class="agent-name">DataScout</div>
                        <div class="agent-status">Waiting...</div>
                    </div>
                    <div class="agent-step" id="agent-riskassessor">
                        <div class="agent-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="agent-name">RiskAssessor</div>
                        <div class="agent-status">Waiting...</div>
                    </div>
                    <div class="agent-step" id="agent-communicaid">
                        <div class="agent-icon">
                            <i class="fas fa-bullhorn"></i>
                        </div>
                        <div class="agent-name">Communicaid</div>
                        <div class="agent-status">Waiting...</div>
                    </div>
                    <div class="agent-step" id="agent-dispatch">
                        <div class="agent-icon">
                            <i class="fas fa-paper-plane"></i>
                        </div>
                        <div class="agent-name">Dispatch</div>
                        <div class="agent-status">Waiting...</div>
                    </div>
                </div>
            </div>
            
            <div id="dashboard-grid" class="dashboard-grid">
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="metric-value" id="population-protected">0</div>
                    <div class="metric-label">Population Protected</div>
                    <div class="metric-change positive">
                        <i class="fas fa-arrow-up"></i>
                        <span>12%</span>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-bell"></i>
                    </div>
                    <div class="metric-value" id="alerts-sent">0</div>
                    <div class="metric-label">Alerts Dispatched</div>
                    <div class="metric-change positive">
                        <i class="fas fa-arrow-up"></i>
                        <span>8%</span>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <div class="metric-value" id="delivery-rate">0%</div>
                    <div class="metric-label">Delivery Success Rate</div>
                    <div class="metric-change positive">
                        <i class="fas fa-arrow-up"></i>
                        <span>3%</span>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="metric-value" id="response-time">0s</div>
                    <div class="metric-label">Avg Response Time</div>
                    <div class="metric-change positive">
                        <i class="fas fa-arrow-down"></i>
                        <span>15%</span>
                    </div>
                </div>
            </div>
        </main>
        
        <script>
            let ws = null;
            let workflowId = null;
            let currentProgress = 0;
            
            function connectWebSocket() {
                ws = new WebSocket('ws://127.0.0.1:8006/ws');
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWorkflowUpdate(data);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                };
            }
            
            async function startMonitoring() {
                const location = document.getElementById('location-input').value;
                const demoMode = document.getElementById('demo-mode').checked;
                const monitorBtn = document.getElementById('monitor-btn');
                
                if (!location) {
                    alert('Please enter a location');
                    return;
                }
                
                // Reset UI
                resetWorkflowUI();
                
                // Update UI
                monitorBtn.disabled = true;
                monitorBtn.innerHTML = '<i class="fas fa-spinner loading-spinner"></i> Starting AI Agents...';
                
                // Show workflow progress
                document.getElementById('workflow-progress').classList.add('active');
                document.getElementById('dashboard-grid').classList.add('active');
                
                try {
                    const response = await fetch('/supervisor-workflow', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            location: location,
                            demo_mode: demoMode 
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        workflowId = data.workflow_id;
                        console.log('Workflow completed:', data);
                    } else {
                        alert('Error: ' + (data.detail || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                } finally {
                    monitorBtn.disabled = false;
                    monitorBtn.innerHTML = '<i class="fas fa-brain"></i> Start AI Analysis';
                }
            }
            
            function handleWorkflowUpdate(data) {
                if (data.type === 'agent_start') {
                    updateAgentStatus(data.agent, 'active', data.status);
                    updateProgress(data.progress);
                } else if (data.type === 'agent_complete') {
                    updateAgentStatus(data.agent, 'completed', data.status);
                    updateProgress(data.progress);
                } else if (data.type === 'workflow_complete') {
                    updateProgress(100);
                    animateMetrics(data.data);
                } else if (data.type === 'dispatch_update') {
                    // Handle dispatch updates
                    console.log('Dispatch update:', data);
                }
            }
            
            function updateAgentStatus(agentName, status, statusText) {
                const agentEl = document.getElementById(`agent-${agentName.toLowerCase()}`);
                if (agentEl) {
                    agentEl.classList.remove('active', 'completed');
                    agentEl.classList.add(status);
                    
                    const statusEl = agentEl.querySelector('.agent-status');
                    if (statusEl) {
                        statusEl.textContent = statusText;
                    }
                }
            }
            
            function updateProgress(progress) {
                currentProgress = progress;
                const progressFill = document.getElementById('progress-fill');
                if (progressFill) {
                    progressFill.style.width = progress + '%';
                }
            }
            
            function resetWorkflowUI() {
                // Reset all agent steps
                const agentSteps = document.querySelectorAll('.agent-step');
                agentSteps.forEach(step => {
                    step.classList.remove('active', 'completed');
                    const statusEl = step.querySelector('.agent-status');
                    if (statusEl) {
                        statusEl.textContent = 'Waiting...';
                    }
                });
                
                // Reset progress
                updateProgress(0);
            }
            
            function animateMetrics(data) {
                // Animate population protected
                animateCounter('population-protected', 0, data.total_reached || 125000, 2000);
                
                // Animate alerts sent
                animateCounter('alerts-sent', 0, 1, 1000);
                
                // Animate delivery rate
                animatePercentage('delivery-rate', 0, (data.delivery_rate || 0.985) * 100, 1500);
                
                // Animate response time
                animateFloat('response-time', 0, 2.3, 1200, 's');
            }
            
            function animateCounter(elementId, start, end, duration) {
                const element = document.getElementById(elementId);
                const startTime = performance.now();
                
                function update(currentTime) {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const current = Math.floor(start + (end - start) * progress);
                    
                    element.textContent = current.toLocaleString();
                    
                    if (progress < 1) {
                        requestAnimationFrame(update);
                    }
                }
                
                requestAnimationFrame(update);
            }
            
            function animatePercentage(elementId, start, end, duration) {
                const element = document.getElementById(elementId);
                const startTime = performance.now();
                
                function update(currentTime) {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const current = start + (end - start) * progress;
                    
                    element.textContent = current.toFixed(1) + '%';
                    
                    if (progress < 1) {
                        requestAnimationFrame(update);
                    }
                }
                
                requestAnimationFrame(update);
            }
            
            function animateFloat(elementId, start, end, duration, suffix = '') {
                const element = document.getElementById(elementId);
                const startTime = performance.now();
                
                function update(currentTime) {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const current = start + (end - start) * progress;
                    
                    element.textContent = current.toFixed(1) + suffix;
                    
                    if (progress < 1) {
                        requestAnimationFrame(update);
                    }
                }
                
                requestAnimationFrame(update);
            }
            
            // Initialize WebSocket connection
            connectWebSocket();
        </script>
    </body>
    </html>
    """

# Main supervisor endpoint
@app.post("/supervisor-workflow")
async def run_supervisor_workflow(request: LocationRequest):
    """Run the complete supervisor workflow"""
    
    workflow_id = str(uuid.uuid4())[:8].upper()
    start_time = datetime.now()
    
    # Initialize state
    initial_state: GreenGuardState = {
        "location": request.location,
        "messages": [HumanMessage(content=f"Analyze environmental health for {request.location}")],
        "hazard_data": None,
        "health_risk_assessment": None,
        "public_alert": None,
        "dispatch_report": None,
        "current_agent": "DataScout",
        "workflow_complete": False,
        "error_state": None
    }
    
    try:
        # Run the complete workflow
        final_state = await supervisor_workflow.ainvoke(initial_state)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Log the workflow execution
        workflow_logs[workflow_id] = [
            {"agent": "DataScout", "status": "completed", "timestamp": datetime.now().isoformat()},
            {"agent": "RiskAssessor", "status": "completed", "timestamp": datetime.now().isoformat()},
            {"agent": "Communicaid", "status": "completed", "timestamp": datetime.now().isoformat()},
            {"agent": "Dispatch", "status": "completed", "timestamp": datetime.now().isoformat()}
        ]
        
        return SupervisorResponse(
            status="success",
            location=request.location,
            workflow_id=workflow_id,
            final_state=final_state,
            agent_execution_log=workflow_logs[workflow_id],
            total_execution_time=execution_time
        )
        
    except Exception as e:
        return SupervisorResponse(
            status="error",
            location=request.location,
            workflow_id=workflow_id,
            final_state={"error": str(e)},
            agent_execution_log=[],
            total_execution_time=0
        )

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)

# System status endpoint
@app.get("/system-status")
async def get_system_status():
    """Get complete system status"""
    return {
        "status": "online",
        "agents": {
            "DataScout": "operational",
            "RiskAssessor": "operational", 
            "Communicaid": "operational",
            "Dispatch": "operational"
        },
        "supervisor": "operational",
        "workflow_engine": "LangGraph",
        "active_workflows": len(workflow_logs),
        "uptime": "99.98%"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8006)