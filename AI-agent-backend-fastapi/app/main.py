"""FastAPI 应用主入口"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import APIException
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.api import auth, users, roles, permissions, user_roles, upload, menus, departments, role_menus, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    
    # 创建上传目录
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

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 添加限流中间件
app.add_middleware(
    RateLimitMiddleware,
    calls=settings.RATE_LIMIT_CALLS,
    period=settings.RATE_LIMIT_PERIOD
)

# 挂载静态文件目录（用于访问上传的文件）
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# 全局异常处理
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
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
app.include_router(permissions.router, prefix=settings.API_PREFIX, tags=["权限管理"])
app.include_router(user_roles.router, prefix=settings.API_PREFIX, tags=["用户角色关联"])
app.include_router(role_menus.router, prefix=settings.API_PREFIX, tags=["角色菜单关联"])
app.include_router(upload.router, prefix=settings.API_PREFIX, tags=["文件上传"])
app.include_router(dashboard.router, prefix=settings.API_PREFIX, tags=["仪表板"])


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

