# Middleware Module - 中间件模块
# 包含自定义中间件、CORS、认证等

from .cors import setup_cors
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
from .logging import LoggingMiddleware, create_logging_middleware

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
    "create_logging_middleware"
]
