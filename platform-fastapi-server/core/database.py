import logging
from typing import Generator

from config.dev_settings import settings
from sqlmodel import create_engine, Session, SQLModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库引擎
# SQLite线程安全配置：允许跨线程访问
if settings.DB_TYPE.lower() == "sqlite":
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        echo=settings.SQLALCHEMY_ECHO,
        connect_args={"check_same_thread": False},  # SQLite多线程支持
        pool_pre_ping=True,  # 连接池健康检查
        pool_recycle=3600  # 连接回收时间
    )
else:
    # MySQL/PostgreSQL等其他数据库
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        echo=settings.SQLALCHEMY_ECHO,
        pool_pre_ping=True,
        pool_recycle=3600
    )

def get_session() -> Generator[Session, None, None]: # 获取数据库会话（依赖注入）
    with Session(engine) as session:
        yield session

def init_db(): # 初始化数据库表
    try:
        logger.info("开始创建数据库表...")
        SQLModel.metadata.create_all(engine)
        logger.info("数据库表创建完成")
    except Exception as e:
        logger.error(f"数据库表创建失败: {e}")
        raise

def init_data(): # 初始化数据库数据
    """
    初始化数据库数据
    
    注意: 生产环境下数据初始化失败将导致应用退出
    开发环境下仅记录错误,允许应用继续启动
    """
    try:
        from .init_data import init_all_data
        init_all_data()
        logger.info("数据初始化完成")
    except Exception as e:
        logger.error(f"数据初始化失败: {e}", exc_info=True)
        
        # ✅ 修复异常处理：根据环境决定是否抛出异常
        if settings.ENV == "production":
            logger.critical("生产环境数据初始化失败,应用无法启动")
            raise  # 生产环境必须初始化成功
        else:
            logger.warning("开发环境数据初始化失败,应用继续启动")
            # 开发环境允许继续启动,方便调试

