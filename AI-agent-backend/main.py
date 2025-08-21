"""
AI Agent Backend - 主应用入口
企业级五层架构FastAPI应用
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.logger import get_logger
from app.db.session import create_tables
from app.controller.user_controller import router as user_router
from app.utils.exceptions import BaseAPIException

logger = get_logger(__name__)


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
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)


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
            "timestamp": "2023-01-01T00:00:00Z"  # 实际应该使用当前时间
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
            "timestamp": "2023-01-01T00:00:00Z"
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
            "timestamp": "2023-01-01T00:00:00Z"
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
        "timestamp": "2023-01-01T00:00:00Z"
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
app.include_router(user_router, prefix=settings.API_V1_PREFIX)


# 中间件：请求日志
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    记录HTTP请求日志
    """
    # 记录请求开始
    logger.info(f"Request: {request.method} {request.url}")
    
    # 处理请求
    response = await call_next(request)
    
    # 记录响应
    logger.info(f"Response: {response.status_code}")
    
    return response


if __name__ == "__main__":
    # 直接运行应用
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
