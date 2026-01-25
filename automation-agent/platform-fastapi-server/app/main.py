"""
FastAPI 应用主入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.rabbitmq import RabbitMQManager
from app.core.deps import get_current_user
from app.core.middleware.audit import create_audit_middleware
from app.api.v1.endpoints import (
    login, 
    api_info, 
    api_info_case, 
    api_history, 
    api_collection_info, 
    robot_config, 
    user, 
    user_menu,
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
    api_test_plan_chart,
    permission,
    role_endpoint,
    menu_endpoint,
    dept_endpoint,
    api_resource_endpoint,
    audit_log_endpoint,
    settings,
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
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"]
)

# 注册审计日志中间件
create_audit_middleware(app)


@app.middleware("http")
async def verify_token_middleware(request: Request, call_next):
    """JWT Token 验证中间件"""
    from app.core.logger import logger
    
    # 跳过 OPTIONS 预检请求
    if request.method == "OPTIONS":
        return await call_next(request)
    
    # 白名单路径
    whitelist = [
        "/login",
        "/api/v1/login", 
        "/docs",
        "/openapi.json",
        "/redoc",
        "/health",
        "/",
        "/api/settings",
        "/api/settings/"
    ]
    
    if request.url.path in whitelist or request.url.path.startswith("/api/settings"):
        return await call_next(request)
    
    try:
        # 获取 Token
        token = request.headers.get("token")
        if not token:
            from fastapi import status
            from fastapi.responses import JSONResponse
            logger.warning(f"请求 {request.url.path} 缺少 token")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"code": 401, "message": "未登录", "data": None}
            )
        
        # 验证 Token
        from app.core.security import verify_token
        payload = verify_token(token)
        if not payload:
            from fastapi import status
            from fastapi.responses import JSONResponse
            logger.warning(f"请求 {request.url.path} 的 token 验证失败")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"code": 401, "message": "Token 失效", "data": None}
            )
        
        # 保存到 request.state
        request.state.username = payload.get('username')
        request.state.user_id = payload.get('user_id')
        request.state.payload = payload
        
        response = await call_next(request)
        return response
    except HTTPException as e:
        # HTTPException直接抛出，让FastAPI处理
        raise
    except Exception as e:
        logger.error(f"Token 验证中间件异常: {str(e)}", exc_info=True)
        from fastapi import status
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 500, "message": f"服务器内部错误: {str(e)}", "data": None}
        )


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
    user_menu.router,
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

app.include_router(
    permission.router,
    prefix="/api/v1"
)

app.include_router(
    role_endpoint.router,
    prefix="/api/v1"
)

app.include_router(
    menu_endpoint.router,
    prefix="/api/v1"
)

app.include_router(
    dept_endpoint.router,
    prefix="/api/v1"
)

app.include_router(
    api_resource_endpoint.router,
    prefix="/api/v1"
)

app.include_router(
    audit_log_endpoint.router,
    prefix="/api/v1"
)

app.include_router(
    settings.router,
    prefix="/api"
)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    from app.core.logger import logger
    logger.info("FastAPI 应用启动中...")
    
    # 初始化统一缓存管理器（Redis→内存缓存自动降级）
    try:
        from app.core.unified_cache import cache_manager
        await cache_manager.initialize()
        cache_type = cache_manager.get_backend_type()
        logger.info(f"缓存管理器初始化成功: {cache_type}")
    except Exception as e:
        logger.error(f"缓存管理器初始化失败: {e}")
    
    # 初始化统一队列管理器（RabbitMQ→内存队列自动降级）
    try:
        from app.core.unified_queue import queue_manager
        await queue_manager.initialize()
        queue_type = queue_manager.get_backend_type()
        logger.info(f"队列管理器初始化成功: {queue_type}")
        
        # 定义队列消息处理回调
        from app.core.logger import logger
        
        async def web_queue_callback(message):
            """Web队列回调"""
            logger.info(f"收到Web队列消息: {message}")
        
        async def app_queue_callback(message):
            """App队列回调"""
            logger.info(f"收到App队列消息: {message}")
        
        async def api_queue_callback(message):
            """API队列回调"""
            logger.info(f"收到API队列消息: {message}")
        
        # 构建队列配置
        queue_configs = {}
        callbacks = {
            "web_queue": web_queue_callback,
            "app_queue": app_queue_callback,
            "api_queue": api_queue_callback
        }
        
        for queue_name, worker_count in settings.QUEUE_LIST:
            queue_configs[queue_name] = {
                "worker_count": worker_count,
                "callback": callbacks.get(queue_name)
            }
        
        # 启动所有队列消费者
        await queue_manager.start_all(queue_configs)
        logger.info("队列消费者已启动")
    except Exception as e:
        logger.error(f"队列管理器初始化失败: {e}")
    
    # 初始化数据库（MySQL→SQLite自动降级）
    try:
        from app.core.logger import logger
        from app.db.session import create_database_engine, get_database_type
        await create_database_engine()
        from app.db.init_db import init_database
        await init_database()
        db_type = get_database_type()
        logger.info(f"数据库初始化成功: {db_type}")
    except Exception as e:
        from app.core.logger import logger
        logger.error(f"数据库初始化失败: {e}")
        # 数据库初始化失败不影响应用启动，继续启动
    
    logger.info("FastAPI 应用启动完成!")
    logger.info(f"API 文档: http://localhost:8000/docs")
    logger.info(f"ReDoc 文档: http://localhost:8000/redoc")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    from app.core.logger import logger
    logger.info("FastAPI 应用关闭中...")
    
    # 停止队列管理器
    try:
        from app.core.unified_queue import queue_manager
        await queue_manager.stop_all()
        logger.info("队列管理器已停止")
    except Exception as e:
        logger.error(f"停止队列管理器失败: {e}")
    
    # 关闭缓存管理器
    try:
        from app.core.unified_cache import cache_manager
        await cache_manager.close()
        logger.info("缓存管理器已关闭")
    except Exception as e:
        logger.error(f"关闭缓存管理器失败: {e}")


@app.get("/")
async def root():
    """根路径"""
    return {"message": "API 测试平台后端服务 - FastAPI", "version": "1.0.0"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "framework": "FastAPI", "version": "1.0.0"}
