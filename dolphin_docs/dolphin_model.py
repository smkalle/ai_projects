"""
Dolphin Model Loader and Inference
Handles loading and running the Dolphin vision-language model
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer, AutoProcessor
from PIL import Image
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import json
from dataclasses import dataclass
import time

from dolphin_config import DolphinConfig, ModelPaths

logger = logging.getLogger(__name__)

@dataclass
class DolphinAnchor:
    """Represents an anchor point in the document"""
    anchor_type: str  # text, table, list, key_value, medication, diagnosis
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    page_num: int
    metadata: Dict[str, Any]

@dataclass
class AnalysisResult:
    """Result from the analyze stage"""
    anchors: List[DolphinAnchor]
    layout_type: str  # clinical_report, lab_results, etc.
    confidence: float
    processing_time: float
    page_count: int
    
@dataclass
class ParseResult:
    """Result from the parse stage"""
    extracted_data: Dict[str, Any]
    anchor_type: str
    confidence: float
    processing_time: float

class DolphinModel:
    """
    Dolphin Vision-Language Model for document parsing
    Implements the two-stage analyze-then-parse paradigm
    """
    
    def __init__(self, config: DolphinConfig):
        self.config = config
        self.model_paths = ModelPaths(config.model_path)
        self.device = torch.device(config.device if torch.cuda.is_available() else "cpu")
        
        # Model components (will be loaded)
        self.vision_encoder = None
        self.language_model = None
        self.processor = None
        self.tokenizer = None
        
        # Cache for model outputs
        self.cache = {}
        
        logger.info(f"Initializing Dolphin model on {self.device}")
        
    def load_model(self) -> bool:
        """Load the Dolphin model components"""
        try:
            # For MVP, we'll use a vision-language model as proxy
            # In production, this would load actual Dolphin weights
            
            if self.config.model_type == "dolphin-vision-language":
                # Use a smaller model for demonstration
                model_name = "microsoft/layoutlmv3-base"
                
                logger.info(f"Loading model: {model_name}")
                
                # Load tokenizer and processor
                from transformers import LayoutLMv3Processor, LayoutLMv3ForSequenceClassification
                
                self.processor = LayoutLMv3Processor.from_pretrained(
                    model_name,
                    apply_ocr=True
                )
                
                self.model = LayoutLMv3ForSequenceClassification.from_pretrained(
                    model_name
                ).to(self.device)
                
                # Set to evaluation mode
                self.model.eval()
                
                logger.info("Model loaded successfully")
                return True
                
            else:
                # Placeholder for actual Dolphin model loading
                logger.warning("Using mock model - actual Dolphin weights not found")
                return self._load_mock_model()
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def _load_mock_model(self) -> bool:
        """Load a mock model for testing"""
        logger.info("Loading mock Dolphin model for demonstration")
        
        # Create mock components
        self.vision_encoder = lambda x: torch.randn(1, 256, 768)
        self.language_model = lambda x: {"logits": torch.randn(1, 100, 50000)}
        self.processor = lambda x: {"input_ids": torch.randint(0, 50000, (1, 512))}
        self.tokenizer = None
        
        return True
    
    def analyze_document(
        self, 
        image: Image.Image, 
        doc_type: str = "medical",
        page_num: int = 0
    ) -> AnalysisResult:
        """
        Stage 1: Analyze document structure and identify anchor points
        
        Args:
            image: PIL Image of document page
            doc_type: Type of medical document
            page_num: Page number in multi-page document
            
        Returns:
            AnalysisResult with identified anchors
        """
        start_time = time.time()
        
        logger.info(f"Analyzing page {page_num} as {doc_type}")
        
        try:
            # Convert image to tensor
            if self.processor:
                # Real processing
                encoding = self.processor(
                    image,
                    return_tensors="pt",
                    truncation=True,
                    padding=True
                )
                
                # Move to device
                encoding = {k: v.to(self.device) for k, v in encoding.items()}
                
                # Get model predictions
                with torch.no_grad():
                    outputs = self.model(**encoding)
                
                # Process outputs to identify anchors
                anchors = self._extract_anchors_from_output(
                    outputs, 
                    image.size,
                    page_num
                )
                
            else:
                # Mock analysis for demonstration
                anchors = self._mock_analyze(image, doc_type, page_num)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return AnalysisResult(
                anchors=anchors,
                layout_type=doc_type,
                confidence=0.95,
                processing_time=processing_time,
                page_count=1
            )
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return AnalysisResult(
                anchors=[],
                layout_type=doc_type,
                confidence=0.0,
                processing_time=time.time() - start_time,
                page_count=0
            )
    
    def parse_anchors(
        self,
        image: Image.Image,
        anchors: List[DolphinAnchor],
        prompt_type: str = "medical"
    ) -> List[ParseResult]:
        """
        Stage 2: Parse content from identified anchor points
        
        Args:
            image: PIL Image of document
            anchors: List of anchor points from analysis
            prompt_type: Type of prompts to use
            
        Returns:
            List of ParseResult with extracted data
        """
        results = []
        
        for anchor in anchors:
            start_time = time.time()
            
            logger.info(f"Parsing {anchor.anchor_type} anchor at {anchor.bbox}")
            
            try:
                # Crop image to anchor region
                cropped = self._crop_to_anchor(image, anchor)
                
                # Parse based on anchor type
                if self.processor:
                    extracted_data = self._parse_with_model(
                        cropped, 
                        anchor.anchor_type
                    )
                else:
                    extracted_data = self._mock_parse(
                        cropped,
                        anchor
                    )
                
                results.append(ParseResult(
                    extracted_data=extracted_data,
                    anchor_type=anchor.anchor_type,
                    confidence=anchor.confidence,
                    processing_time=time.time() - start_time
                ))
                
            except Exception as e:
                logger.error(f"Failed to parse anchor: {e}")
                results.append(ParseResult(
                    extracted_data={},
                    anchor_type=anchor.anchor_type,
                    confidence=0.0,
                    processing_time=time.time() - start_time
                ))
        
        return results
    
    def _extract_anchors_from_output(
        self,
        outputs: Any,
        image_size: Tuple[int, int],
        page_num: int
    ) -> List[DolphinAnchor]:
        """Extract anchor points from model output"""
        anchors = []
        
        # This would normally process actual model outputs
        # For now, create sample anchors based on common medical document structure
        
        width, height = image_size
        
        # Header region (patient info)
        anchors.append(DolphinAnchor(
            anchor_type="key_value",
            bbox=(50, 50, width-50, 200),
            confidence=0.95,
            page_num=page_num,
            metadata={"section": "patient_demographics"}
        ))
        
        # Main content region
        anchors.append(DolphinAnchor(
            anchor_type="text",
            bbox=(50, 200, width-50, height-200),
            confidence=0.92,
            page_num=page_num,
            metadata={"section": "clinical_notes"}
        ))
        
        # Table region (if detected)
        if height > 600:
            anchors.append(DolphinAnchor(
                anchor_type="table",
                bbox=(50, 400, width-50, 600),
                confidence=0.88,
                page_num=page_num,
                metadata={"section": "lab_results"}
            ))
        
        return anchors
    
    def _crop_to_anchor(
        self, 
        image: Image.Image,
        anchor: DolphinAnchor
    ) -> Image.Image:
        """Crop image to anchor bounding box"""
        return image.crop(anchor.bbox)
    
    def _parse_with_model(
        self,
        image: Image.Image,
        anchor_type: str
    ) -> Dict[str, Any]:
        """Parse image region with model"""
        # This would use the actual model for parsing
        # For MVP, return structured data based on anchor type
        
        if anchor_type == "key_value":
            return {
                "patient_name": "John Doe",
                "patient_id": "P123456",
                "dob": "1979-01-15",
                "visit_date": "2025-01-08"
            }
        elif anchor_type == "table":
            return {
                "headers": ["Test", "Value", "Reference", "Status"],
                "rows": [
                    ["WBC", "7.2", "4.0-11.0", "Normal"],
                    ["RBC", "4.5", "4.2-5.4", "Normal"],
                    ["Hemoglobin", "14.2", "13.5-17.5", "Normal"]
                ]
            }
        elif anchor_type == "text":
            return {
                "content": "Patient presents with chief complaint of routine follow-up...",
                "sections": ["Chief Complaint", "HPI", "Assessment"]
            }
        else:
            return {"raw_text": "Extracted text content"}
    
    def _mock_analyze(
        self,
        image: Image.Image,
        doc_type: str,
        page_num: int
    ) -> List[DolphinAnchor]:
        """Mock analysis for demonstration"""
        width, height = image.size
        
        anchors = []
        
        # Simulate different anchor patterns based on document type
        if doc_type == "clinical_report":
            # Patient info at top
            anchors.append(DolphinAnchor(
                anchor_type="key_value",
                bbox=(50, 50, width-50, 250),
                confidence=0.95,
                page_num=page_num,
                metadata={"section": "patient_header"}
            ))
            
            # Clinical notes in middle
            anchors.append(DolphinAnchor(
                anchor_type="text",
                bbox=(50, 250, width-50, height-150),
                confidence=0.92,
                page_num=page_num,
                metadata={"section": "clinical_notes"}
            ))
            
            # Medications at bottom
            anchors.append(DolphinAnchor(
                anchor_type="medication",
                bbox=(50, height-150, width-50, height-50),
                confidence=0.90,
                page_num=page_num,
                metadata={"section": "medications"}
            ))
            
        elif doc_type == "lab_results":
            # Header
            anchors.append(DolphinAnchor(
                anchor_type="key_value",
                bbox=(50, 50, width-50, 150),
                confidence=0.94,
                page_num=page_num,
                metadata={"section": "lab_header"}
            ))
            
            # Results table
            anchors.append(DolphinAnchor(
                anchor_type="table",
                bbox=(50, 150, width-50, height-100),
                confidence=0.96,
                page_num=page_num,
                metadata={"section": "test_results"}
            ))
            
        elif doc_type == "prescription":
            # Patient and prescriber info
            anchors.append(DolphinAnchor(
                anchor_type="key_value",
                bbox=(50, 50, width-50, 200),
                confidence=0.93,
                page_num=page_num,
                metadata={"section": "rx_header"}
            ))
            
            # Medication list
            anchors.append(DolphinAnchor(
                anchor_type="medication",
                bbox=(50, 200, width-50, height-150),
                confidence=0.95,
                page_num=page_num,
                metadata={"section": "prescriptions"}
            ))
            
        else:
            # Generic document structure
            anchors.append(DolphinAnchor(
                anchor_type="text",
                bbox=(50, 50, width-50, height-50),
                confidence=0.85,
                page_num=page_num,
                metadata={"section": "full_page"}
            ))
        
        return anchors
    
    def _mock_parse(
        self,
        image: Image.Image,
        anchor: DolphinAnchor
    ) -> Dict[str, Any]:
        """Mock parsing for demonstration"""
        
        if anchor.anchor_type == "key_value":
            return {
                "patient_name": "Jane Smith",
                "patient_id": "MRN-2024-001",
                "dob": "1985-03-22",
                "gender": "Female",
                "phone": "555-0123",
                "visit_date": "2025-01-08",
                "provider": "Dr. Johnson"
            }
            
        elif anchor.anchor_type == "table":
            return {
                "table_type": "lab_results",
                "headers": ["Test Name", "Result", "Units", "Reference Range", "Flag"],
                "rows": [
                    ["Glucose", "95", "mg/dL", "70-110", ""],
                    ["Creatinine", "0.9", "mg/dL", "0.6-1.2", ""],
                    ["Potassium", "4.2", "mEq/L", "3.5-5.0", ""],
                    ["Sodium", "140", "mEq/L", "136-145", ""],
                    ["Hemoglobin", "13.2", "g/dL", "12.0-16.0", ""]
                ]
            }
            
        elif anchor.anchor_type == "medication":
            return {
                "medications": [
                    {
                        "name": "Metformin",
                        "strength": "500mg",
                        "form": "tablet",
                        "sig": "Take 1 tablet by mouth twice daily",
                        "quantity": "60",
                        "refills": "5"
                    },
                    {
                        "name": "Lisinopril",
                        "strength": "10mg",
                        "form": "tablet",
                        "sig": "Take 1 tablet by mouth once daily",
                        "quantity": "30",
                        "refills": "11"
                    }
                ]
            }
            
        elif anchor.anchor_type == "diagnosis":
            return {
                "diagnoses": [
                    {
                        "description": "Type 2 diabetes mellitus",
                        "icd10": "E11.9",
                        "status": "active"
                    },
                    {
                        "description": "Essential hypertension",
                        "icd10": "I10",
                        "status": "active"
                    }
                ]
            }
            
        else:
            return {
                "text": "Lorem ipsum medical content...",
                "confidence": 0.85
            }
    
    def process_document(
        self,
        images: List[Image.Image],
        doc_type: str = "medical"
    ) -> Dict[str, Any]:
        """
        Complete two-stage processing of document
        
        Args:
            images: List of PIL Images (pages)
            doc_type: Type of medical document
            
        Returns:
            Complete extraction results
        """
        all_results = {
            "document_type": doc_type,
            "page_count": len(images),
            "pages": [],
            "aggregated_data": {},
            "processing_time": 0
        }
        
        total_start = time.time()
        
        for page_num, image in enumerate(images):
            logger.info(f"Processing page {page_num + 1}/{len(images)}")
            
            # Stage 1: Analyze
            analysis = self.analyze_document(image, doc_type, page_num)
            
            # Stage 2: Parse
            parse_results = self.parse_anchors(image, analysis.anchors)
            
            # Combine results for this page
            page_data = {
                "page_number": page_num + 1,
                "analysis": {
                    "layout_type": analysis.layout_type,
                    "anchor_count": len(analysis.anchors),
                    "confidence": analysis.confidence,
                    "time": analysis.processing_time
                },
                "extracted_data": {}
            }
            
            # Organize parsed data by anchor type
            for anchor, parse_result in zip(analysis.anchors, parse_results):
                section = anchor.metadata.get("section", "unknown")
                page_data["extracted_data"][section] = parse_result.extracted_data
            
            all_results["pages"].append(page_data)
        
        # Aggregate data across pages
        all_results["aggregated_data"] = self._aggregate_results(all_results["pages"])
        all_results["processing_time"] = time.time() - total_start
        
        return all_results
    
    def _aggregate_results(self, pages: List[Dict]) -> Dict[str, Any]:
        """Aggregate extracted data from all pages"""
        aggregated = {
            "patient_info": {},
            "medications": [],
            "lab_results": [],
            "diagnoses": [],
            "clinical_notes": []
        }
        
        for page in pages:
            data = page.get("extracted_data", {})
            
            # Aggregate patient info (take first occurrence)
            for section, content in data.items():
                if "patient" in section.lower() and not aggregated["patient_info"]:
                    aggregated["patient_info"] = content
                
                if "medication" in section.lower():
                    meds = content.get("medications", [])
                    aggregated["medications"].extend(meds)
                
                if "lab" in section.lower() or "result" in section.lower():
                    if "rows" in content:
                        aggregated["lab_results"].append(content)
                
                if "diagnos" in section.lower():
                    diags = content.get("diagnoses", [])
                    aggregated["diagnoses"].extend(diags)
                
                if "clinical" in section.lower() or "notes" in section.lower():
                    if "content" in content:
                        aggregated["clinical_notes"].append(content["content"])
        
        return aggregated