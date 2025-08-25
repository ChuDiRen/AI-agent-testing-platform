"""
应用配置模块
使用Pydantic Settings管理配置
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置类
    """
    # 应用基本信息
    APP_NAME: str = "AI-Agent-Backend"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI Agent Backend - 企业级五层架构FastAPI应用"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000  # 标准后端端口
    RELOAD: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./ai_agent.db"
    DATABASE_ECHO: bool = False  # 是否打印SQL语句
    
    # Redis配置（可选）
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_ENABLED: bool = True  # 是否启用Redis
    
    # JWT配置
    SECRET_KEY: str = "dev-secret-key-change-this-in-production-environment"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = ["*"]  # 开发环境使用通配符
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads/"
    
    # 邮件配置（可选）
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    
    # 第三方API配置（可选）
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 1小时
    CACHE_PREFIX: str = "ai_agent:"
    
    # 安全配置
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8
    
    # API配置
    API_V1_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 速率限制配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # 秒
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """验证数据库URL"""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        """验证密钥"""
        if not v:
            raise ValueError("SECRET_KEY cannot be empty")
        
        # 生产环境检查密钥强度
        if values.get("ENVIRONMENT") == "production":
            if len(v) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
            if v == "dev-secret-key-change-this-in-production-environment":
                raise ValueError("Must change default SECRET_KEY in production")
        
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """验证日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @validator("ALLOWED_ORIGINS")
    def validate_allowed_origins(cls, v):
        """验证CORS允许的源"""
        if not v:
            return ["*"]  # 如果为空，允许所有源（仅开发环境）
        return v
    
    @validator("UPLOAD_DIR")
    def validate_upload_dir(cls, v):
        """验证上传目录"""
        if v and not v.endswith("/"):
            v += "/"
        return v
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.ENVIRONMENT.lower() == "testing"
    
    @property
    def database_url_sync(self) -> str:
        """同步数据库URL"""
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL
        # 对于其他数据库，移除异步前缀
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://") \
                                .replace("mysql+aiomysql://", "mysql+pymysql://")
    
    @property
    def redis_url_parsed(self) -> dict:
        """解析Redis URL"""
        from urllib.parse import urlparse
        parsed = urlparse(self.REDIS_URL)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6379,
            "db": self.REDIS_DB,
            "password": self.REDIS_PASSWORD or parsed.password,
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置实例（单例模式）
    """
    return Settings()


# 全局配置实例
settings = get_settings()

# 导出配置
__all__ = ["settings", "Settings", "get_settings"]
