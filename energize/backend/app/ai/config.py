"""AI configuration for Energize platform."""

from pydantic_settings import BaseSettings
from typing import Optional


class AIConfig(BaseSettings):
    """AI-specific configuration."""
    
    # OpenAI Configuration
    openai_api_key: str = "your-openai-api-key"
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 1000
    
    # Energy Optimization Targets
    target_energy_reduction: float = 30.0  # 30% reduction
    anomaly_threshold: float = 3.0  # Z-score threshold
    carbon_intensity_api: str = "https://api.carbonintensity.org.uk"
    
    # Agent Configuration
    max_workflow_steps: int = 50
    agent_timeout: int = 30  # seconds
    
    class Config:
        env_prefix = "AI_"