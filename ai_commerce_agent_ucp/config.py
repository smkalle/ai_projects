"""Application configuration using pydantic-settings."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"

    # UCP Merchant Server
    merchant_server_host: str = "0.0.0.0"
    merchant_server_port: int = 8182
    merchant_server_url: str = "http://localhost:8182"

    # Agent API Server
    agent_api_host: str = "0.0.0.0"
    agent_api_port: int = 8000

    # ChromaDB
    chroma_collection_name: str = "ucp_products"
    chroma_persist_directory: str = "./data/chroma_db"

    # Products
    products_json_path: str = "./data/products.json"

    # Payment
    default_currency: str = "USD"
    default_payment_handler: str = "google_pay"

    @property
    def merchant_base_url(self) -> str:
        return f"http://localhost:{self.merchant_server_port}"

    model_config = {"env_prefix": "UCP_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
