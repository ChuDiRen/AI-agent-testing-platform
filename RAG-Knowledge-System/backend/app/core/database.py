"""
数据库连接和会话管理
"""
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import QueuePool
from typing import Generator
from config.settings import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
)


def init_db():
    """初始化数据库表"""
    import models  # 导入所有模型
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    获取数据库会话（依赖注入）

    用法：
        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            return session.exec(select(User)).all()
    """
    with Session(engine) as session:
        yield session


def close_db():
    """关闭数据库连接"""
    engine.dispose()
