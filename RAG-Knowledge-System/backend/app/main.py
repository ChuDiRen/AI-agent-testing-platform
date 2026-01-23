"""
主应用入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config.settings import settings
from core.logger import setup_logger
from db.session import engine
from sqlmodel import SQLModel

# 导入API路由
from app.api.auth_api import router as auth_router
from app.api.user_api import router as user_router
from app.api.document_api import router as document_router
from app.api.document_index_api import router as document_index_router
from app.api.chat_api import router as chat_router
from app.api.feedback_api import router as feedback_router
from app.api.operation_log_api import router as operation_log_router

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    启动和关闭时执行的操作
    """
    # 启动时
    logger.info("=" * 50)
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    logger.info("=" * 50)
    logger.info(f"环境: {settings.ENVIRONMENT}")
    logger.info(f"调试模式: {settings.DEBUG}")

    # 创建数据库表
    from models import user, role, permission, document, document_chunk, vector_store, feedback, operation_log, system_config
    logger.info("创建数据库表...")
    SQLModel.metadata.create_all(engine)

    logger.info(f"{settings.APP_NAME} 启动完成！")
    logger.info(f"API文档地址: http://localhost:8000/docs")
    logger.info("=" * 50)

    yield

    # 关闭时
    logger.info("=" * 50)
    logger.info(f"{settings.APP_NAME} 关闭中...")
    logger.info("=" * 50)


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="企业级智能知识库管理系统",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"全局异常: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": str(exc) if settings.DEBUG else "请联系管理员"
        }
    )


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# 注册API路由
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(user_router, prefix=settings.API_V1_PREFIX)
app.include_router(document_router, prefix=settings.API_V1_PREFIX)
app.include_router(document_index_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(feedback_router, prefix=settings.API_V1_PREFIX)
app.include_router(operation_log_router, prefix=settings.API_V1_PREFIX)


# 注册依赖注入
from core.deps import get_rag_engine, get_llm_service, get_chat_service

# 可以在这里添加全局依赖
# app.dependency_overrides[...] = ...


