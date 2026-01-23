"""
FastAPI 应用主入口 - AI Agent 编排平台
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logger import setup_logger

# 创建日志器
logger = setup_logger(name="app", level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动事件
    logger.info("=" * 60)
    logger.info("AI Agent 编排平台启动中...")
    logger.info("=" * 60)

    # 初始化数据库连接
    from app.db.session import init_db
    await init_db()

    logger.info("✅ AI Agent 编排平台启动完成!")
    logger.info(f"API 文档: http://localhost:{settings.PORT}/docs")
    logger.info(f"ReDoc 文档: http://localhost:{settings.PORT}/redoc")

    yield

    # 关闭事件
    logger.info("AI Agent 编排平台关闭中...")


# 创建 FastAPI 应用
app = FastAPI(
    title="AI Agent 编排平台",
    description="AI Agent 编排与工作流管理平台后端服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """请求日志中间件"""
    import time
    import uuid

    # 生成请求 ID
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    # 记录请求开始
    start_time = time.time()

    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None,
        }
    )

    # 处理请求
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "error": str(e),
            },
            exc_info=True
        )
        raise

    # 记录请求结束
    duration = time.time() - start_time
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2)
        }
    )

    # 添加响应头
    response.headers["X-Request-ID"] = request_id

    return response


# 导入路由（延迟导入以避免循环依赖）
from app.api.v1.endpoints import agents, workflows, tools, executions, billing, auth, workflow_version, batch, export, advanced_node
from app.services.monitoring_service import router as monitoring_router

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(tools.router, prefix="/api/v1")
app.include_router(executions.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(monitoring_router, prefix="/api/v1")
app.include_router(workflow_version.router, prefix="/api/v1")
app.include_router(batch.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")
app.include_router(advanced_node.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI Agent 编排平台后端服务",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "framework": "FastAPI",
        "version": "1.0.0"
    }
