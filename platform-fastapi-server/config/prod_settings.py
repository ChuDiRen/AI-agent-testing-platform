from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional
import os


class Settings(BaseSettings): # 生产环境配置
    # ==================== 路径配置 ====================
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMP_DIR: Optional[Path] = None  # 将在__init__中初始化
    YAML_DIR: Optional[Path] = None
    REPORT_DIR: Optional[Path] = None
    LOG_DIR: Optional[Path] = None
    KEYWORDS_DIR: Optional[Path] = None
    DATA_DIR: Optional[Path] = None
    # 插件存储根目录（可指向文件服务器挂载路径）
    PLUGIN_BASE_DIR: Optional[Path] = None
    
    # ==================== 环境配置 ====================
    ENV: str = "production"
    
    # ==================== 数据库配置 ====================
    DB_TYPE: str = "mysql" # 生产环境推荐使用MySQL
    
    # MySQL配置
    MYSQL_HOST: str = "192.168.111.128"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "admin123456"
    MYSQL_DATABASE: str = "testdb"
    
    # SQLite配置
    SQLITE_DATABASE: str = "./data/ai_agent.db"
    
    SQLALCHEMY_ECHO: bool = False # 生产环境不打印SQL
    
    # JWT密钥 - 生产环境必须使用强密钥
    SECRET_KEY: str = "change-this-to-a-strong-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # MINIO平台的配置信息
    MINIO_CLIENT_URL: str = "http://192.168.111.128:9000"
    MINIO_ENDPOINT: str = "192.168.111.128:9000"
    MINIO_ACCESS_KEY: str = "admin"
    MINIO_SECRET_KEY: str = "admin123456"
    MINIO_SECURE: bool = False
    
    # ==================== 消息队列配置 ====================
    QUEUE_TYPE: str = "rabbitmq"  # 生产环境使用rabbitmq
    
    # RabbitMQ配置
    RABBITMQ_HOST: str = "192.168.111.128"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "admin"
    RABBITMQ_PASSWORD: str = "admin123456"
    
    # Redis配置
    REDIS_HOST: str = "192.168.111.128"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "admin123456"
    REDIS_DB: int = 0
    
    # MongoDB配置
    MONGODB_HOST: str = "192.168.111.128"
    MONGODB_PORT: int = 27017
    MONGODB_USER: str = "root"
    MONGODB_PASSWORD: str = "admin123456"
    MONGODB_DATABASE: str = "testdb"
    
    # WebSocket配置
    WEBSOCKET_PING_INTERVAL: int = 30
    WEBSOCKET_PING_TIMEOUT: int = 10
    
    # API测试配置
    APITEST_EXECUTION_TIMEOUT: int = 600  # 生产环境更长的超时时间
    APITEST_MAX_CONCURRENT_TESTS: int = 20  # 生产环境支持更多并发
    
    # 消息推送配置
    ROBOT_RETRY_COUNT: int = 3
    ROBOT_TIMEOUT: int = 15
    
    def __init__(self, **kwargs):
        """初始化配置,设置派生路径"""
        super().__init__(**kwargs)
        
        # 初始化派生路径
        self.TEMP_DIR = self.BASE_DIR / "temp"
        self.YAML_DIR = self.TEMP_DIR / "yaml_cases"
        self.REPORT_DIR = self.TEMP_DIR / "allure_reports"
        self.LOG_DIR = self.TEMP_DIR / "logs"
        self.KEYWORDS_DIR = self.BASE_DIR / "keywords"
        self.DATA_DIR = self.BASE_DIR / "data"
        # 默认插件目录: 项目根目录同级的 plugins 目录，可在部署时改为文件服务器挂载路径
        if self.PLUGIN_BASE_DIR is None:
            self.PLUGIN_BASE_DIR = self.BASE_DIR.parent / "plugins"
        
        # 确保关键目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.TEMP_DIR,
            self.YAML_DIR,
            self.REPORT_DIR,
            self.LOG_DIR,
            self.KEYWORDS_DIR,
            self.DATA_DIR,
            self.PLUGIN_BASE_DIR
        ]
        for directory in directories:
            if directory and not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """根据DB_TYPE自动生成数据库连接URI"""
        if self.DB_TYPE.lower() == "mysql":
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8"
        else:
            db_dir = os.path.dirname(self.SQLITE_DATABASE)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            return f"sqlite:///{self.SQLITE_DATABASE}"
    
    class Config:
        env_file = ".env.production"
        case_sensitive = True

settings = Settings()

