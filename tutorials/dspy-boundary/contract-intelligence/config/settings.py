"""Application configuration and settings."""

import os
from functools import lru_cache
from typing import Optional, List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )
    
    # Application
    app_name: str = Field(default="Contract Intelligence Platform")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    secret_key: str = Field(default="change-me-in-production")
    
    # Database
    database_url: str = Field(default="sqlite:///./contract_intelligence.db")
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    fast_model: str = Field(default="openai/gpt-4o-mini")
    smart_model: str = Field(default="openai/gpt-4o")
    embedding_model: str = Field(default="text-embedding-3-small")
    
    # File Storage
    storage_type: str = Field(default="local")  # local, s3
    aws_access_key_id: Optional[str] = Field(default=None)
    aws_secret_access_key: Optional[str] = Field(default=None)
    aws_bucket_name: Optional[str] = Field(default=None)
    aws_region: str = Field(default="us-east-1")
    
    # Email
    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_user: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    from_email: str = Field(default="noreply@contractintelligence.com")
    
    # Authentication
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # Streamlit
    streamlit_server_port: int = Field(default=8501)
    streamlit_server_address: str = Field(default="0.0.0.0")
    
    # Processing Limits
    max_file_size_mb: int = Field(default=50)
    max_pages_per_document: int = Field(default=500)
    analysis_timeout_seconds: int = Field(default=300)
    
    # Feature Flags
    enable_ocr: bool = Field(default=True)
    enable_comparison: bool = Field(default=True)
    enable_redlining: bool = Field(default=True)
    enable_collaboration: bool = Field(default=True)
    
    # Monitoring
    log_level: str = Field(default="INFO")
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL."""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    @property
    def upload_dir(self) -> str:
        """Get upload directory path."""
        return os.path.join(os.getcwd(), "data", "uploads")
    
    @property
    def processed_dir(self) -> str:
        """Get processed files directory path."""
        return os.path.join(os.getcwd(), "data", "processed")
    
    @property
    def exports_dir(self) -> str:
        """Get exports directory path."""
        return os.path.join(os.getcwd(), "data", "exports")
    
    def get_allowed_file_types(self) -> List[str]:
        """Get list of allowed file types."""
        return [".pdf", ".docx", ".doc", ".txt"]
    
    def get_max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()