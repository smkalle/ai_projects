"""
Configuration management for PagerDuty AI Agent.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.0, env="OPENAI_TEMPERATURE")

    # LangSmith Configuration (Optional)
    langchain_tracing_v2: bool = Field(default=False, env="LANGCHAIN_TRACING_V2")
    langchain_api_key: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="pagerduty-ai-agent", env="LANGCHAIN_PROJECT")

    # Database Configuration
    database_url: str = Field(default="sqlite:///incidents.db", env="DATABASE_URL")

    # Application Configuration
    app_name: str = Field(default="PagerDuty AI Agent", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Streamlit Configuration
    streamlit_server_port: int = Field(default=8501, env="STREAMLIT_SERVER_PORT")
    streamlit_server_address: str = Field(default="localhost", env="STREAMLIT_SERVER_ADDRESS")

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def load_config() -> Settings:
    """Load configuration and set environment variables."""
    settings = get_settings()

    # Set LangSmith environment variables if enabled
    if settings.langchain_tracing_v2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        if settings.langchain_api_key:
            os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project

    return settings

# Database configuration
def get_database_url() -> str:
    """Get database URL."""
    return get_settings().database_url

# OpenAI configuration
def get_openai_config() -> dict:
    """Get OpenAI configuration."""
    settings = get_settings()
    return {
        "api_key": settings.openai_api_key,
        "model": settings.openai_model,
        "temperature": settings.openai_temperature,
    }