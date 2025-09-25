"""
数据库会话管理
配置SQLAlchemy数据库连接和会话
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.logger import get_logger
import importlib
import pkgutil

logger = get_logger(__name__)

# 创建数据库引擎
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite配置
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DATABASE_ECHO
    )
else:
    # 其他数据库配置
    engine = create_engine(
        settings.database_url_sync,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_recycle=3600
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    获取数据库会话
    用于FastAPI依赖注入
    
    Yields:
        数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """
    创建所有数据库表
    """
    from app.db.base import Base

    # 导入所有实体以确保它们被注册到metadata中
    def _import_all_submodules(package_name: str) -> None:
        try:
            package = importlib.import_module(package_name)
        except Exception as e:
            logger.warning(f"Skip importing package '{package_name}': {e}")
            return
        package_path = getattr(package, "__path__", None)
        if not package_path:
            return
        for finder, name, ispkg in pkgutil.walk_packages(package_path, package_name + "."):
            try:
                importlib.import_module(name)
            except Exception as e:
                logger.warning(f"Failed to import module '{name}': {e}")

    # 动态导入实体与模型模块，确保所有表与外键可见
    _import_all_submodules("app.entity")
    _import_all_submodules("app.models")

    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)

        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


def drop_tables():
    """
    删除所有数据库表
    """
    from app.db.base import Base

    try:
        # 删除所有表
        Base.metadata.drop_all(bind=engine)

        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {str(e)}")
        raise


# 导出数据库相关对象
__all__ = ["engine", "SessionLocal", "get_db", "create_tables", "drop_tables"]
