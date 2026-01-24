"""
配置管理模块
使用 pydantic_settings 管理环境变量
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置类"""
    
    # ========== 数据库配置 ==========
    # 数据库类型: sqlite 或 mysql
    # 如果连接失败会自动降级到sqlite
    DATABASE_TYPE: str = "mysql"
    
    # 数据库URL（根据DATABASE_TYPE自动选择）
    # SQLite默认值
    DATABASE_URL_SQLITE: str = "sqlite+aiosqlite:///./app/data/database.db"
    # MySQL默认值（如需使用，请在.env中配置）
    DATABASE_URL_MYSQL: str = "mysql+aiomysql://root:admin123456@192.168.111.128:3306/testdb?charset=utf8mb4"
    
    @property
    def DATABASE_URL(self) -> str:
        """根据DATABASE_TYPE返回对应的数据库URL"""
        if self.DATABASE_TYPE.lower() == "mysql":
            return self.DATABASE_URL_MYSQL
        return self.DATABASE_URL_SQLITE
    
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
    # 如果连接失败会自动降级到内存消息队列
    RABBITMQ_HOST: str = "192.168.111.128"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "admin"
    RABBITMQ_PASSWORD: str = "admin"
    QUEUE_LIST: list = [("web_queue", 3), ("app_queue", 3), ("api_queue", 6)]
    # 是否启用RabbitMQ自动降级
    RABBITMQ_FALLBACK_ENABLED: bool = True

    # ========== Redis 配置 ==========
    # 如果连接失败会自动降级到内存缓存
    REDIS_HOST: str = "192.168.111.128"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    REDIS_PASSWORD: str = "admin123456"
    # 是否启用Redis自动降级
    REDIS_FALLBACK_ENABLED: bool = True
    
    # ========== 内存缓存配置 ==========
    # 是否启用内存缓存（Redis降级时自动启用）
    MEMORY_CACHE_ENABLED: bool = False
    # 缓存最大条目数
    MEMORY_CACHE_MAXSIZE: int = 10000
    # 缓存默认过期时间（秒）
    MEMORY_CACHE_TTL: int = 3600
    
    # ========== 内存消息队列配置 ==========
    # 是否启用内存消息队列（RabbitMQ降级时自动启用）
    MEMORY_QUEUE_ENABLED: bool = False
    # 队列配置列表: [(队列名称, 消费者数量)]
    MEMORY_QUEUE_LIST: list = [
        ("web_queue", 3),
        ("app_queue", 3),
        ("api_queue", 6)
    ]
    
    # ========== MinIO 配置 ==========
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "apitest"
    MINIO_CLIENT_URL: str = "http://localhost:9000"
    MINIO_SECURE: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()
