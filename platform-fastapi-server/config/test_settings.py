from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings): # 测试环境配置
    # 数据库配置 - 测试环境推荐使用SQLite
    DB_TYPE: str = "sqlite"
    
    # MySQL配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "test"
    MYSQL_PASSWORD: str = "test"
    MYSQL_DATABASE: str = "platfrom_test"
    
    # SQLite配置
    SQLITE_DATABASE: str = "./data/ai_agent_test.db"
    
    SQLALCHEMY_ECHO: bool = True # 测试环境打印SQL便于调试
    
    # JWT密钥
    SECRET_KEY: str = "test-secret-key-12345678"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MINIO平台的配置信息
    MINIO_CLIENT_URL: str = "http://localhost:9000"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    
    # 关键字文件目录
    KEY_WORDS_DIR: str = "./keywords"
    
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
        env_file = ".env.test"
        case_sensitive = True

settings = Settings()
