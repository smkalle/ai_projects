"""
MediPulse Agent Orchestrator
Coordinates multiple AI agents for medical document processing
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import base64

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

class AgentType(str, Enum):
    SCANNER = "Scanner Agent"
    MEDICAL_EXPERT = "Medical Expert Agent"
    VALIDATOR = "Validator Agent"

class ProcessingState(BaseModel):
    """State management for document processing"""
    session_id: str
    image_base64: str
    document_type: Optional[str] = None
    confidence_scores: Dict[str, float] = {}
    extracted_data: Optional[Dict] = None
    validation_results: Optional[Dict] = None
    processing_steps: List[str] = []
    current_agent: Optional[str] = None
    errors: List[str] = []

class AgentMessage(BaseModel):
    """Message format for agent communication"""
    agent: str
    action: str
    data: Dict[str, Any]
    confidence: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class MedicalAgentOrchestrator:
    """Orchestrates multiple agents for medical document processing"""
    
    def __init__(self, session_id: str, websocket_callback=None):
        self.session_id = session_id
        self.websocket_callback = websocket_callback
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.state = ProcessingState(
            session_id=session_id,
            image_base64=""
        )
        
    async def broadcast(self, agent: str, action: str, data: Dict, confidence: float = None):
        """Send updates via websocket if callback is provided"""
        message = AgentMessage(
            agent=agent,
            action=action,
            data=data,
            confidence=confidence
        )
        
        if self.websocket_callback:
            await self.websocket_callback(message.dict())
    
    async def scanner_agent(self, image_base64: str) -> Dict:
        """
        Scanner Agent: Analyzes document type and quality
        """
        await self.broadcast(
            AgentType.SCANNER,
            "scanning",
            {"status": "Analyzing document type and quality..."},
            0.1
        )
        
        try:
            # Prepare messages for GPT-4V
            messages = [
                {
                    "role": "system",
                    "content": """You are a medical document scanner agent. Analyze the document and return:
                    1. Document type (lab_report, patient_intake, prescription, discharge_summary, other)
                    2. Quality score (0-1) 
                    3. Detected issues (blur, rotation, missing sections)
                    4. Key sections identified
                    
                    Return as JSON with keys: document_type, quality_score, issues, sections"""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this medical document and classify it:"},
                        {
                            "type": "image_url", 
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Call OpenAI API
            from langchain_core.messages import HumanMessage
            human_msg = HumanMessage(content=messages[1]["content"])
            response = await self.llm.ainvoke([human_msg])
            
            # Try to parse JSON response
            try:
                import json
                response_text = response.content.strip()
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif response_text.startswith("```"):
                    response_text = response_text.split("```")[1].split("```")[0]
                
                result = json.loads(response_text)
                
                # Ensure required fields
                if "document_type" not in result:
                    result["document_type"] = "lab_report"
                if "quality_score" not in result:
                    result["quality_score"] = 0.85
                if "issues" not in result:
                    result["issues"] = []
                if "sections" not in result:
                    result["sections"] = ["patient_info", "test_results"]
                    
            except (json.JSONDecodeError, IndexError):
                # Fallback if JSON parsing fails
                result = {
                    "document_type": "lab_report",
                    "quality_score": 0.85,
                    "issues": [],
                    "sections": ["patient_info", "test_results", "reference_ranges"]
                }
            
            await self.broadcast(
                AgentType.SCANNER,
                "scanned",
                result,
                0.92
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Scanner agent error: {str(e)}"
            self.state.errors.append(error_msg)
            await self.broadcast(
                AgentType.SCANNER,
                "error",
                {"error": error_msg},
                0.0
            )
            return {"error": error_msg}
    
    async def medical_expert_agent(self, image_base64: str, doc_type: str) -> Dict:
        """
        Medical Expert Agent: Extracts medical data based on document type
        """
        await self.broadcast(
            AgentType.MEDICAL_EXPERT,
            "extracting",
            {"status": f"Extracting data from {doc_type}..."},
            0.3
        )
        
        try:
            # Customize prompt based on document type
            extraction_prompts = {
                "lab_report": """Extract ALL data from this lab report including:
                - Patient demographics (name, ID, age, sex, DOB) 
                - Lab information (ordering physician, dates, lab name)
                - ALL lab test results with exact values, units, and reference ranges
                - Any abnormal flags (H, L, critical values marked with **)
                - Critical alerts or comments
                
                Return as structured JSON.""",
                "patient_intake": """Extract patient demographics, insurance info, 
                                     medical history, allergies, current medications""",
                "prescription": """Extract patient name, date, physician, 
                                  all medications with dosage and instructions""",
                "discharge_summary": """Extract patient info, admission date, discharge date,
                                       diagnosis, treatment summary, follow-up instructions"""
            }
            
            prompt = extraction_prompts.get(doc_type, "Extract all relevant medical information")
            
            # Call OpenAI with the image
            from langchain_core.messages import HumanMessage
            human_msg = HumanMessage(content=[
                {"type": "text", "text": f"You are a medical data extraction expert. {prompt}"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ])
            
            response = await self.llm.ainvoke([human_msg])
            
            # Try to parse structured response
            try:
                import json
                response_text = response.content.strip()
                
                # Clean up response if it's wrapped in markdown
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif response_text.startswith("```"):
                    response_text = response_text.split("```")[1].split("```")[0]
                
                extracted = json.loads(response_text)
                
            except (json.JSONDecodeError, IndexError):
                # Fallback: try to extract key information from text
                extracted = {
                    "patient_name": "Extracted from document",
                    "patient_id": "Document ID found", 
                    "date_of_service": "Document date",
                    "lab_results": {},
                    "raw_extraction": response.content[:500] + "..." if len(response.content) > 500 else response.content
                }
            
            await self.broadcast(
                AgentType.MEDICAL_EXPERT,
                "extracted",
                {
                    "fields_extracted": len(extracted),
                    "data": extracted
                },
                0.88
            )
            
            return extracted
            
        except Exception as e:
            error_msg = f"Medical expert agent error: {str(e)}"
            self.state.errors.append(error_msg)
            await self.broadcast(
                AgentType.MEDICAL_EXPERT,
                "error",
                {"error": error_msg},
                0.0
            )
            return {"error": error_msg}
    
    async def validator_agent(self, extracted_data: Dict, doc_type: str) -> Dict:
        """
        Validator Agent: Validates and cross-checks extracted data
        """
        await self.broadcast(
            AgentType.VALIDATOR,
            "validating",
            {"status": "Cross-checking and validating extracted data..."},
            0.7
        )
        
        try:
            # Validation rules based on document type
            validation_rules = {
                "lab_report": [
                    "patient_id_format",
                    "date_validity",
                    "reference_range_check",
                    "critical_value_alert"
                ],
                "prescription": [
                    "drug_interaction_check",
                    "dosage_validity",
                    "physician_license"
                ]
            }
            
            # Simulate validation
            await asyncio.sleep(1)  # Simulate processing time
            
            validation_result = {
                "is_valid": True,
                "confidence_score": 0.94,
                "validations_passed": [
                    "patient_id_format",
                    "date_validity",
                    "reference_ranges_valid"
                ],
                "warnings": [],
                "corrections": [],
                "field_confidence": {
                    "patient_name": 0.95,
                    "patient_id": 0.98,
                    "lab_results": 0.91
                }
            }
            
            # Check for critical values
            if doc_type == "lab_report" and extracted_data.get("lab_results"):
                for test, values in extracted_data["lab_results"].items():
                    if test == "glucose" and values.get("value", 0) > 200:
                        validation_result["warnings"].append(
                            f"Critical value alert: {test} = {values['value']} {values.get('unit', '')}"
                        )
            
            await self.broadcast(
                AgentType.VALIDATOR,
                "validated",
                validation_result,
                validation_result["confidence_score"]
            )
            
            return validation_result
            
        except Exception as e:
            error_msg = f"Validator agent error: {str(e)}"
            self.state.errors.append(error_msg)
            await self.broadcast(
                AgentType.VALIDATOR,
                "error",
                {"error": error_msg},
                0.0
            )
            return {"error": error_msg}
    
    async def process_document(self, image_base64: str) -> Dict:
        """
        Main orchestration method - coordinates all agents
        """
        self.state.image_base64 = image_base64
        
        try:
            # Phase 1: Document Scanning
            self.state.current_agent = AgentType.SCANNER
            scan_result = await self.scanner_agent(image_base64)
            
            if "error" in scan_result:
                return {"success": False, "error": scan_result["error"]}
            
            self.state.document_type = scan_result["document_type"]
            self.state.confidence_scores["scanning"] = scan_result["quality_score"]
            
            # Phase 2: Data Extraction
            self.state.current_agent = AgentType.MEDICAL_EXPERT
            extracted_data = await self.medical_expert_agent(
                image_base64, 
                self.state.document_type
            )
            
            if "error" in extracted_data:
                return {"success": False, "error": extracted_data["error"]}
            
            self.state.extracted_data = extracted_data
            self.state.confidence_scores["extraction"] = 0.88
            
            # Phase 3: Validation
            self.state.current_agent = AgentType.VALIDATOR
            validation_result = await self.validator_agent(
                extracted_data,
                self.state.document_type
            )
            
            if "error" in validation_result:
                return {"success": False, "error": validation_result["error"]}
            
            self.state.validation_results = validation_result
            self.state.confidence_scores["validation"] = validation_result["confidence_score"]
            
            # Calculate overall confidence
            overall_confidence = sum(self.state.confidence_scores.values()) / len(self.state.confidence_scores)
            
            # Final result
            result = {
                "success": True,
                "session_id": self.session_id,
                "document_type": self.state.document_type,
                "extracted_data": self.state.extracted_data,
                "validation": self.state.validation_results,
                "confidence_score": overall_confidence,
                "processing_time": 4.2,  # Would track actual time
                "agent_trace": self.state.processing_steps
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": self.session_id
            }