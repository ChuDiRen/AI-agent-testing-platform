# Copyright (c) 2025 左岚. All rights reserved.
# DTO Layer - 数据传输对象层
# 职责：定义API请求和响应的数据结构，数据验证和序列化

from .base import (
    BaseRequest,
    BaseResponse,
    PaginationRequest,
    PaginationResponse,
    ApiResponse,
    PaginatedResponse
)
from .department_dto import *
from .indicator_parameter import *
from .menu_dto import *
from .role_dto import *
from .user import *
from .user_dto import *

__all__ = [
    "BaseRequest",
    "BaseResponse",
    "PaginationRequest",
    "PaginationResponse",
    "ApiResponse",
    "PaginatedResponse"
]
