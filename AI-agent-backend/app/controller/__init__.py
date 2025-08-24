# Copyright (c) 2025 左岚. All rights reserved.
# Controller Layer - HTTP请求处理层
# 职责：处理HTTP请求和响应，参数验证和格式化，调用Service层处理业务

from .base import BaseController
from .department_controller import router as department_router
from .menu_controller import router as menu_router
from .rbac_user_controller import router as rbac_user_router
from .role_controller import router as role_router
from .permission_controller import router as permission_router

__all__ = [
    "BaseController",
    "role_router",
    "menu_router",
    "department_router",
    "rbac_user_router"
]
