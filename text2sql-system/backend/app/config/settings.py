"""
应用配置模块
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # 数据库配置
    database_url: str = "sqlite:///data/chinook.db"
    database_type: str = "sqlite"

    # AI模型配置
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    model_name: str = "deepseek-chat"

    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/text2sql.log"

    # WebSocket配置
    websocket_timeout: int = 300
    max_connections: int = 100

    # 跨域配置
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:3001"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()
