from sqlmodel import create_engine, Session, SQLModel
from config.dev_settings import settings
from typing import Generator
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    try:
        logger.info("开始创建数据库表...")
        SQLModel.metadata.create_all(engine)
        logger.info("数据库表创建完成")
    except Exception as e:
        logger.error(f"数据库表创建失败: {e}")
        raise

def init_data(): # 初始化数据库数据
    try:
        from core.init_data import init_all_data
        init_all_data()
    except Exception as e:
        logger.error(f"数据初始化失败: {e}")
        # 不抛出异常，让应用继续启动
        pass

