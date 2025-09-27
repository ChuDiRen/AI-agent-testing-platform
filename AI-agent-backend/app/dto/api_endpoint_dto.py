# Copyright (c) 2025 左岚. All rights reserved.
"""
API端点DTO
定义API管理相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field

from app.dto.base import BaseResponse


class ApiEndpointCreateRequest(BaseModel):
    """
    API端点创建请求DTO
    """
    path: str = Field(..., max_length=500, description="API路径")
    method: str = Field(..., max_length=10, description="HTTP方法")
    name: str = Field(..., max_length=100, description="API名称")
    description: Optional[str] = Field(None, description="API描述")
    module: Optional[str] = Field(None, max_length=100, description="所属模块")
    permission: Optional[str] = Field(None, max_length=100, description="权限标识")
    version: Optional[str] = Field("v1", max_length=20, description="API版本")
    request_example: Optional[Dict[str, Any]] = Field(None, description="请求参数示例")
    response_example: Optional[Dict[str, Any]] = Field(None, description="响应示例")

    class Config:
        json_schema_extra = {
            "example": {
                "path": "/api/v1/users",
                "method": "GET",
                "name": "获取用户列表",
                "description": "获取系统中所有用户的列表",
                "module": "用户管理",
                "permission": "user:view",
                "version": "v1",
                "request_example": {
                    "page": 1,
                    "size": 10,
                    "keyword": "搜索关键词"
                },
                "response_example": {
                    "code": 200,
                    "message": "success",
                    "data": {
                        "items": [],
                        "total": 0
                    }
                }
            }
        }


class ApiEndpointUpdateRequest(BaseModel):
    """
    API端点更新请求DTO
    """
    name: Optional[str] = Field(None, max_length=100, description="API名称")
    description: Optional[str] = Field(None, description="API描述")
    status: Optional[str] = Field(None, description="API状态")
    module: Optional[str] = Field(None, max_length=100, description="所属模块")
    permission: Optional[str] = Field(None, max_length=100, description="权限标识")
    version: Optional[str] = Field(None, max_length=20, description="API版本")
    request_example: Optional[Dict[str, Any]] = Field(None, description="请求参数示例")
    response_example: Optional[Dict[str, Any]] = Field(None, description="响应示例")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "获取用户详情",
                "description": "根据用户ID获取用户详细信息",
                "status": "active",
                "module": "用户管理",
                "permission": "user:view"
            }
        }


class ApiEndpointQueryRequest(BaseModel):
    """
    API端点查询请求DTO
    """
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, description="搜索关键词")
    method: Optional[str] = Field(None, description="HTTP方法筛选")
    status: Optional[str] = Field(None, description="状态筛选")
    module: Optional[str] = Field(None, description="模块筛选")
    permission: Optional[str] = Field(None, description="权限筛选")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 10,
                "keyword": "用户",
                "method": "GET",
                "status": "active",
                "module": "用户管理"
            }
        }


class ApiEndpointResponse(BaseModel):
    """
    API端点响应DTO
    """
    id: int = Field(..., description="API端点ID")
    path: str = Field(..., description="API路径")
    method: str = Field(..., description="HTTP方法")
    name: str = Field(..., description="API名称")
    description: Optional[str] = Field(None, description="API描述")
    status: str = Field(..., description="API状态")
    module: Optional[str] = Field(None, description="所属模块")
    permission: Optional[str] = Field(None, description="权限标识")
    version: str = Field(..., description="API版本")
    request_example: Optional[Dict[str, Any]] = Field(None, description="请求参数示例")
    response_example: Optional[Dict[str, Any]] = Field(None, description="响应示例")
    
    # 统计数据
    total_calls: int = Field(0, description="总调用次数")
    success_calls: int = Field(0, description="成功调用次数")
    error_calls: int = Field(0, description="错误调用次数")
    success_rate: float = Field(0.0, description="成功率")
    avg_response_time: float = Field(0.0, description="平均响应时间")
    max_response_time: float = Field(0.0, description="最大响应时间")
    min_response_time: float = Field(0.0, description="最小响应时间")
    
    # 时间信息
    last_called_at: Optional[str] = Field(None, description="最后调用时间")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    created_by_id: int = Field(..., description="创建者ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "path": "/api/v1/users",
                "method": "GET",
                "name": "获取用户列表",
                "description": "获取系统中所有用户的列表",
                "status": "active",
                "module": "用户管理",
                "permission": "user:view",
                "version": "v1",
                "total_calls": 1250,
                "success_calls": 1200,
                "error_calls": 50,
                "success_rate": 96.0,
                "avg_response_time": 125.5,
                "max_response_time": 500.0,
                "min_response_time": 50.0,
                "last_called_at": "2025-01-27T10:30:00",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-27T10:30:00",
                "created_by_id": 1
            }
        }


class ApiEndpointListResponse(BaseResponse):
    """
    API端点列表响应DTO
    """
    items: List[ApiEndpointResponse] = Field(default=[], description="API端点列表")
    total: int = Field(0, description="总数量")
    page: int = Field(1, description="当前页码")
    size: int = Field(10, description="每页数量")
    pages: int = Field(0, description="总页数")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 50,
                "page": 1,
                "size": 10,
                "pages": 5
            }
        }


class ApiStatisticsResponse(BaseModel):
    """
    API统计响应DTO
    """
    total_apis: int = Field(0, description="API总数")
    active_apis: int = Field(0, description="激活API数")
    deprecated_apis: int = Field(0, description="废弃API数")
    maintenance_apis: int = Field(0, description="维护中API数")
    
    total_calls_today: int = Field(0, description="今日总调用次数")
    success_calls_today: int = Field(0, description="今日成功调用次数")
    error_calls_today: int = Field(0, description="今日错误调用次数")
    
    avg_response_time: float = Field(0.0, description="平均响应时间")
    top_apis: List[Dict[str, Any]] = Field(default=[], description="热门API")
    error_apis: List[Dict[str, Any]] = Field(default=[], description="错误率高的API")

    class Config:
        json_schema_extra = {
            "example": {
                "total_apis": 45,
                "active_apis": 40,
                "deprecated_apis": 3,
                "maintenance_apis": 2,
                "total_calls_today": 5000,
                "success_calls_today": 4800,
                "error_calls_today": 200,
                "avg_response_time": 150.5,
                "top_apis": [
                    {
                        "name": "获取用户列表",
                        "path": "/api/v1/users",
                        "calls": 1200
                    }
                ],
                "error_apis": [
                    {
                        "name": "删除用户",
                        "path": "/api/v1/users/{id}",
                        "error_rate": 15.5
                    }
                ]
            }
        }


class ApiCallLogResponse(BaseModel):
    """
    API调用日志响应DTO
    """
    id: int = Field(..., description="日志ID")
    api_id: int = Field(..., description="API端点ID")
    api_path: str = Field(..., description="API路径")
    method: str = Field(..., description="HTTP方法")
    status_code: int = Field(..., description="响应状态码")
    response_time: float = Field(..., description="响应时间(ms)")
    user_id: Optional[int] = Field(None, description="调用用户ID")
    ip_address: str = Field(..., description="客户端IP")
    user_agent: Optional[str] = Field(None, description="用户代理")
    request_data: Optional[Dict[str, Any]] = Field(None, description="请求数据")
    response_data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: str = Field(..., description="调用时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "api_id": 1,
                "api_path": "/api/v1/users",
                "method": "GET",
                "status_code": 200,
                "response_time": 125.5,
                "user_id": 1,
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "request_data": {"page": 1, "size": 10},
                "response_data": {"code": 200, "data": []},
                "error_message": None,
                "created_at": "2025-01-27T10:30:00"
            }
        }
