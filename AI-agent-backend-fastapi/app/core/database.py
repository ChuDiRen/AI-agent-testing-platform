"""数据库连接配置 - 增强版"""
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool
from app.core.config import settings

logger = logging.getLogger(__name__)

# 数据库引擎配置
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "future": True,
}

# 根据数据库类型配置连接池
if "sqlite" in settings.DATABASE_URL:
    # SQLite 不支持连接池
    engine_kwargs["poolclass"] = NullPool
else:
    # 其他数据库使用连接池
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,  # 检测连接有效性
        "poolclass": QueuePool
    })

# 创建异步引擎
engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    """SQLAlchemy基础模型"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖
    
    Yields:
        AsyncSession: 数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话异常: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库表结构"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ 数据库初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


async def check_db_health() -> bool:
    """
    检查数据库健康状态
    
    Returns:
        bool: 数据库是否健康
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return False


async def close_db():
    """关闭数据库连接"""
    try:
        await engine.dispose()
        logger.info("✅ 数据库连接已关闭")
    except Exception as e:
        logger.error(f"❌ 关闭数据库连接失败: {e}")

