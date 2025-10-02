"""通用响应模式"""
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[T] = None
    error_code: Optional[str] = None

