# Copyright (c) 2025 左岚. All rights reserved.
# Middleware Module - 中间件模块
# 包含自定义中间件、CORS、认证等

from .auth import (
    rbac_auth,
    get_current_user,
    get_current_user_with_audit,
    require_user_view_with_audit,
    require_user_add_with_audit,
    require_user_update_with_audit,
    require_user_delete_with_audit,
    require_user_data_permission,
    require_role_data_permission,
    require_dept_data_permission
)
from .cors import setup_cors
from .logging import LoggingMiddleware, create_logging_middleware

__all__ = [
    "setup_cors",
    "LoggingMiddleware",
    "create_logging_middleware",
    "rbac_auth",
    "get_current_user",
    "get_current_user_with_audit",
    "require_user_view_with_audit",
    "require_user_add_with_audit",
    "require_user_update_with_audit",
    "require_user_delete_with_audit",
    "require_user_data_permission",
    "require_role_data_permission",
    "require_dept_data_permission"
]
