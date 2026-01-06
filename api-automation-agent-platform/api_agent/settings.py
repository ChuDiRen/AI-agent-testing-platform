"""
Application Settings

Configuration management using pydantic-settings.
"""
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # Application
    app_name: str = "API Automation Agent Platform"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"]
    )

    # Database
    database_url: str = "sqlite+aiosqlite:///./api_agent.db"

    # LLM Settings
    llm_provider: str = "openai"
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"

    # Anthropic
    anthropic_api_key: Optional[str] = None

    # RAG Settings
    rag_mode: str = "mix"
    rag_top_k: int = 10
    rag_chunk_top_k: int = 5
    rag_enable_rerank: bool = True

    # ChromaDB
    chroma_persist_directory: str = "./data/chromadb"
    chroma_collection_name: str = "api_knowledge"

    # RAG Embedding
    rag_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 50

    # Chart Server
    chart_server_url: str = "http://localhost:8001"

    # Task Queue
    task_queue_type: str = "memory"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    redis_url: str = "redis://localhost:6379/0"

    # File Storage
    upload_dir: str = "./uploads"
    max_upload_size: int = 10485760  # 10MB

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "./logs/api_agent.log"

    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # Agent Settings
    orchestrator_max_iterations: int = 50
    subagent_timeout: int = 300

    # Test Execution
    test_execution_timeout: int = 600
    max_concurrent_tests: int = 10
    default_test_framework: str = "playwright"

    # Report Generation
    report_format: str = "markdown"
    include_charts: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
