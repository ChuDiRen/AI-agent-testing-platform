"""
配置文件 - 使用 Pydantic Settings 管理环境变量
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# 强制设置开发环境数据库配置
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./app.db"


class Settings(BaseSettings):
    """应用配置类"""

    # 模型配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # 应用配置
    APP_NAME: str = "AI Agent Orchestration Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    SQLALCHEMY_ECHO: bool = False

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24小时

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # LLM 配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2048

    # WebSocket 配置
    WS_MAX_CONNECTIONS: int = 1000
    WS_MESSAGE_QUEUE_SIZE: int = 100

    # 监控配置
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090

    # 文件存储配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 分页配置
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # 计费配置
    TOKEN_PRICE_PER_1K: float = 0.002  # GPT-3.5-turbo 价格
    EXECUTION_PRICE_PER_MINUTE: float = 0.01


# 创建全局配置实例
settings = Settings()


# 导出配置
__all__ = ["settings"]
