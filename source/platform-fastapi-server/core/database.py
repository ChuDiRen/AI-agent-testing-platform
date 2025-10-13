from sqlmodel import create_engine, Session, SQLModel
from config.dev_settings import settings
from typing import Generator

# 创建数据库引擎
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.SQLALCHEMY_ECHO,
    pool_pre_ping=True, # 连接池健康检查
    pool_recycle=3600 # 连接回收时间
)

def get_session() -> Generator[Session, None, None]: # 获取数据库会话（依赖注入）
    with Session(engine) as session:
        yield session

def init_db(): # 初始化数据库表
    SQLModel.metadata.create_all(engine)

