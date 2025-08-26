"""
Configuration settings for Energy Document AI
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Qdrant Configuration
    qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY", None)

    # Collection Settings
    collection_name: str = "energy_documents"

    # PDF Processing
    pdf_dpi: int = 300
    max_file_size_mb: int = 50

    # RAG Settings
    chunk_size: int = 800
    chunk_overlap: int = 100
    max_retrievals: int = 5
    relevance_threshold: float = 0.6

    # Agent Settings
    max_iterations: int = 3
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.1

    # Application
    app_name: str = "Energy Document AI"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()

# Energy sector document types
ENERGY_DOCUMENT_TYPES = {
    "regulatory": "Regulatory and Compliance Documents",
    "technical": "Technical Specifications and Manuals",
    "environmental": "Environmental Impact and Safety Reports",
    "grid": "Grid and Transmission Documents",
    "renewable": "Renewable Energy Research and Reports",
    "efficiency": "Energy Efficiency and Conservation Studies",
    "market": "Energy Market Analysis and Reports",
    "policy": "Energy Policy and Strategy Documents"
}

# Common energy sector keywords for classification
ENERGY_KEYWORDS = {
    "solar": ["solar", "photovoltaic", "pv", "solar panel", "inverter", "irradiance"],
    "wind": ["wind", "turbine", "wind farm", "wind energy", "rotor", "nacelle"],
    "grid": ["grid", "transmission", "distribution", "substation", "transformer", "voltage"],
    "regulatory": ["nerc", "ferc", "epa", "compliance", "regulation", "standard", "audit"],
    "efficiency": ["efficiency", "conservation", "demand response", "smart grid", "ems"],
    "environmental": ["environmental", "impact", "emission", "carbon", "sustainability"],
    "safety": ["safety", "hazard", "protection", "emergency", "incident", "risk"]
}
