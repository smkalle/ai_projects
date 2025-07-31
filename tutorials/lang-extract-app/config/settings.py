"""Application settings and configuration."""

import os
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    langextract_api_key: str = Field(default="", env="LANGEXTRACT_API_KEY")
    
    # Application Settings
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=True, env="DEBUG")
    max_upload_size_mb: int = Field(default=10, env="MAX_UPLOAD_SIZE_MB")
    max_concurrent_extractions: int = Field(default=5, env="MAX_CONCURRENT_EXTRACTIONS")
    
    # Session Settings
    session_timeout_hours: int = Field(default=24, env="SESSION_TIMEOUT_HOURS")
    cache_ttl_minutes: int = Field(default=60, env="CACHE_TTL_MINUTES")
    
    # Feature Flags
    enable_local_mode: bool = Field(default=True, env="ENABLE_LOCAL_MODE")
    enable_batch_processing: bool = Field(default=True, env="ENABLE_BATCH_PROCESSING")
    enable_custom_templates: bool = Field(default=True, env="ENABLE_CUSTOM_TEMPLATES")
    
    # File Paths
    upload_dir: Path = Path("uploads")
    cache_dir: Path = Path("cache")
    export_dir: Path = Path("exports")
    template_dir: Path = Path("templates")
    
    # Supported File Types
    supported_file_types: List[str] = ["pdf", "txt", "docx", "html"]
    
    # UI Configuration
    page_title: str = "LangExtract Medical Research Assistant"
    page_icon: str = "🔬"
    layout: str = "wide"
    
    # Medical Templates
    medical_templates: Dict[str, Any] = {
        "clinical_trial": {
            "name": "Clinical Trial Data",
            "description": "Extract patient demographics, interventions, and outcomes",
            "fields": ["patient_id", "demographics", "intervention", "outcome", "adverse_events"]
        },
        "case_report": {
            "name": "Case Report",
            "description": "Extract patient history, symptoms, diagnosis, and treatment",
            "fields": ["patient_history", "symptoms", "diagnosis", "treatment", "follow_up"]
        },
        "drug_information": {
            "name": "Drug Information",
            "description": "Extract drug names, dosages, side effects, and interactions",
            "fields": ["drug_name", "dosage", "indication", "side_effects", "interactions"]
        },
        "research_findings": {
            "name": "Research Findings",
            "description": "Extract hypotheses, methods, results, and conclusions",
            "fields": ["hypothesis", "methodology", "results", "conclusions", "limitations"]
        },
        "patient_records": {
            "name": "Patient Records",
            "description": "Extract chief complaints, diagnoses, and medications",
            "fields": ["chief_complaint", "diagnosis", "medications", "vitals", "lab_results"]
        },
        "literature_review": {
            "name": "Literature Review",
            "description": "Extract key findings, methodologies, and citations",
            "fields": ["study_title", "authors", "methodology", "key_findings", "citations"]
        }
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def create_directories(self):
        """Create necessary directories if they don't exist."""
        for dir_path in [self.upload_dir, self.cache_dir, self.export_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.create_directories()