"""
API Automation Agent Platform - Configuration Management

This module handles all configuration management using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "API Automation Agent Platform"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Database
    database_url: str = "sqlite:///./data/app.db"

    # LLM - OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    openai_base_url: str = "https://api.openai.com/v1"

    # LLM - Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-opus-20240229"

    # RAG
    rag_mode: str = "mix"  # local, global, hybrid, naive, mix, bypass
    rag_top_k: int = 10
    rag_chunk_top_k: int = 5
    rag_enable_rerank: bool = True
    chromadb_path: str = "./data/chromadb"

    # File Storage
    upload_dir: str = "./data/uploads"
    output_dir: str = "./data/outputs"
    max_upload_size: int = 104857600  # 100MB

    # Task Queue
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # MCP Servers
    rag_mcp_host: str = "localhost"
    rag_mcp_port: int = 8001
    chart_mcp_host: str = "localhost"
    chart_mcp_port: int = 8002
    aq_mcp_host: str = "localhost"
    aq_mcp_port: int = 8003

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080"
    ]

    # Test Configuration
    test_timeout: int = 60
    test_retry: int = 3
    test_parallel: int = 1

    @property
    def rag_mcp_url(self) -> str:
        """RAG MCP Server URL"""
        return f"http://{self.rag_mcp_host}:{self.rag_mcp_port}"

    @property
    def chart_mcp_url(self) -> str:
        """Chart MCP Server URL"""
        return f"http://{self.chart_mcp_host}:{self.chart_mcp_port}"

    @property
    def aq_mcp_url(self) -> str:
        """Automation-Quality MCP Server URL"""
        return f"http://{self.aq_mcp_host}:{self.aq_mcp_port}"

    @property
    def use_openai(self) -> bool:
        """Check if OpenAI API key is configured"""
        return bool(self.openai_api_key)

    @property
    def use_anthropic(self) -> bool:
        """Check if Anthropic API key is configured"""
        return bool(self.anthropic_api_key)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    This function is called multiple times during the application lifecycle,
    but the settings are loaded only once and cached.
    """
    return Settings()


# Export for convenience
settings = get_settings()
