"""
MediPulse: Agentic Workflow for Medical Document Extraction

A prototype designed for medical workflows, inspired by Pulse AI's document extraction platform.
Uses LangGraph to create an agentic workflow for extracting structured information from medical records.

Author: Open Source Community
License: MIT
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import json
import base64
from pathlib import Path

# Load environment variables
load_dotenv()

class MediPulseConfig:
    """Configuration class for MediPulse"""
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.model = "gpt-4o"

    def get_llm(self):
        return ChatOpenAI(model=self.model, api_key=self.openai_api_key)

# Initialize configuration and LLM
config = MediPulseConfig()
llm = config.get_llm()

# Define structured outputs
class DocumentType(BaseModel):
    """Document classification result"""
    doc_type: Literal["lab_report", "patient_intake", "prescription", "discharge_summary", "other"]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    reasoning: str = Field(description="Brief explanation for the classification")

class LabResult(BaseModel):
    """Individual lab result"""
    test_name: str
    value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: Optional[str] = None  # Normal, High, Low, Critical

class ExtractedData(BaseModel):
    """Structured medical data extraction"""
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    date_of_service: Optional[str] = None
    date_of_birth: Optional[str] = None
    physician_name: Optional[str] = None
    lab_results: Optional[dict] = None  # Key-value pairs for lab results
    medications: Optional[list] = None  # List of medications
    diagnosis: Optional[str] = None
    vital_signs: Optional[dict] = None  # Blood pressure, heart rate, etc.
    allergies: Optional[list] = None
    notes: Optional[str] = None
    confidence_score: Optional[float] = None

class ValidationResult(BaseModel):
    """Validation result for extracted data"""
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    completeness_score: float = Field(ge=0.0, le=1.0, description="Data completeness score")

# State for the workflow
class MediState(TypedDict):
    image_base64: str  # Input medical document image
    doc_type: str
    doc_classification: Optional[DocumentType]
    extracted_data: Optional[dict]
    validation_result: Optional[ValidationResult]
    processing_steps: list[str]
    error_message: Optional[str]

class MediPulse:
    """Main MediPulse class for medical document extraction"""

    def __init__(self, config: MediPulseConfig = None):
        self.config = config or MediPulseConfig()
        self.llm = self.config.get_llm()
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(MediState)

        # Add nodes
        workflow.add_node("classify", self._classify_document)
        workflow.add_node("extract", self._extract_structure)
        workflow.add_node("reason", self._adaptive_reasoning)
        workflow.add_node("validate", self._schema_validation)
        workflow.add_node("handle_other", self._handle_unsupported)

        # Add edges
        workflow.add_edge(START, "classify")
        workflow.add_conditional_edges("classify", self._route_extraction, {
            "extract": "extract", 
            "other": "handle_other"
        })
        workflow.add_edge("extract", "reason")
        workflow.add_edge("reason", "validate")
        workflow.add_edge("validate", END)
        workflow.add_edge("handle_other", END)

        return workflow.compile()

    def _classify_document(self, state: MediState) -> MediState:
        """Node 1: Classify document type using OpenAI vision"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a medical document classifier. Analyze the provided medical document image and classify it into one of these categories:
                - lab_report: Laboratory test results, blood work, urinalysis, etc.
                - patient_intake: Patient intake forms, registration forms, medical history forms
                - prescription: Prescription forms, medication lists, pharmacy documents
                - discharge_summary: Hospital discharge summaries, treatment summaries
                - other: Any other medical document type

                Provide your confidence level and reasoning for the classification."""),
                ("user", [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{state['image_base64']}"}}])
            ])

            chain = prompt | self.llm.with_structured_output(DocumentType)
            result = chain.invoke({})

            return {
                **state, 
                "doc_type": result.doc_type,
                "doc_classification": result,
                "processing_steps": state.get("processing_steps", []) + ["Document classified successfully"]
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Classification error: {str(e)}",
                "processing_steps": state.get("processing_steps", []) + ["Classification failed"]
            }

    def _extract_structure(self, state: MediState) -> MediState:
        """Node 2: Extract structured data based on document type"""
        try:
            doc_type = state.get("doc_type", "other")

            # Customize extraction prompt based on document type
            if doc_type == "lab_report":
                system_prompt = """Extract key information from this laboratory report:
                - Patient demographics (name, ID, DOB)
                - Date of service
                - Laboratory results with values, units, and reference ranges
                - Physician/provider information
                - Any critical or abnormal findings"""
            elif doc_type == "patient_intake":
                system_prompt = """Extract key information from this patient intake form:
                - Patient demographics (name, ID, DOB, address, phone)
                - Medical history
                - Current medications
                - Allergies
                - Insurance information
                - Emergency contact"""
            elif doc_type == "prescription":
                system_prompt = """Extract key information from this prescription:
                - Patient information
                - Prescribing physician
                - Medications with dosages, frequencies, and quantities
                - Date prescribed
                - Pharmacy information
                - Special instructions"""
            else:
                system_prompt = f"""Extract key medical information from this {doc_type} document:
                - Patient demographics
                - Date of service
                - Healthcare provider information
                - Key medical findings or information
                - Any medications or treatments mentioned"""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt + "\n\nFormat the output as structured JSON. Be precise with medical terminology and preserve all numeric values with their units."),
                ("user", [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{state['image_base64']}"}}])
            ])

            parser = JsonOutputParser(pydantic_object=ExtractedData)
            chain = prompt | self.llm | parser
            result = chain.invoke({})

            return {
                **state, 
                "extracted_data": result,
                "processing_steps": state.get("processing_steps", []) + ["Data extracted successfully"]
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Extraction error: {str(e)}",
                "processing_steps": state.get("processing_steps", []) + ["Extraction failed"]
            }

    def _adaptive_reasoning(self, state: MediState) -> MediState:
        """Node 3: Adaptive reasoning for ambiguities and data enhancement"""
        try:
            extracted_data = state.get("extracted_data", {})

            # Check for potential ambiguities or missing critical data
            needs_reasoning = False
            reasoning_prompts = []

            # Check for missing critical fields
            if not extracted_data.get("patient_name"):
                needs_reasoning = True
                reasoning_prompts.append("Patient name appears to be missing or unclear")

            if not extracted_data.get("date_of_service"):
                needs_reasoning = True
                reasoning_prompts.append("Date of service is missing or unclear")

            # Check for lab reports without results
            if state.get("doc_type") == "lab_report" and not extracted_data.get("lab_results"):
                needs_reasoning = True
                reasoning_prompts.append("Laboratory results appear to be missing from lab report")

            if needs_reasoning:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", f"""Re-examine this medical document image to resolve the following issues:
                    {chr(10).join(f'- {prompt}' for prompt in reasoning_prompts)}

                    Current extracted data: {json.dumps(extracted_data, indent=2)}

                    Focus on:
                    - Handwritten text that may have been missed
                    - Text in tables or complex layouts
                    - Faded or low-quality text
                    - Medical abbreviations or terminology

                    Provide updated/corrected extraction."""),
                    ("user", [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{state['image_base64']}"}}])
                ])

                chain = prompt | self.llm | JsonOutputParser(pydantic_object=ExtractedData)
                updated_data = chain.invoke({})

                return {
                    **state, 
                    "extracted_data": updated_data,
                    "processing_steps": state.get("processing_steps", []) + ["Adaptive reasoning applied"]
                }

            return {
                **state,
                "processing_steps": state.get("processing_steps", []) + ["No reasoning needed - data looks complete"]
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Reasoning error: {str(e)}",
                "processing_steps": state.get("processing_steps", []) + ["Reasoning failed"]
            }

    def _schema_validation(self, state: MediState) -> MediState:
        """Node 4: Validate against medical schema and data quality checks"""
        try:
            extracted_data = state.get("extracted_data", {})
            errors = []
            warnings = []

            # Validate patient name
            if not extracted_data.get("patient_name"):
                errors.append("Patient name is required but missing")
            elif len(extracted_data["patient_name"].strip()) < 2:
                warnings.append("Patient name seems too short")

            # Validate dates
            date_fields = ["date_of_service", "date_of_birth"]
            for field in date_fields:
                if extracted_data.get(field):
                    # Basic date format validation (could be enhanced)
                    date_str = extracted_data[field]
                    if len(date_str) < 8:
                        warnings.append(f"{field} format may be incomplete: {date_str}")

            # Validate lab results format
            if state.get("doc_type") == "lab_report":
                lab_results = extracted_data.get("lab_results", {})
                if not lab_results:
                    errors.append("Lab report should contain lab results")
                else:
                    for test_name, result in lab_results.items():
                        if not isinstance(result, str) or len(result.strip()) == 0:
                            warnings.append(f"Lab result for {test_name} appears to be empty or invalid")

            # Calculate completeness score
            total_fields = len(ExtractedData.model_fields)
            filled_fields = sum(1 for field in ExtractedData.model_fields.keys() 
                              if extracted_data.get(field) is not None and extracted_data[field] != "")
            completeness_score = filled_fields / total_fields

            validation_result = ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                completeness_score=completeness_score
            )

            return {
                **state, 
                "validation_result": validation_result,
                "processing_steps": state.get("processing_steps", []) + ["Validation completed"]
            }
        except Exception as e:
            return {
                **state,
                "error_message": f"Validation error: {str(e)}",
                "processing_steps": state.get("processing_steps", []) + ["Validation failed"]
            }

    def _handle_unsupported(self, state: MediState) -> MediState:
        """Handle unsupported document types"""
        return {
            **state, 
            "extracted_data": {"error": "Unsupported document type", "doc_type": state.get("doc_type")},
            "processing_steps": state.get("processing_steps", []) + ["Document type not supported"]
        }

    def _route_extraction(self, state: MediState) -> Literal["extract", "other"]:
        """Router: Conditional routing based on document type"""
        doc_type = state.get("doc_type", "other")
        supported_types = ["lab_report", "patient_intake", "prescription", "discharge_summary"]

        if doc_type in supported_types:
            return "extract"
        return "other"

    def process_document(self, image_base64: str) -> dict:
        """
        Process a medical document image and extract structured data

        Args:
            image_base64: Base64 encoded image of the medical document

        Returns:
            Dictionary containing extracted data and processing results
        """
        try:
            initial_state = {
                "image_base64": image_base64,
                "doc_type": "",
                "doc_classification": None,
                "extracted_data": None,
                "validation_result": None,
                "processing_steps": [],
                "error_message": None
            }

            result = self.workflow.invoke(initial_state)

            # Format the final result
            return {
                "success": result.get("error_message") is None,
                "doc_classification": result.get("doc_classification").__dict__ if result.get("doc_classification") else None,
                "extracted_data": result.get("extracted_data"),
                "validation": result.get("validation_result").__dict__ if result.get("validation_result") else None,
                "processing_steps": result.get("processing_steps", []),
                "error_message": result.get("error_message")
            }
        except Exception as e:
            return {
                "success": False,
                "error_message": f"Processing failed: {str(e)}",
                "processing_steps": ["Processing failed at workflow level"]
            }

    def process_document_from_file(self, file_path: str) -> dict:
        """
        Process a medical document from a file path

        Args:
            file_path: Path to the image file

        Returns:
            Dictionary containing extracted data and processing results
        """
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                return self.process_document(image_base64)
        except Exception as e:
            return {
                "success": False,
                "error_message": f"Failed to read file {file_path}: {str(e)}",
                "processing_steps": ["File reading failed"]
            }

def main():
    """Example usage of MediPulse"""
    print("MediPulse - Medical Document Extraction")
    print("=" * 50)

    try:
        medipulse = MediPulse()
        print("✓ MediPulse initialized successfully")

        # For demo purposes - you would replace this with actual base64 encoded image
        print("\nFor actual usage:")
        print("1. Convert your medical document (PDF/image) to base64")
        print("2. Call medipulse.process_document(base64_string)")
        print("3. Or use medipulse.process_document_from_file('path/to/image.jpg')")

        print("\nExample with a sample base64 string:")
        sample_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

        result = medipulse.process_document(sample_base64)
        print("\nProcessing Result:")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("Make sure you have set OPENAI_API_KEY in your .env file")

if __name__ == "__main__":
    main()
