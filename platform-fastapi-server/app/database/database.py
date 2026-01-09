import logging
from typing import Generator

from app.config.dev_settings import settings
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

def get_session_maker(): # 获取会话工厂（用于后台线程）
    """返回一个可调用的会话工厂，用于在后台线程中创建数据库会话"""
    def session_factory():
        return Session(engine)
    return session_factory

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
        from .init_data import init_data
        init_data()
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
    
    # 自动同步前端视图到菜单
    sync_frontend_views()


def sync_frontend_views():
    """
    自动扫描前端视图目录，同步菜单数据到数据库
    
    - 扫描 platform-vue-web/src/views 目录
    - 自动创建缺失的菜单项
    - Form 页面自动设为隐藏
    - 自动为管理员角色分配权限
    """
    try:
        from pathlib import Path
        
        # 计算前端 views 目录路径
        # 当前文件: platform-fastapi-server/app/database/database.py
        # views 目录: platform-vue-web/src/views
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent  # AI-agent-testing-platform
        views_path = project_root / "platform-vue-web" / "src" / "views"
        
        if not views_path.exists():
            logger.warning(f"前端 views 目录不存在，跳过菜单同步: {views_path}")
            return
        
        logger.info(f"开始同步前端视图到菜单: {views_path}")
        
        from app.services.ViewScanService import ViewScanService
        
        with Session(engine) as session:
            service = ViewScanService(str(views_path))
            stats = service.sync_to_database(session, admin_role_id=1)
            
            if stats['added_menus'] > 0:
                logger.info(f"✓ 菜单同步完成: 添加 {stats['added_menus']} 个菜单, {stats['added_permissions']} 条权限")
            else:
                logger.info("✓ 菜单已是最新状态，无需同步")
                
    except Exception as e:
        logger.error(f"前端视图同步失败: {e}", exc_info=True)
        # 同步失败不影响应用启动

