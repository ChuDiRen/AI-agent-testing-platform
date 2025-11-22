from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings): # 生产环境配置
    # 数据库配置 - 支持MySQL和SQLite切换
    DB_TYPE: str = "mysql" # 生产环境推荐使用MySQL
    
    # MySQL配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "your-strong-password"
    MYSQL_DATABASE: str = "platfrom_back"
    
    # SQLite配置
    SQLITE_DATABASE: str = "./data/ai_agent.db"
    
    SQLALCHEMY_ECHO: bool = False # 生产环境不打印SQL
    
    # JWT密钥 - 生产环境必须使用强密钥
    SECRET_KEY: str = "change-this-to-a-strong-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # MINIO平台的配置信息
    MINIO_CLIENT_URL: str = "http://minio.example.com:9000"
    MINIO_ENDPOINT: str = "minio.example.com:9000"
    MINIO_ACCESS_KEY: str = "production-access-key"
    MINIO_SECRET_KEY: str = "production-secret-key"
    MINIO_SECURE: bool = True # 生产环境启用HTTPS
    
    # 关键字文件目录
    KEY_WORDS_DIR: str = "./keywords"
    
    # RabbitMQ配置
    RABBITMQ_HOST: str = "rabbitmq.example.com"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "production-user"
    RABBITMQ_PASSWORD: str = "production-password"
    
    # WebSocket配置
    WEBSOCKET_PING_INTERVAL: int = 30
    WEBSOCKET_PING_TIMEOUT: int = 10
    
    # API测试配置
    APITEST_EXECUTION_TIMEOUT: int = 600  # 生产环境更长的超时时间
    APITEST_MAX_CONCURRENT_TESTS: int = 20  # 生产环境支持更多并发
    
    # 消息推送配置
    ROBOT_RETRY_COUNT: int = 3
    ROBOT_TIMEOUT: int = 15
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str: # 根据DB_TYPE自动生成数据库连接URI
        if self.DB_TYPE.lower() == "mysql":
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8"
        else:
            import os
            db_dir = os.path.dirname(self.SQLITE_DATABASE)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            return f"sqlite:///{self.SQLITE_DATABASE}"
    
    class Config:
        env_file = ".env.production"
        case_sensitive = True

settings = Settings()

