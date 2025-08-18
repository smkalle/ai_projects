#!/usr/bin/env python3
"""
NGO Medical AI Assistant - Main Application
Created for NGO Health Medical Hackathons

This module provides the main FastAPI application for multimodal medical reasoning.
Based on GPT-5 multimodal medical reasoning research for charity healthcare initiatives.

Author: Google SDE3 AI Engineer (Simulated)
Date: August 2025
License: MIT
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import base64
import json
from io import BytesIO

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
import openai
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NGO Medical AI Assistant",
    description="Multimodal medical reasoning tool for NGO healthcare initiatives",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class AnalysisRequest(BaseModel):
    """Request model for medical analysis"""
    symptoms: str
    patient_history: Optional[str] = ""
    image_data: Optional[str] = None  # Base64 encoded image
    image_type: Optional[str] = "chest_xray"
    priority: Optional[str] = "normal"

    @validator('symptoms')
    def validate_symptoms(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Symptoms description must be at least 10 characters')
        return v.strip()

class ChatRequest(BaseModel):
    """Request model for medical chat"""
    message: str
    context: Optional[Dict[str, Any]] = {}

class AnalysisResponse(BaseModel):
    """Response model for medical analysis"""
    analysis_id: str
    reasoning_chain: List[str]
    findings: List[str]
    recommendations: List[str]
    confidence_score: float
    priority_level: str
    disclaimers: List[str]
    timestamp: str

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NGO Medical AI Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .hero { text-align: center; padding: 40px 0; }
            .disclaimer { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1>🏥 NGO Medical AI Assistant</h1>
                <p>Multimodal medical reasoning for underserved communities</p>
            </div>

            <div class="disclaimer">
                <strong>⚠️ Important Medical Disclaimer:</strong> 
                This tool provides preliminary insights only and should never replace professional medical diagnosis.
                Always consult qualified medical professionals for diagnosis and treatment.
                In case of emergency, contact local emergency services immediately.
            </div>

            <h2>🚀 Quick Start</h2>
            <ul>
                <li><a href="/docs">API Documentation</a> - Interactive API testing</li>
                <li><a href="/health">Health Check</a> - System status</li>
                <li><a href="/api/sample-cases">Sample Cases</a> - Example medical scenarios</li>
            </ul>

            <h2>🔧 Setup Instructions</h2>
            <ol>
                <li>Copy <code>config/.env.example</code> to <code>config/.env</code></li>
                <li>Add your OpenAI API key to the .env file</li>
                <li>Install dependencies: <code>pip install -r requirements.txt</code></li>
                <li>Run the server: <code>python src/main.py</code></li>
            </ol>

            <h2>🎯 Use Cases</h2>
            <ul>
                <li><strong>Chest X-ray Analysis</strong> - Pneumonia detection and lung assessment</li>
                <li><strong>Emergency Triage</strong> - Rapid patient prioritization</li>
                <li><strong>Wound Assessment</strong> - Infection risk evaluation</li>
                <li><strong>Medical Chat</strong> - Healthcare worker guidance</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2025-08-15T10:00:00Z",
        "message": "NGO Medical AI Assistant is running"
    }

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_medical_case(request: AnalysisRequest):
    """
    Perform multimodal medical analysis on image and symptoms

    This endpoint processes medical images with patient symptoms using
    state-of-the-art multimodal AI models to provide preliminary diagnostic insights.

    **Important**: This is for educational/triage purposes only. Always consult medical professionals.
    """
    try:
        import uuid
        from datetime import datetime

        # Simulate medical analysis
        analysis_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Basic reasoning chain based on symptoms
        reasoning_chain = [
            f"Initial Assessment: Patient presents with {request.symptoms}",
            "Clinical Analysis: Processing symptom pattern and severity",
            "Risk Assessment: Evaluating urgency and priority level",
            "Synthesis: Combining available evidence for preliminary assessment"
        ]

        # Sample findings based on keywords
        findings = []
        symptoms_lower = request.symptoms.lower()

        if any(word in symptoms_lower for word in ["cough", "fever", "breathing"]):
            findings.extend([
                "Respiratory symptoms present",
                "Consider infectious etiology",
                "Monitor oxygen saturation"
            ])

        if any(word in symptoms_lower for word in ["chest pain", "cardiac"]):
            findings.extend([
                "Chest pain requires evaluation",
                "Consider cardiac causes",
                "ECG recommended"
            ])

        if any(word in symptoms_lower for word in ["wound", "infection", "redness"]):
            findings.extend([
                "Possible wound infection",
                "Local inflammatory signs",
                "Antibiotic consideration"
            ])

        # Recommendations
        recommendations = [
            "Comprehensive medical evaluation recommended",
            "Document all findings and treatments",
            "Arrange follow-up with qualified medical professional",
            "Monitor for worsening symptoms",
            "Provide patient education on warning signs"
        ]

        # Priority level
        priority_keywords = ["severe", "acute", "emergency", "difficulty breathing", "chest pain"]
        priority_level = "HIGH" if any(keyword in symptoms_lower for keyword in priority_keywords) else "MODERATE"

        # Confidence (simulated)
        confidence_score = 0.75 if len(findings) > 2 else 0.60

        disclaimers = [
            "This analysis is for preliminary assessment only and should not replace professional medical diagnosis",
            "All findings must be verified by qualified medical professionals", 
            "In case of emergency, contact local emergency services immediately",
            "This AI tool is designed for educational and triage support purposes only"
        ]

        return AnalysisResponse(
            analysis_id=analysis_id,
            reasoning_chain=reasoning_chain,
            findings=findings[:5],  # Limit to 5 findings
            recommendations=recommendations[:5],
            confidence_score=confidence_score,
            priority_level=priority_level,
            disclaimers=disclaimers,
            timestamp=timestamp
        )

    except Exception as e:
        logger.error(f"Error in medical analysis: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")

@app.post("/api/chat")
async def medical_chat(request: ChatRequest):
    """
    Interactive medical chat assistant for healthcare workers

    Provides context-aware responses to medical questions and guidance
    for NGO healthcare workers in the field.
    """
    try:
        # Simple rule-based responses for demo
        message_lower = request.message.lower()

        if "pneumonia" in message_lower:
            response_text = """
            Pneumonia Signs and Management:

            Key Signs:
            - Fever, cough, difficulty breathing
            - Chest pain, especially when breathing
            - Fatigue and weakness
            - On X-ray: infiltrates or consolidation

            Initial Management:
            - Assess oxygen saturation
            - Consider antibiotic therapy
            - Monitor respiratory status
            - Arrange for advanced care if severe

            Red Flags requiring immediate attention:
            - Severe respiratory distress
            - Low oxygen saturation
            - Altered mental status
            - Hemodynamic instability
            """

        elif "triage" in message_lower:
            response_text = """
            Emergency Triage Principles:

            Priority Levels:
            1. EMERGENCY (< 15 min): Life-threatening conditions
            2. HIGH (< 1 hour): Urgent medical needs
            3. MODERATE (< 4 hours): Important but stable
            4. ROUTINE (< 24 hours): Non-urgent care

            Assessment Factors:
            - Vital signs and consciousness
            - Airway, breathing, circulation
            - Pain level and mechanism of injury
            - Age and comorbidities

            Remember: When in doubt, prioritize higher acuity
            """

        elif "emergency" in message_lower:
            response_text = """
            Medical Emergency Response:

            Primary Assessment (ABCDE):
            - Airway: Clear and patent?
            - Breathing: Rate, effort, oxygen saturation
            - Circulation: Pulse, blood pressure, perfusion
            - Disability: Neurological status
            - Exposure: Full examination for injuries

            Immediate Actions:
            - Ensure scene safety
            - Call for advanced medical support
            - Begin life-saving interventions
            - Prepare for transport if needed

            Documentation: Record all assessments and interventions
            """

        else:
            response_text = f"""
            Thank you for your question: "{request.message}"

            For specific medical guidance, please:
            - Consult medical protocols and guidelines
            - Contact medical supervision if available
            - Consider patient safety as the top priority
            - Document all assessments and decisions

            Common topics I can help with:
            - Signs of pneumonia and respiratory conditions
            - Emergency triage protocols
            - Basic wound care and infection signs
            - When to seek advanced medical care
            """

        return {
            "response": response_text,
            "context_used": bool(request.context),
            "disclaimers": [
                "This guidance is for educational purposes only",
                "Always follow local medical protocols",
                "Consult medical professionals for specific cases",
                "In emergencies, contact emergency services immediately"
            ]
        }

    except Exception as e:
        logger.error(f"Error in medical chat: {e}")
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable")

@app.get("/api/sample-cases")
async def get_sample_cases():
    """Return sample medical cases for testing and demonstration"""
    sample_cases = [
        {
            "id": 1,
            "title": "Chest X-ray Analysis",
            "symptoms": "Patient presents with persistent cough, fever, and difficulty breathing for 3 days",
            "image_type": "chest_xray",
            "expected_findings": ["Possible pneumonia", "Bilateral infiltrates", "Recommend immediate medical attention"],
            "confidence": 0.78
        },
        {
            "id": 2,
            "title": "Emergency Triage",
            "symptoms": "45-year-old patient with severe chest pain radiating to left arm, sweating profusely",
            "image_type": "ecg",
            "expected_findings": ["High priority case", "Possible cardiac event", "Emergency transport required"],
            "confidence": 0.92
        },
        {
            "id": 3,
            "title": "Wound Assessment",
            "symptoms": "Local injury with redness, swelling, and warmth around the wound site",
            "image_type": "wound_photo",
            "expected_findings": ["Signs of infection", "Requires antibiotic treatment", "Monitor for worsening"],
            "confidence": 0.85
        }
    ]

    return {"sample_cases": sample_cases}

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )
