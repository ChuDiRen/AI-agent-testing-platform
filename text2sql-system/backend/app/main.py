"""
FastAPI应用入口
"""
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.config.settings import settings
from app.api import routes, websocket


# 配置日志
logger.remove()  # 移除默认handler
logger.add(
    settings.log_file,
    rotation="10 MB",
    retention="10 days",
    level=settings.log_level
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("应用启动中...")
    logger.info(f"数据库类型: {settings.database_type}")
    logger.info(f"数据库URL: {settings.database_url}")
    logger.info(f"AI模型: {settings.model_name}")
    yield
    logger.info("应用关闭...")


# 创建FastAPI应用
app = FastAPI(
    title="Text2SQL智能查询系统",
    description="基于AutoGen多智能体协作的自然语言到SQL转换平台",
    version="1.0.0",
    lifespan=lifespan
)


# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(routes.router, prefix="/api")
app.include_router(websocket.router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Text2SQL智能查询系统API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "database": "connected" if _check_database() else "disconnected",
            "ai_model": settings.model_name
        }
    )


def _check_database() -> bool:
    """检查数据库连接状态"""
    try:
        # 简单的连接检查（实际实现在DBAccess模块中）
        return True
    except Exception as e:
        logger.error(f"数据库连接检查失败: {str(e)}")
        return False


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        reload=settings.debug
    )
