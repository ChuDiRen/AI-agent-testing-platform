import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings): # 开发环境配置
    # ==================== 路径配置 ====================
    # ✅ P2修复: 统一管理项目路径,避免硬编码
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Optional[Path] = None
    
    # ==================== 环境配置 ====================
    ENV: str = "development"  # 环境: development, production, test
    
    # ==================== 数据库配置 ====================
    # 数据库配置 - 支持MySQL和SQLite切换
    DB_TYPE: str = "sqlite" # 数据库类型: mysql 或 sqlite
    
    # MySQL配置
    MYSQL_HOST: str = "192.168.111.128"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "admin123456"
    MYSQL_DATABASE: str = "testdb"
    
    # SQLite配置
    SQLITE_DATABASE: str = "./data/ai_agent.db" # SQLite数据库文件路径
    
    SQLALCHEMY_ECHO: bool = True # 打印sql语句
    
    # ==================== JWT配置 ====================
    # JWT密钥
    SECRET_KEY: str = "1234567812345678"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8小时
    
    # ==================== MinIO配置 ====================
    # MINIO平台的配置信息
    # 注意：9000是API端口（SDK连接），9001是控制台端口（浏览器访问）
    MINIO_CLIENT_URL: str = "http://192.168.111.128:9000"
    MINIO_ENDPOINT: str = "192.168.111.128:9000"
    MINIO_ACCESS_KEY: str = "admin"
    MINIO_SECRET_KEY: str = "admin123456"
    MINIO_SECURE: bool = False
    
    # ==================== 消息队列配置 ====================
    # 消息队列配置
    QUEUE_TYPE: str = "memory"  # 队列类型: rabbitmq 或 memory
    
    # RabbitMQ配置（当QUEUE_TYPE=rabbitmq时使用）
    RABBITMQ_HOST: str = "192.168.111.128"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "admin"
    RABBITMQ_PASSWORD: str = "admin123456"
    
    # ==================== Redis配置 ====================
    REDIS_HOST: str = "192.168.111.128"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "admin123456"
    REDIS_DB: int = 0
    
    # ==================== MongoDB配置 ====================
    MONGODB_HOST: str = "192.168.111.128"
    MONGODB_PORT: int = 27017
    MONGODB_USER: str = "root"
    MONGODB_PASSWORD: str = "admin123456"
    MONGODB_DATABASE: str = "testdb"
    
    # ==================== WebSocket配置 ====================
    WEBSOCKET_PING_INTERVAL: int = 30  # WebSocket心跳间隔（秒）
    WEBSOCKET_PING_TIMEOUT: int = 10   # WebSocket超时时间（秒）
    
    # ==================== 基础配置 ====================
    # 系统基础配置
    ROBOT_TIMEOUT: int = 10  # 系统超时时间（秒）
    
    # ==================== 系统配置 ====================
    # 系统基础配置
    
    def __init__(self, **kwargs):
        """初始化配置,设置派生路径"""
        super().__init__(**kwargs)
        
        # 初始化派生路径
        self.DATA_DIR = self.BASE_DIR / "data"
        
        # 确保关键目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.DATA_DIR
        ]
        for directory in directories:
            if directory and not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str: # 根据DB_TYPE自动生成数据库连接URI
        if self.DB_TYPE.lower() == "mysql":
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8"
        else: # 默认使用SQLite
            db_dir = os.path.dirname(self.SQLITE_DATABASE)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            return f"sqlite:///{self.SQLITE_DATABASE}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() # 全局配置实例