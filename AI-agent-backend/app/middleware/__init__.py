# Copyright (c) 2025 左岚. All rights reserved.
# Middleware Module - 中间件模块
# 包含自定义中间件、CORS、认证等

from .auth import (
    AuthMiddleware,
    auth_middleware,
    get_current_user_id,
    require_authentication,
    get_current_user,
    require_admin,
    require_superuser,
    require_verified_user,
    optional_authentication
)
from .cors import setup_cors
from .logging import LoggingMiddleware, create_logging_middleware
from .rbac_auth import (
    rbac_auth,
    get_current_user as rbac_get_current_user,
    require_user_view,
    require_user_add,
    require_user_update,
    require_user_delete,
    require_admin_role
)

__all__ = [
    "setup_cors",
    "AuthMiddleware",
    "auth_middleware",
    "get_current_user_id",
    "require_authentication",
    "get_current_user",
    "require_admin",
    "require_superuser",
    "require_verified_user",
    "optional_authentication",
    "LoggingMiddleware",
    "create_logging_middleware",
    "rbac_auth",
    "rbac_get_current_user",
    "require_user_view",
    "require_user_add",
    "require_user_update",
    "require_user_delete",
    "require_admin_role"
]
