"""
Dolphin Framework Configuration
Handles model initialization and configuration for the Dolphin document parser
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DolphinConfig:
    """Configuration for Dolphin framework"""
    model_path: str = "./models/dolphin"
    model_type: str = "dolphin-vision-language"
    max_batch_size: int = 8
    device: str = "cuda"  # cuda or cpu
    precision: str = "fp16"  # fp16, fp32, int8
    
    # Analyze stage config
    analyze_temperature: float = 0.1
    analyze_max_tokens: int = 2048
    
    # Parse stage config  
    parse_temperature: float = 0.1
    parse_max_tokens: int = 4096
    
    # Medical document specific
    enable_medical_prompts: bool = True
    medical_terminology_boost: bool = True
    
    # Performance settings
    use_tensorrt: bool = False
    use_vllm: bool = False
    num_workers: int = 4
    
    # Logging
    verbose: bool = True
    log_level: str = "INFO"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "model_path": self.model_path,
            "model_type": self.model_type,
            "max_batch_size": self.max_batch_size,
            "device": self.device,
            "precision": self.precision,
            "analyze_temperature": self.analyze_temperature,
            "analyze_max_tokens": self.analyze_max_tokens,
            "parse_temperature": self.parse_temperature,
            "parse_max_tokens": self.parse_max_tokens,
            "enable_medical_prompts": self.enable_medical_prompts,
            "medical_terminology_boost": self.medical_terminology_boost,
            "use_tensorrt": self.use_tensorrt,
            "use_vllm": self.use_vllm,
            "num_workers": self.num_workers,
            "verbose": self.verbose,
            "log_level": self.log_level
        }
    
    @classmethod
    def from_json(cls, json_path: str) -> 'DolphinConfig':
        """Load config from JSON file"""
        with open(json_path, 'r') as f:
            config_dict = json.load(f)
        return cls(**config_dict)
    
    def save_json(self, json_path: str):
        """Save config to JSON file"""
        with open(json_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

class DolphinPrompts:
    """Medical document specific prompts for Dolphin framework"""
    
    # Stage 1: Analyze prompts
    ANALYZE_PROMPTS = {
        "clinical_report": """
        Analyze this clinical report document and identify:
        1. Document sections (patient info, chief complaint, HPI, exam, assessment, plan)
        2. Table regions containing lab results or vital signs
        3. Medication lists and prescription information
        4. Diagnostic codes and medical terminology
        Output structured anchors for each identified region.
        """,
        
        "lab_results": """
        Analyze this laboratory results document and identify:
        1. Patient identification header
        2. Test result tables with values and reference ranges
        3. Abnormal values and critical results
        4. Test methodology and collection information
        5. Provider notes and interpretations
        Output structured anchors for data extraction.
        """,
        
        "prescription": """
        Analyze this prescription document and identify:
        1. Patient and prescriber information
        2. Medication names, dosages, and sig codes
        3. Quantity, refills, and DEA schedule
        4. Pharmacy instructions and warnings
        5. Authorization signatures
        Output structured anchors for each element.
        """,
        
        "radiology_report": """
        Analyze this radiology report and identify:
        1. Patient demographics and exam information
        2. Clinical history and indication
        3. Technique/protocol description
        4. Findings section with anatomical descriptions
        5. Impression/conclusion summary
        6. Comparison with prior studies
        Output structured anchors for parsing.
        """,
        
        "discharge_summary": """
        Analyze this discharge summary and identify:
        1. Admission and discharge dates
        2. Principal and secondary diagnoses
        3. Hospital course narrative
        4. Procedures performed
        5. Discharge medications
        6. Follow-up instructions
        Output structured anchors for each section.
        """
    }
    
    # Stage 2: Parse prompts with heterogeneous anchors
    PARSE_PROMPTS = {
        "text_anchor": """
        Extract text content from the identified region.
        Preserve medical terminology and maintain exact values.
        Format: Plain text with original formatting.
        """,
        
        "table_anchor": """
        Parse table structure and extract:
        - Column headers
        - Row labels  
        - Cell values with units
        - Reference ranges if present
        Format: Structured JSON with rows and columns.
        """,
        
        "list_anchor": """
        Extract list items maintaining:
        - Item numbering/bullets
        - Nested structure
        - Associated metadata
        Format: JSON array with hierarchical structure.
        """,
        
        "key_value_anchor": """
        Extract key-value pairs for:
        - Patient demographics
        - Vital signs
        - Lab values with units
        - Dates and identifiers
        Format: JSON object with typed values.
        """,
        
        "medication_anchor": """
        Extract medication information:
        - Drug name (generic and brand)
        - Strength and dosage form
        - Sig/directions
        - Quantity and refills
        - Prescriber information
        Format: Structured medication JSON.
        """,
        
        "diagnosis_anchor": """
        Extract diagnostic information:
        - Diagnosis description
        - ICD-10/CPT codes
        - Severity/stage
        - Associated symptoms
        Format: Structured diagnosis JSON.
        """
    }
    
    @classmethod
    def get_analyze_prompt(cls, doc_type: str) -> str:
        """Get analysis prompt for document type"""
        return cls.ANALYZE_PROMPTS.get(
            doc_type, 
            cls.ANALYZE_PROMPTS["clinical_report"]
        )
    
    @classmethod
    def get_parse_prompt(cls, anchor_type: str) -> str:
        """Get parsing prompt for anchor type"""
        return cls.PARSE_PROMPTS.get(
            anchor_type,
            cls.PARSE_PROMPTS["text_anchor"]
        )

class ModelPaths:
    """Paths for Dolphin model files"""
    
    def __init__(self, base_path: str = "./models/dolphin"):
        self.base_path = Path(base_path)
        
    @property
    def model_dir(self) -> Path:
        """Main model directory"""
        return self.base_path
    
    @property
    def weights_path(self) -> Path:
        """Model weights file"""
        return self.base_path / "pytorch_model.bin"
    
    @property
    def config_path(self) -> Path:
        """Model configuration"""
        return self.base_path / "config.json"
    
    @property
    def tokenizer_path(self) -> Path:
        """Tokenizer files"""
        return self.base_path / "tokenizer"
    
    @property
    def vision_encoder_path(self) -> Path:
        """Vision encoder weights"""
        return self.base_path / "vision_encoder.pt"
    
    def validate_paths(self) -> bool:
        """Check if all required model files exist"""
        required_files = [
            self.config_path,
            self.weights_path,
        ]
        
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        if missing_files:
            logger.warning(f"Missing model files: {missing_files}")
            return False
            
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "cache").mkdir(exist_ok=True)
        (self.base_path / "outputs").mkdir(exist_ok=True)