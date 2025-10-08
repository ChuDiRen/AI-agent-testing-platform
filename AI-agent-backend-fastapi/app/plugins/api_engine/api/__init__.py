"""
API引擎插件API路由
"""
from fastapi import APIRouter
from ..config import API_ENGINE_PLUGIN_CONFIG

# 创建主路由
router = APIRouter(
    prefix=API_ENGINE_PLUGIN_CONFIG.route_prefix,
    tags=["API引擎插件"]
)

# 导入子路由
from .suite import router as suite_router
from .case import router as case_router
from .execution import router as execution_router
from .keyword import router as keyword_router

# 挂载子路由
router.include_router(suite_router, prefix="/suites", tags=["套件管理"])
router.include_router(case_router, prefix="/cases", tags=["用例管理"])
router.include_router(execution_router, prefix="/executions", tags=["执行管理"])
router.include_router(keyword_router, prefix="/keywords", tags=["关键字管理"])


@router.get("/health")
async def plugin_health():
    """插件健康检查"""
    return {
        "status": "ok",
        "plugin": "api_engine",
        "version": "1.0.0"
    }

__all__ = ["router"]

