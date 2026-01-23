"""
数据库会话管理模块
支持SQLite和MySQL两种数据库
使用异步引擎和会话工厂
支持自动降级：MySQL连接失败时自动切换到SQLite
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
import os
import asyncio

# 全局变量存储当前使用的数据库类型
_current_database_type = None
_engine = None
AsyncSessionLocal = None


async def test_mysql_connection() -> bool:
    """
    测试MySQL连接是否可用
    
    Returns:
        True表示可用，False表示不可用
    """
    try:
        test_engine = create_async_engine(
            settings.DATABASE_URL_MYSQL,
            echo=False,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        async with test_engine.connect() as conn:
            # 执行简单查询测试连接
            await conn.execute("SELECT 1")
            await test_engine.dispose()
            return True
    except Exception as e:
        print(f"⚠️ MySQL连接测试失败: {e}")
        return False


async def create_database_engine():
    """
    创建数据库引擎，支持自动降级

    Returns:
        engine: SQLAlchemy异步引擎
    """
    global _current_database_type, _engine, engine, AsyncSessionLocal

    # 如果已经创建过引擎，直接返回
    if _engine is not None:
        return _engine

    # 尝试使用MySQL
    if settings.DATABASE_TYPE.lower() == "mysql":
        print("🔄 尝试连接MySQL数据库...")
        mysql_available = await test_mysql_connection()

        if mysql_available:
            try:
                _engine = create_async_engine(
                    settings.DATABASE_URL_MYSQL,
                    echo=settings.SQLALCHEMY_ECHO,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    pool_recycle=3600
                )
                # 同时更新公共engine变量
                engine = _engine
                _current_database_type = "mysql"
                print(f"✅ 成功使用MySQL数据库")
                return _engine
            except Exception as e:
                print(f"⚠️ MySQL引擎创建失败: {e}")
        else:
            print("⚠️ MySQL服务不可用，自动降级到SQLite")

    # 降级到SQLite
    print("🔄 使用SQLite数据库（降级模式）...")

    # 确保数据库目录存在
    db_path = settings.DATABASE_URL_SQLITE.replace("sqlite+aiosqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    _engine = create_async_engine(
        settings.DATABASE_URL_SQLITE,
        echo=settings.SQLALCHEMY_ECHO,
    )
    # 同时更新公共engine变量
    engine = _engine
    _current_database_type = "sqlite"
    print(f"✅ 使用SQLite数据库: {settings.DATABASE_URL_SQLITE}")

    # 创建会话工厂
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    return _engine


# 创建引擎（异步初始化）
engine = None
_current_database_type = None

# 创建异步会话工厂（不使用lambda，在get_db中动态绑定）
AsyncSessionLocal = None


async def get_db() -> AsyncSession:
    """
    依赖注入: 获取数据库会话

    Yields:
        AsyncSession: 数据库会话对象
    """
    # 确保引擎已初始化
    global engine, AsyncSessionLocal
    if engine is None or AsyncSessionLocal is None:
        await create_database_engine()

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_database_type() -> str:
    """
    获取当前使用的数据库类型

    Returns:
        数据库类型: "mysql" 或 "sqlite"
    """
    return _current_database_type
