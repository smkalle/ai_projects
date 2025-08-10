"""
Configuration settings for the Rare Disease Drug Repurposing AI System
"""
import os
from typing import Dict, List, Optional
from pydantic import BaseSettings, Field
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    app_name: str = "Rare Disease Drug Repurposing AI"
    version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    default_llm_model: str = "gpt-3.5-turbo"  # Using cheaper model for demo
    max_tokens: int = 4096
    temperature: float = 0.1  # Low temperature for medical applications

    # Database Configuration  
    vector_db_url: str = Field(default="memory://", env="VECTOR_DB_URL")  # In-memory for demo
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Biomedical API Configuration
    pubmed_api_key: Optional[str] = Field(default=None, env="PUBMED_API_KEY")
    drugbank_api_key: Optional[str] = Field(default=None, env="DRUGBANK_API_KEY")

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # Citation Configuration
    citation_format: str = "vancouver"
    min_citation_count: int = 3
    evidence_level_threshold: int = 3

    # Safety Configuration
    confidence_threshold: float = 0.7
    safety_check_enabled: bool = True
    require_peer_review: bool = True

    # Demo Mode Settings
    demo_mode: bool = True
    use_mock_data: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

# Sample data for demo mode
SAMPLE_DISEASES = {
    "Hutchinson-Gilford Progeria Syndrome": {
        "omim_id": "176670",
        "orphanet_id": "740",
        "description": "Rare genetic disorder causing accelerated aging",
        "prevalence": "1 in 4-8 million births",
        "associated_genes": ["LMNA"]
    },
    "Duchenne Muscular Dystrophy": {
        "omim_id": "310200",
        "orphanet_id": "98896",
        "description": "X-linked recessive muscle-wasting disease",
        "prevalence": "1 in 3,500-5,000 male births",
        "associated_genes": ["DMD"]
    }
}

SAMPLE_DRUGS = {
    "lonafarnib": {
        "drugbank_id": "DB05294",
        "name": "Lonafarnib",
        "generic_name": "lonafarnib",
        "brand_names": ["Zokinvy"],
        "mechanism": "Farnesyltransferase inhibitor",
        "approval_status": "approved"
    },
    "ataluren": {
        "drugbank_id": "DB05109", 
        "name": "Ataluren",
        "generic_name": "ataluren",
        "brand_names": ["Translarna"],
        "mechanism": "Nonsense mutation readthrough",
        "approval_status": "approved"
    }
}

settings = Settings()