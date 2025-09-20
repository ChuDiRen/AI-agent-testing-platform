# Copyright (c) 2025 左岚. All rights reserved.
"""
API响应工具
提供标准化的API响应格式
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.logger import get_logger

logger = get_logger(__name__)


class StandardResponse(BaseModel):
    """标准API响应格式"""
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None
    error_data: Optional[Dict[str, Any]] = None
    timestamp: str
    request_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


class PaginatedResponse(StandardResponse):
    """分页响应格式"""
    data: Optional[Dict[str, Any]] = None
    pagination: Optional[Dict[str, Any]] = None


class ResponseBuilder:
    """响应构建器"""
    
    @staticmethod
    def success(data: Any = None, 
                message: str = "操作成功",
                request_id: Optional[str] = None) -> StandardResponse:
        """构建成功响应"""
        return StandardResponse(
            success=True,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat() + "Z",
            request_id=request_id
        )
    
    @staticmethod
    def error(message: str = "操作失败",
              error_code: Optional[str] = None,
              error_data: Optional[Dict[str, Any]] = None,
              request_id: Optional[str] = None) -> StandardResponse:
        """构建错误响应"""
        return StandardResponse(
            success=False,
            message=message,
            error_code=error_code,
            error_data=error_data or {},
            timestamp=datetime.now().isoformat() + "Z",
            request_id=request_id
        )
    
    @staticmethod
    def paginated(data: List[Any],
                  total: int,
                  page: int,
                  page_size: int,
                  message: str = "获取数据成功",
                  request_id: Optional[str] = None) -> PaginatedResponse:
        """构建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        
        return PaginatedResponse(
            success=True,
            message=message,
            data={
                "items": data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            pagination={
                "current_page": page,
                "total_pages": total_pages,
                "page_size": page_size,
                "total_items": total,
                "has_next_page": page < total_pages,
                "has_previous_page": page > 1
            },
            timestamp=datetime.now().isoformat() + "Z",
            request_id=request_id
        )


class APIResponse:
    """API响应工具类"""
    
    @staticmethod
    def success(data: Any = None, 
                message: str = "操作成功",
                status_code: int = status.HTTP_200_OK,
                headers: Optional[Dict[str, str]] = None) -> JSONResponse:
        """返回成功响应"""
        response_data = ResponseBuilder.success(data=data, message=message)
        return JSONResponse(
            content=response_data.dict(),
            status_code=status_code,
            headers=headers
        )
    
    @staticmethod
    def error(message: str = "操作失败",
              error_code: Optional[str] = None,
              error_data: Optional[Dict[str, Any]] = None,
              status_code: int = status.HTTP_400_BAD_REQUEST,
              headers: Optional[Dict[str, str]] = None) -> JSONResponse:
        """返回错误响应"""
        response_data = ResponseBuilder.error(
            message=message,
            error_code=error_code,
            error_data=error_data
        )
        return JSONResponse(
            content=response_data.dict(),
            status_code=status_code,
            headers=headers
        )
    
    @staticmethod
    def created(data: Any = None,
                message: str = "创建成功") -> JSONResponse:
        """返回创建成功响应"""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def not_found(message: str = "资源不存在") -> JSONResponse:
        """返回404响应"""
        return APIResponse.error(
            message=message,
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def forbidden(message: str = "权限不足") -> JSONResponse:
        """返回403响应"""
        return APIResponse.error(
            message=message,
            error_code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def unauthorized(message: str = "未授权访问") -> JSONResponse:
        """返回401响应"""
        return APIResponse.error(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def validation_error(errors: List[Dict[str, Any]],
                        message: str = "数据验证失败") -> JSONResponse:
        """返回验证错误响应"""
        return APIResponse.error(
            message=message,
            error_code="VALIDATION_ERROR",
            error_data={"validation_errors": errors},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    @staticmethod
    def internal_error(message: str = "服务器内部错误") -> JSONResponse:
        """返回500响应"""
        return APIResponse.error(
            message=message,
            error_code="INTERNAL_SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# 快捷响应函数
def success_response(data: Any = None, message: str = "操作成功") -> JSONResponse:
    """快捷成功响应"""
    return APIResponse.success(data=data, message=message)


def error_response(message: str = "操作失败", 
                  error_code: Optional[str] = None,
                  status_code: int = status.HTTP_400_BAD_REQUEST) -> JSONResponse:
    """快捷错误响应"""
    return APIResponse.error(
        message=message,
        error_code=error_code,
        status_code=status_code
    )


# 导出响应工具
__all__ = [
    "StandardResponse", 
    "PaginatedResponse", 
    "ResponseBuilder", 
    "APIResponse",
    "success_response",
    "error_response"
]
