"""
统一响应模型
"""
from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """统一响应格式"""

    code: int = Field(0, description="响应码，0表示成功，非0表示失败")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp() * 1000),
        description="时间戳（毫秒）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "success",
                "data": {},
                "timestamp": 1703404800000
            }
        }


class ErrorDetail(BaseModel):
    """错误详情"""

    field: str = Field(..., description="错误字段")
    message: str = Field(..., description="错误消息")


class ErrorResponseModel(BaseModel):
    """错误响应格式"""

    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    errors: list[ErrorDetail] = Field(default_factory=list, description="错误详情列表")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp() * 1000),
        description="时间戳（毫秒）"
    )


class PageResponseModel(BaseModel, Generic[T]):
    """分页响应模型"""

    code: int = 0
    message: str = "success"
    data: Optional[PageData[T]] = None
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp() * 1000)
    )


class PageData(BaseModel, Generic[T]):
    """分页数据"""

    items: list[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(0, description="总数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页数量")
    pages: int = Field(0, description="总页数")


class ResponseHelper:
    """响应辅助类"""

    @staticmethod
    def ok(data: Optional[Any] = None, message: str = "success") -> ResponseModel:
        """成功响应"""
        return ResponseModel(code=0, message=message, data=data)

    @staticmethod
    def error(code: int = 500, message: str = "操作失败", errors: list = None) -> ErrorResponseModel:
        """错误响应"""
        return ErrorResponseModel(
            code=code,
            message=message,
            errors=errors or []
        )

    @staticmethod
    def page(
        items: list,
        total: int,
        page: int = 1,
        page_size: int = 20
    ) -> PageResponseModel:
        """分页响应"""
        pages = (total + page_size - 1) // page_size if total > 0 else 0
        page_data = PageData(items=items, total=total, page=page, page_size=page_size, pages=pages)
        return PageResponseModel(data=page_data)


# 全局响应辅助实例
respModel = ResponseHelper()
