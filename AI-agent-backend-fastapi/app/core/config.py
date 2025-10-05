"""应用配置管理"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import secrets


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "AI Agent Testing Platform API"
    APP_VERSION: str = "2.1.0"
    DEBUG: bool = Field(default=True, description="调试模式")
    API_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", description="运行环境: development, staging, production")
    
    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./app.db",
        description="数据库连接URL"
    )
    DB_POOL_SIZE: int = Field(default=5, description="数据库连接池大小")
    DB_MAX_OVERFLOW: int = Field(default=10, description="数据库连接池最大溢出")
    DB_POOL_RECYCLE: int = Field(default=3600, description="连接回收时间(秒)")
    DB_ECHO: bool = Field(default=False, description="是否打印SQL语句")
    
    # JWT配置
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="JWT密钥,生产环境必须设置"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="访问令牌过期时间(分钟)")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="刷新令牌过期时间(天)")
    
    # API密钥加密
    ENCRYPTION_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="API密钥加密密钥"
    )
    
    # Redis配置 (用于Token黑名单、缓存等)
    REDIS_HOST: str = Field(default="localhost", description="Redis主机")
    REDIS_PORT: int = Field(default=6379, description="Redis端口")
    REDIS_DB: int = Field(default=0, description="Redis数据库编号")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis密码")
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="允许的CORS源"
    )
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """解析CORS源列表"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    # 邮件配置
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # 前端URL
    FRONTEND_URL: str = "http://localhost:5173"
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="最大上传文件大小(字节)")
    UPLOAD_DIR: str = Field(default="uploads", description="上传文件目录")
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = Field(
        default=["pdf", "docx", "doc", "txt", "md", "html", "xlsx", "xls", "pptx", "ppt"],
        description="允许的上传文件扩展名"
    )
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="默认分页大小")
    MAX_PAGE_SIZE: int = Field(default=100, description="最大分页大小")
    
    # 限流配置
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="是否启用限流")
    RATE_LIMIT_CALLS: int = Field(default=100, description="限流调用次数")
    RATE_LIMIT_PERIOD: int = Field(default=60, description="限流周期(秒)")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE: str = Field(default="logs/app.log", description="日志文件路径")
    LOG_MAX_BYTES: int = Field(default=10 * 1024 * 1024, description="日志文件最大大小")
    LOG_BACKUP_COUNT: int = Field(default=5, description="日志文件备份数量")

    # Celery配置
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Celery消息代理URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/1",
        description="Celery结果后端URL"
    )
    
    # AI配置
    AI_MAX_CONTEXT_MESSAGES: int = Field(default=20, description="AI对话最大上下文消息数")
    AI_DEFAULT_TEMPERATURE: float = Field(default=0.7, description="AI默认温度参数")
    AI_DEFAULT_MAX_TOKENS: int = Field(default=2000, description="AI默认最大Token数")
    
    # 向量数据库配置
    QDRANT_HOST: str = Field(default="localhost", description="Qdrant主机")
    QDRANT_PORT: int = Field(default=6333, description="Qdrant端口")
    QDRANT_GRPC_PORT: int = Field(default=6334, description="Qdrant gRPC端口")
    
    # 性能监控
    ENABLE_PERFORMANCE_MONITORING: bool = Field(default=True, description="启用性能监控")
    SLOW_QUERY_THRESHOLD: float = Field(default=1.0, description="慢查询阈值(秒)")

    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def validate_production_settings(self):
        """验证生产环境配置"""
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "your-secret-key-change-in-production":
                raise ValueError("生产环境必须设置 SECRET_KEY")
            if "*" in self.BACKEND_CORS_ORIGINS:
                raise ValueError("生产环境不允许使用 CORS 通配符")
            if self.DEBUG:
                print("⚠️  警告: 生产环境不建议开启 DEBUG 模式")


settings = Settings()

# 验证生产环境配置
if settings.ENVIRONMENT == "production":
    settings.validate_production_settings()

