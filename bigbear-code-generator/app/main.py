# -*- coding: utf-8 -*-
"""FastAPI应用入口"""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.database import init_db, init_data
from app.logger.logger import setup_logging, get_logger
from app.middleware.middleware import trace_id_middleware, cors_header_middleware

# 配置日志系统
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    consumer_threads = []
    try:
        logger.info("=" * 60)
        logger.info("Admin Platform 启动中...")
        logger.info("=" * 60)

        # 初始化数据库表
        init_db()

        # 初始化数据
        init_data()

        # 基础功能启动完成
        logger.info("✓ 基础功能模块已启动")

        logger.info("=" * 60)
        logger.info("🚀 应用启动完成！")
        logger.info("📖 API文档: http://localhost:5000/docs")
        logger.info("🔗 ReDoc文档: http://localhost:5000/redoc")
        logger.info("� 系统管理功能已启用")
        logger.info("🔐 登录认证功能已启用")
        logger.info("⚙️ 代码生成功能已启用")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()

    try:
        yield  # 应用运行期间
    except asyncio.CancelledError:
        # 正常关闭信号，不需要记录错误
        logger.info("收到关闭信号...")
    finally:
        # 关闭时执行清理工作
        logger.info("=" * 60)
        logger.info("正在优雅关闭应用...")

        # 关闭时执行清理工作
        logger.info("正在清理资源...")
        
        logger.info("👋 应用已安全关闭")
        logger.info("=" * 60)

# 创建FastAPI应用实例
application = FastAPI(
    title="Admin Platform API",
    description="基于 FastAPI + Vue3 + Naive UI 的现代化轻量管理平台",
    version="1.0.0",
    lifespan=lifespan  # 使用新的生命周期管理
)

# 配置CORS中间件
application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册自定义中间件
@application.middleware("http")
async def add_trace_id(request, call_next):
    return await trace_id_middleware(request, call_next)


@application.middleware("http")
async def add_cors_headers(request, call_next):
    return await cors_header_middleware(request, call_next)

# 注册路由
from app.api.v1.endpoints import AuthController
application.include_router(AuthController.router)

from app.api.v1.endpoints import UsersController
application.include_router(UsersController.router)

from app.api.v1.endpoints import RolesController
application.include_router(RolesController.router)

from app.api.v1.endpoints import MenusController
application.include_router(MenusController.router)

from app.api.v1.endpoints import DepartmentsController
application.include_router(DepartmentsController.router)

# 注册代码生成器模块路由
from app.api.v1.endpoints import GenTablesController
application.include_router(GenTablesController.module_route)

from app.api.v1.endpoints import GeneratorController
application.include_router(GeneratorController.module_route)

from app.api.v1.endpoints import StatisticsController
application.include_router(StatisticsController.router)

# 静态文件服务 (用于生产环境)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    application.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")
    
    @application.get("/")
    async def read_root():
        """返回前端应用的入口页面"""
        from fastapi.responses import FileResponse
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Admin Platform API", "docs": "/docs"}
    
    @application.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """处理前端路由,返回 index.html"""
        from fastapi.responses import FileResponse
        # 如果是 API 路径,跳过
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        # 检查文件是否存在
        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # 返回 index.html 用于 SPA 路由
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

# 基础功能路由配置完成
