from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise import Tortoise

from app.core.exceptions import SettingNotFound
from app.core.init_app import (
    init_data,
    make_middlewares,
    register_exceptions,
    register_routers,
)
from app.log import logger

try:
    from app.settings.config import settings
except ImportError:
    raise SettingNotFound("Can not import settings")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据
    try:
        await init_data(app)
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Error during application initialization: {e}")
        raise

    yield

    # 关闭时清理数据库连接
    try:
        await Tortoise.close_connections()
        logger.info("Database connections closed successfully")
    except BaseException:
        # 捕获所有异常包括 CancelledError，避免 reload 时输出错误堆栈
        pass


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        openapi_url="/openapi.json",
        middleware=make_middlewares(),
        lifespan=lifespan,
    )
    register_exceptions(app)
    register_routers(app, prefix="/api")
    return app


app = create_app()
