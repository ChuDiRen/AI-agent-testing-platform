"""
配置管理模块
使用 pydantic_settings 管理环境变量
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置类"""
    
    # ========== 数据库配置 ==========
    DATABASE_URL: str = "mysql+aiomysql://root:admin123456@192.168.111.128:3306/testdb"
    SQLALCHEMY_ECHO: bool = True
    
    # ========== JWT 配置 ==========
    SECRET_KEY: str = "1234567812345678"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 5
    
    # ========== 文件路径配置 ==========
    KEY_WORDS_DIR: str = "/keyswords"
    CASES_ROOT_DIR: str = "/yamls"
    REPORT_ROOT_DIR: str = "/report"
    REPORT_API_URL: str = "http://127.0.0.1:8000/ApiReportViewer"
    REPORT_WEB_URL: str = "http://127.0.0.1:8000"
    REPORT_APP_URL: str = "http://127.0.0.1:8000"
    
    # ========== RabbitMQ 配置 ==========
    RABBITMQ_HOST: str = "192.168.111.128"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "admin"
    RABBITMQ_PASSWORD: str = "admin"
    QUEUE_LIST: list = [("web_queue", 3), ("app_queue", 3), ("api_queue", 6)]

    # ========== Redis 配置 ==========
    REDIS_HOST: str = "192.168.111.128"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    REDIS_PASSWORD: str = "admin123456"
    
    # ========== MinIO 配置 ==========
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "apitest"
    MINIO_CLIENT_URL: str = "http://localhost:9000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()
