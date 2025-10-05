"""通用响应模式"""
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, Any

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    success: bool = Field(default=True, description="请求是否成功")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    error_code: Optional[str] = Field(default=None, description="错误代码")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "操作成功",
                "data": None,
                "error_code": None
            }
        }

    @classmethod
    def success_response(cls, data: Optional[T] = None, message: str = "操作成功") -> "APIResponse[T]":
        """创建成功响应"""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str = "操作失败", error_code: Optional[str] = None) -> "APIResponse[T]":
        """创建错误响应"""
        return cls(success=False, message=message, error_code=error_code, data=None)

