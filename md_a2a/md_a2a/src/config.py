"""
Configuration management for Medical AI Assistant MVP.
Handles all environment variables and settings using pydantic-settings.
"""

import os
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    app_name: str = Field(default="Medical AI Assistant MVP", description="Application name")
    app_version: str = Field(default="0.2.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    environment: str = Field(default="development", description="Environment name")
    
    # =============================================================================
    # OPENAI CONFIGURATION
    # =============================================================================
    openai_api_key: str = Field(default="sk-your-openai-api-key-here", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    openai_max_tokens: int = Field(default=500, description="Maximum tokens per request")
    openai_temperature: float = Field(default=0.3, description="AI temperature setting")
    openai_timeout: int = Field(default=10, description="API timeout in seconds")
    openai_max_retries: int = Field(default=3, description="Maximum API retries")
    
    # =============================================================================
    # AI BEHAVIOR SETTINGS
    # =============================================================================
    ai_confidence_threshold: float = Field(
        default=0.7, 
        ge=0.0, 
        le=1.0, 
        description="Confidence threshold for AI assessments"
    )
    ai_fallback_enabled: bool = Field(
        default=True, 
        description="Enable fallback to local processing"
    )
    ai_cost_optimization: bool = Field(
        default=True, 
        description="Enable cost optimization routing"
    )
    ai_safety_mode: bool = Field(
        default=True, 
        description="Enable extra conservative medical advice"
    )
    ai_max_cost_per_assessment: int = Field(
        default=10, 
        description="Maximum cost per assessment in cents"
    )
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    database_url: str = Field(
        default="sqlite:///./mvp_medical.db", 
        description="Database connection URL"
    )
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_echo: bool = Field(default=False, description="Enable SQL query logging")
    
    # =============================================================================
    # API CONFIGURATION
    # =============================================================================
    api_host: str = Field(default="0.0.0.0", description="API host address")
    api_port: int = Field(default=8000, description="API port number")
    api_reload: bool = Field(default=False, description="Enable auto-reload in development")
    api_workers: int = Field(default=1, description="Number of worker processes")
    
    # CORS settings
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000",
        description="Allowed CORS origins (comma-separated)"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    secret_key: str = Field(default="dev-secret-key-change-in-production", description="Secret key for JWT tokens")
    access_token_expire_minutes: int = Field(
        default=30, 
        description="Access token expiration time"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    
    # =============================================================================
    # FILE UPLOAD SETTINGS
    # =============================================================================
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    allowed_file_types: str = Field(
        default="image/jpeg,image/png,image/webp",
        description="Allowed file MIME types (comma-separated)"
    )
    upload_dir: str = Field(default="./static/photos", description="Upload directory")
    
    # =============================================================================
    # MONITORING & LOGGING
    # =============================================================================
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, description="Metrics server port")
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    
    # Log settings
    log_file: str = Field(default="./logs/app.log", description="Log file path")
    log_rotation: str = Field(default="1 day", description="Log rotation interval")
    log_retention: str = Field(default="30 days", description="Log retention period")
    
    # =============================================================================
    # CACHING SETTINGS
    # =============================================================================
    enable_assessment_cache: bool = Field(
        default=True, 
        description="Enable assessment caching"
    )
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")
    cache_max_size: int = Field(default=1000, description="Maximum cache size")
    
    # =============================================================================
    # RATE LIMITING
    # =============================================================================
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # AI-specific rate limiting
    ai_rate_limit_requests: int = Field(
        default=50, 
        description="AI rate limit requests per window"
    )
    ai_rate_limit_window: int = Field(
        default=60, 
        description="AI rate limit window in seconds"
    )
    
    # =============================================================================
    # DEVELOPMENT SETTINGS
    # =============================================================================
    dev_mode: bool = Field(default=True, description="Enable development features")
    dev_mock_ai: bool = Field(default=False, description="Mock AI responses for testing")
    dev_seed_data: bool = Field(default=True, description="Seed database with test data")
    
    # =============================================================================
    # BACKUP SETTINGS
    # =============================================================================
    backup_enabled: bool = Field(default=True, description="Enable automatic backups")
    backup_interval_hours: int = Field(default=24, description="Backup interval in hours")
    backup_retention_days: int = Field(default=30, description="Backup retention in days")
    backup_dir: str = Field(default="./backups", description="Backup directory")
    
    # =============================================================================
    # NOTIFICATION SETTINGS (future use)
    # =============================================================================
    smtp_host: Optional[str] = Field(default=None, description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_username: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_use_tls: bool = Field(default=True, description="Use TLS for SMTP")
    
    # =============================================================================
    # INTEGRATION SETTINGS (future use)
    # =============================================================================
    webhook_doctor_notification: Optional[str] = Field(
        default=None, 
        description="Webhook URL for doctor notifications"
    )
    webhook_emergency_alert: Optional[str] = Field(
        default=None, 
        description="Webhook URL for emergency alerts"
    )
    external_medical_db_url: Optional[str] = Field(
        default=None, 
        description="External medical database URL"
    )
    external_medical_db_key: Optional[str] = Field(
        default=None, 
        description="External medical database API key"
    )
    
    # =============================================================================
    # VALIDATORS
    # =============================================================================
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment name."""
        valid_envs = ['development', 'testing', 'staging', 'production']
        if v.lower() not in valid_envs:
            raise ValueError(f'Environment must be one of: {valid_envs}')
        return v.lower()
    
    # =============================================================================
    # COMPUTED PROPERTIES
    # =============================================================================
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == 'development'
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == 'production'
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(',')]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        return [file_type.strip() for file_type in self.allowed_file_types.split(',')]
    
    @property
    def openai_config(self) -> dict:
        """Get OpenAI configuration as dictionary."""
        return {
            'api_key': self.openai_api_key,
            'model': self.openai_model,
            'max_tokens': self.openai_max_tokens,
            'temperature': self.openai_temperature,
            'timeout': self.openai_timeout,
            'max_retries': self.openai_max_retries,
        }
    
    @property
    def ai_behavior_config(self) -> dict:
        """Get AI behavior configuration as dictionary."""
        return {
            'confidence_threshold': self.ai_confidence_threshold,
            'fallback_enabled': self.ai_fallback_enabled,
            'cost_optimization': self.ai_cost_optimization,
            'safety_mode': self.ai_safety_mode,
            'max_cost_per_assessment': self.ai_max_cost_per_assessment,
        }
    
    # =============================================================================
    # CONFIGURATION
    # =============================================================================
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Allow extra fields for future extensibility
        extra = "ignore"


# =============================================================================
# GLOBAL SETTINGS INSTANCE
# =============================================================================

def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Create global settings instance
settings = get_settings()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_directories():
    """Create necessary directories based on settings."""
    directories = [
        settings.upload_dir,
        settings.backup_dir,
        os.path.dirname(settings.log_file),
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)


def validate_settings():
    """Validate critical settings and environment."""
    errors = []
    
    # Check required API key only if AI is enabled and not in mock mode
    if (settings.ai_fallback_enabled and 
        not settings.dev_mock_ai and 
        (not settings.openai_api_key or settings.openai_api_key == "sk-your-openai-api-key-here")):
        if settings.is_production:
            errors.append("OpenAI API key is required in production")
        else:
            print("⚠️  Warning: OpenAI API key not configured - AI features will use local fallback")
    
    # Check secret key
    if settings.secret_key == "dev-secret-key-change-in-production":
        if settings.is_production:
            errors.append("Secret key must be changed in production")
        elif settings.environment != 'development':
            errors.append("Secret key should be set for non-development environments")
    
    # Check production settings
    if settings.is_production:
        if settings.debug:
            errors.append("Debug mode should be disabled in production")
        if settings.api_reload:
            errors.append("API reload should be disabled in production")
        if settings.dev_mode:
            errors.append("Development mode should be disabled in production")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")


def print_settings_summary():
    """Print a summary of current settings (excluding sensitive data)."""
    print(f"""
Medical AI Assistant MVP - Configuration Summary
================================================
Environment: {settings.environment}
Debug Mode: {settings.debug}
AI Model: {settings.openai_model}
AI Fallback: {settings.ai_fallback_enabled}
AI Mock Mode: {settings.dev_mock_ai}
Cost Optimization: {settings.ai_cost_optimization}
API Host: {settings.api_host}:{settings.api_port}
Database: {settings.database_url}
Upload Directory: {settings.upload_dir}
Log Level: {settings.log_level}
================================================
""")


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize_settings():
    """Initialize settings and create necessary directories."""
    try:
        validate_settings()
        create_directories()
        if settings.dev_mode:
            print_settings_summary()
    except Exception as e:
        print(f"Configuration error: {e}")
        if settings.is_production:
            raise


# Auto-initialize when module is imported
if __name__ != "__main__":
    initialize_settings() 