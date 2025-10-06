# Copyright (c) 2025 左岚. All rights reserved.
"""FastAPI 应用主入口"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from app.core.config import settings
from app.core.database import init_db, check_db_empty, init_data
from app.core.exceptions import BaseAPIException
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.api import auth, users, roles, user_roles, upload, menus, departments, role_menus, dashboard, notifications, data_management, testcases, reports, ai, knowledge, test_data

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 - 智能初始化"""
    # 1. 初始化数据库表结构
    await init_db()

    # 2. 智能检查并初始化数据
    try:
        is_empty = await check_db_empty()
        if is_empty:
            logger.info("🔍 检测到数据库为空，开始自动初始化数据...")
            await init_data()
            logger.info("✅ 数据库自动初始化完成")
        else:
            logger.info("✅ 数据库已有数据，跳过初始化")
    except Exception as e:
        logger.error(f"❌ 数据库初始化检查失败: {e}")

    # 3. 创建上传目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/avatars", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/files", exist_ok=True)

    yield
    # 关闭时的清理操作
    pass


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于 RBAC 权限模型的 FastAPI 后端系统",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 添加限流中间件（最先添加，最后执行）
app.add_middleware(
    RateLimitMiddleware,
    calls=settings.RATE_LIMIT_CALLS,
    period=settings.RATE_LIMIT_PERIOD
)

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 配置 CORS（最后添加，最先执行）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600  # 预检请求缓存时间
)

# 挂载静态文件目录（用于访问上传的文件）
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# 全局异常处理
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """处理自定义API异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "data": exc.details
        }
    )


# 注册路由
app.include_router(auth.router, prefix=settings.API_PREFIX, tags=["认证"])
app.include_router(users.router, prefix=settings.API_PREFIX, tags=["用户管理"])
app.include_router(roles.router, prefix=settings.API_PREFIX, tags=["角色管理"])
app.include_router(menus.router, prefix=settings.API_PREFIX, tags=["菜单管理"])
app.include_router(departments.router, prefix=settings.API_PREFIX, tags=["部门管理"])
app.include_router(user_roles.router, prefix=settings.API_PREFIX, tags=["用户角色关联"])
app.include_router(role_menus.router, prefix=settings.API_PREFIX, tags=["角色菜单关联"])
app.include_router(upload.router, prefix=settings.API_PREFIX, tags=["文件上传"])
app.include_router(dashboard.router, prefix=settings.API_PREFIX, tags=["仪表板"])
app.include_router(notifications.router, prefix=f"{settings.API_PREFIX}/notifications", tags=["消息通知"])
app.include_router(data_management.router, prefix=f"{settings.API_PREFIX}/data", tags=["数据管理"])
app.include_router(testcases.router, prefix=f"{settings.API_PREFIX}/testcases", tags=["测试用例"])
app.include_router(reports.router, prefix=f"{settings.API_PREFIX}/reports", tags=["测试报告"])
app.include_router(test_data.router, prefix=f"{settings.API_PREFIX}", tags=["测试数据管理"])
app.include_router(ai.router, prefix=f"{settings.API_PREFIX}/ai", tags=["AI助手"])
app.include_router(knowledge.router, prefix=f"{settings.API_PREFIX}", tags=["知识库"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to FastAPI RBAC Backend System",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }

