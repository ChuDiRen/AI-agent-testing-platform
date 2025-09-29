from fastapi import APIRouter

from .knowledge import router as knowledge_router
from .base import router as base_router
from .user import router as user_router
from .role import router as role_router
from .menu import router as menu_router

api_v1_router = APIRouter()

# 注册路由
api_v1_router.include_router(base_router, prefix="/base", tags=["基础模块"])
api_v1_router.include_router(user_router, prefix="/user", tags=["用户管理"])
api_v1_router.include_router(role_router, prefix="/role", tags=["角色管理"])
api_v1_router.include_router(menu_router, prefix="/menu", tags=["菜单管理"])
api_v1_router.include_router(knowledge_router, prefix="/knowledge", tags=["知识库管理"])
