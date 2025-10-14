# -*- coding: utf-8 -*-
"""FastAPI应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import init_db, init_data
import uvicorn
import logging
import asyncio
from contextlib import asynccontextmanager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    try:
        logger.info("=" * 60)
        logger.info("AI Agent Testing Platform 启动中...")
        logger.info("=" * 60)

        # 初始化数据库表
        init_db()

        # 初始化数据
        init_data()

        logger.info("=" * 60)
        logger.info("🚀 应用启动完成！")
        logger.info("📖 API文档: http://localhost:8000/docs")
        logger.info("🔗 ReDoc文档: http://localhost:8000/redoc")
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
        logger.info("👋 应用已安全关闭")
        logger.info("=" * 60)

# 创建FastAPI应用实例
application = FastAPI(
    title="AI Agent Testing Platform API",
    description="API接口测试平台后端服务",
    version="2.0.0",
    lifespan=lifespan  # 使用新的生命周期管理
)

# 配置CORS
application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from login.api import LoginController
application.include_router(LoginController.module_route)

from sysmanage.api import UserController
application.include_router(UserController.module_route)

from sysmanage.api import RoleController
application.include_router(RoleController.module_route)

from sysmanage.api import MenuController
application.include_router(MenuController.module_route)

from sysmanage.api import DeptController
application.include_router(DeptController.module_route)

from apitest.api import ApiProjectContoller
application.include_router(ApiProjectContoller.module_route)

from apitest.api import ApiDbBaseController
application.include_router(ApiDbBaseController.module_route)

from apitest.api import ApiKeyWordController
application.include_router(ApiKeyWordController.module_route)

from apitest.api import ApiOperationTypeController
application.include_router(ApiOperationTypeController.module_route)

from apitest.api import ApiMetaController
application.include_router(ApiMetaController.module_route)

from apitest.api import ApiInfoController
application.include_router(ApiInfoController.module_route)

from apitest.api import ApiGroupController
application.include_router(ApiGroupController.module_route)

from apitest.api import ApiTestController
application.include_router(ApiTestController.module_route)

from apitest.api import ApiTestHistoryController
application.include_router(ApiTestHistoryController.module_route)

# 移除旧的 on_event 装饰器，已使用 lifespan 替代

@application.get("/", tags=["根路径"]) # 根路径接口
def root():
    return {
        "message": "AI Agent Testing Platform API",
        "version": "2.0.0",
        "docs": "/docs"
    }

