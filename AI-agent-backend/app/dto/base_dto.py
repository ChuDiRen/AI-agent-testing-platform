"""
基础响应DTO - 兼容vue-fastapi-admin格式
"""

from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型"""
    code: int = Field(..., description="响应码")
    msg: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": None
            }
        }


class Success(BaseResponse[T]):
    """成功响应"""
    def __init__(self, data: Optional[T] = None, msg: str = "success", **kwargs):
        super().__init__(code=200, msg=msg, data=data, **kwargs)


class Fail(BaseResponse[T]):
    """失败响应"""
    def __init__(self, msg: str = "error", code: int = 400, data: Optional[T] = None, **kwargs):
        super().__init__(code=code, msg=msg, data=data, **kwargs)


class PageResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: list[T] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总数量")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页数量")
    pages: int = Field(default=0, description="总页数")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "page_size": 20,
                "pages": 0
            }
        }


class PageRequest(BaseModel):
    """分页请求"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, description="搜索关键词")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "keyword": ""
            }
        }
