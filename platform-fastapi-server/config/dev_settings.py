from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings): # 开发环境配置
    # 数据库配置 - 支持MySQL和SQLite切换
    DB_TYPE: str = "sqlite" # 数据库类型: mysql 或 sqlite
    
    # MySQL配置
    MYSQL_HOST: str = "192.168.1.111"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "platfrom_back"
    
    # SQLite配置
    SQLITE_DATABASE: str = "./data/ai_agent.db" # SQLite数据库文件路径
    
    SQLALCHEMY_ECHO: bool = True # 打印sql语句
    
    # JWT密钥
    SECRET_KEY: str = "1234567812345678"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # MINIO平台的配置信息
    # 注意：9000是API端口（SDK连接），9001是控制台端口（浏览器访问）
    MINIO_CLIENT_URL: str = "http://192.168.163.128:9000"
    MINIO_ENDPOINT: str = "192.168.163.128:9000"
    MINIO_ACCESS_KEY: str = "admin"
    MINIO_SECRET_KEY: str = "12345678"
    MINIO_SECURE: bool = False
    
    # 关键字文件目录
    KEY_WORDS_DIR: str = "./keywords"
    
    # 消息队列配置
    QUEUE_TYPE: str = "memory"  # 队列类型: rabbitmq 或 memory
    
    # RabbitMQ配置（当QUEUE_TYPE=rabbitmq时使用）
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    
    # WebSocket配置
    WEBSOCKET_PING_INTERVAL: int = 30  # WebSocket心跳间隔（秒）
    WEBSOCKET_PING_TIMEOUT: int = 10   # WebSocket超时时间（秒）
    
    # API测试配置
    APITEST_EXECUTION_TIMEOUT: int = 300  # 测试执行超时时间（秒）
    APITEST_MAX_CONCURRENT_TESTS: int = 10  # 最大并发测试数
    
    # 消息推送配置
    ROBOT_RETRY_COUNT: int = 3  # 消息推送重试次数
    ROBOT_TIMEOUT: int = 10  # 消息推送超时时间（秒）
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str: # 根据DB_TYPE自动生成数据库连接URI
        if self.DB_TYPE.lower() == "mysql":
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8"
        else: # 默认使用SQLite
            import os
            db_dir = os.path.dirname(self.SQLITE_DATABASE)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            return f"sqlite:///{self.SQLITE_DATABASE}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() # 全局配置实例