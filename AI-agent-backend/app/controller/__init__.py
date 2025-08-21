# Controller Layer - HTTP请求处理层
# 职责：处理HTTP请求和响应，参数验证和格式化，调用Service层处理业务

from .base import BaseController
from .user_controller import UserController, router as user_router

__all__ = ["BaseController", "UserController", "user_router"]
