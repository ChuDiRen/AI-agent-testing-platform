"""
AI Agent Backend - 主应用入口
企业级五层架构FastAPI应用
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.controller.department_controller import router as department_router
from app.controller.menu_controller import router as menu_router
from app.controller.user_controller import router as rbac_user_router
from app.controller.role_controller import router as role_router
from app.controller.permission_controller import router as permission_router
from app.controller.dashboard_controller import router as dashboard_router
from app.controller.log_controller import router as log_router
from app.controller.log_config_controller import router as log_config_router
from app.controller.agent_controller import router as agent_router
from app.controller.test_case_controller import router as test_case_router
from app.controller.test_report_controller import router as test_report_router
from app.controller.ai_generation_controller import router as ai_generation_router
from app.controller.model_config_controller import router as model_config_router
from app.controller.chat_controller import router as chat_router
from app.controller.api_endpoint_controller import router as api_endpoint_router
from app.api.v1.knowledge import router as knowledge_router
from app.core.config import settings
from app.core.logger import get_logger
from app.db.session import create_tables, SessionLocal
from app.utils.exceptions import BaseAPIException

logger = get_logger(__name__)


def check_and_init_data():
    """
    检查并初始化数据库数据
    """
    db = SessionLocal()
    try:
        # 检查是否已有用户数据
        from app.entity.user import User
        user_count = db.query(User).count()

        if user_count == 0:
            logger.info("No users found, initializing database with default data...")

            # 导入并运行初始化脚本
            from scripts.init_db import create_initial_data
            create_initial_data()

            logger.info("Database initialized with default data successfully")
        else:
            logger.info(f"Database already has {user_count} users, skipping initialization")

    except Exception as e:
        logger.error(f"Failed to check/initialize data: {str(e)}")
        # 不抛出异常，让应用继续启动
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    logger.info("Starting AI Agent Backend...")

    # 创建数据库表
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

    # 检查并初始化数据
    check_and_init_data()

    logger.info("AI Agent Backend started successfully")

    yield

    # 关闭时执行
    logger.info("Shutting down AI Agent Backend...")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url=settings.DOCS_URL if not settings.is_production else None,
    redoc_url=settings.REDOC_URL if not settings.is_production else None,
    openapi_url=settings.OPENAPI_URL if not settings.is_production else None,
    lifespan=lifespan,
    redirect_slashes=True
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,  # 通配符与凭据不能同时使用
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
    expose_headers=["X-Total-Count", "X-Page-Count"],
    max_age=3600,
)

# 添加中间件
from app.middleware.logging import LoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware, RateLimitMiddleware, RequestValidationMiddleware

# 安全中间件
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_REQUESTS)
app.add_middleware(RequestValidationMiddleware)

# 日志中间件
app.add_middleware(LoggingMiddleware, log_requests=True, log_responses=True, log_to_db=True)


# 全局异常处理器
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """
    处理自定义API异常
    """
    logger.warning(f"API Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": getattr(exc, 'error_code', None),
            "error_data": getattr(exc, 'error_data', {}),
            "timestamp": datetime.now().isoformat() + "Z"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求验证异常
    """
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "error_data": {
                "errors": exc.errors(),
                "body": exc.body
            },
            "timestamp": datetime.now().isoformat() + "Z"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    处理通用异常
    """
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "error_data": {},
            "timestamp": datetime.now().isoformat() + "Z"
        }
    )


# 健康检查端点
@app.get("/health", tags=["health"])
async def health_check():
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat() + "Z"
    }


# 根端点
@app.get("/", tags=["root"])
async def root():
    """
    根端点
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs_url": settings.DOCS_URL,
        "environment": settings.ENVIRONMENT
    }


# 注册路由
app.include_router(role_router, prefix=settings.API_V1_PREFIX)
app.include_router(menu_router, prefix=settings.API_V1_PREFIX)
app.include_router(department_router, prefix=settings.API_V1_PREFIX)
app.include_router(rbac_user_router, prefix=settings.API_V1_PREFIX)
app.include_router(permission_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(log_router, prefix=settings.API_V1_PREFIX)
app.include_router(log_config_router, prefix=settings.API_V1_PREFIX)
app.include_router(agent_router, prefix=settings.API_V1_PREFIX)
app.include_router(test_case_router, prefix=settings.API_V1_PREFIX)
app.include_router(test_report_router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_generation_router, prefix=settings.API_V1_PREFIX)
app.include_router(model_config_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(api_endpoint_router, prefix=settings.API_V1_PREFIX)  # API端点管理路由
app.include_router(knowledge_router, prefix=settings.API_V1_PREFIX)

# 静态文件服务
from fastapi.staticfiles import StaticFiles
import os

# 创建上传目录
uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

# 挂载静态文件服务
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# CORS 预检与兜底响应头
@app.middleware("http")
async def cors_preflight(request: Request, call_next):
    # 预检请求直接放行并返回必要头
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": ",".join(settings.ALLOWED_METHODS),
            "Access-Control-Allow-Headers": "*" if "*" in settings.ALLOWED_HEADERS else ",".join(settings.ALLOWED_HEADERS),
            "Access-Control-Max-Age": "3600",
        }
        return JSONResponse(status_code=200, content=None, headers=headers)
    # 正常请求继续
    response = await call_next(request)
    # 兜底添加CORS响应头
    response.headers.setdefault("Access-Control-Allow-Origin", "*")
    response.headers.setdefault("Access-Control-Expose-Headers", "X-Total-Count, X-Page-Count")
    return response

# 注释掉原有的简单日志中间件，已被LoggingMiddleware替代
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     """
#     记录HTTP请求日志
#     """
#     # 记录请求开始
#     logger.info(f"Request: {request.method} {request.url}")
#
#     # 处理请求
#     response = await call_next(request)
#
#     # 记录响应
#     logger.info(f"Response: {response.status_code}")
#
#     return response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # 使用导入字符串格式以支持reload
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        reload=True
    )
