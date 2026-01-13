"""
FastAPI 应用主入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.rabbitmq import RabbitMQManager
from app.core.deps import get_current_user
from app.api.v1.endpoints import (
    login, 
    api_info, 
    api_info_case, 
    api_history, 
    api_collection_info, 
    robot_config, 
    user, 
    swagger_import,
    api_project,
    api_db_base,
    api_keyword,
    api_operation_type,
    api_meta,
    api_info_case_step,
    api_report_viewer,
    api_collection_detail,
    robot_msg_config,
    api_test_plan_chart
)
from app.utils.third_party_messenger import get_messenger

# 创建 FastAPI 应用
app = FastAPI(
    title="API 测试平台",
    description="API 自动化测试平台后端服务 - FastAPI 版本",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
async def verify_token_middleware(request: Request, call_next):
    """JWT Token 验证中间件"""
    # 白名单路径
    whitelist = [
        "/api/v1/login",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/health",
        "/"
    ]
    
    if request.url.path in whitelist:
        return await call_next(request)
    
    # 获取 Token
    token = request.headers.get("token")
    if not token:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录"
        )
    
    # 验证 Token
    from app.core.security import verify_token
    payload = verify_token(token)
    if not payload:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 失效"
        )
    
    # 保存到 request.state
    request.state.username = payload.get('username')
    request.state.payload = payload
    
    response = await call_next(request)
    return response


# 注册路由
app.include_router(
    login.router,
    prefix="/api/v1"
)

app.include_router(
    api_info.router,
    prefix="/api/v1"
)

app.include_router(
    api_info_case.router,
    prefix="/api/v1"
)

app.include_router(
    api_history.router,
    prefix="/api/v1"
)

app.include_router(
    api_collection_info.router,
    prefix="/api/v1"
)

app.include_router(
    robot_config.router,
    prefix="/api/v1"
)

app.include_router(
    user.router,
    prefix="/api/v1"
)

app.include_router(
    swagger_import.router,
    prefix="/api/v1"
)

app.include_router(
    api_project.router,
    prefix="/api/v1"
)

app.include_router(
    api_db_base.router,
    prefix="/api/v1"
)

app.include_router(
    api_keyword.router,
    prefix="/api/v1"
)

app.include_router(
    api_operation_type.router,
    prefix="/api/v1"
)

app.include_router(
    api_meta.router,
    prefix="/api/v1"
)

app.include_router(
    api_info_case_step.router,
    prefix="/api/v1"
)

app.include_router(
    api_report_viewer.router,
    prefix="/api/v1"
)

app.include_router(
    api_collection_detail.router,
    prefix="/api/v1"
)

app.include_router(
    robot_msg_config.router,
    prefix="/api/v1"
)

app.include_router(
    api_test_plan_chart.router,
    prefix="/api/v1"
)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("=" * 60)
    print("FastAPI 应用启动中...")
    print("=" * 60)
    
    # 启动 RabbitMQ 消费者
    try:
        from app.services.rabbitmq_consumer import rabbitmq_manager
        await rabbitmq_manager.start_workers()
        print("✅ RabbitMQ 消费者启动成功")
    except Exception as e:
        print(f"❌ RabbitMQ 消费者启动失败: {e}")
    
    print("=" * 60)
    print("FastAPI 应用启动完成!")
    print("=" * 60)
    print(f"API 文档: http://localhost:8000/docs")
    print(f"ReDoc 文档: http://localhost:8000/redoc")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("FastAPI 应用关闭中...")


@app.get("/")
async def root():
    """根路径"""
    return {"message": "API 测试平台后端服务 - FastAPI", "version": "1.0.0"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "framework": "FastAPI", "version": "1.0.0"}

