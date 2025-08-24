# Copyright (c) 2025 左岚. All rights reserved.
"""
日志DTO
定义日志相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogQueryRequest(BaseModel):
    """
    日志查询请求DTO
    """
    level: Optional[LogLevel] = Field(None, description="日志级别")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    module: Optional[str] = Field(None, description="模块名称")
    user: Optional[str] = Field(None, description="用户名")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")
    
    class Config:
        json_schema_extra = {
            "example": {
                "level": "INFO",
                "start_time": "2025-08-24T00:00:00",
                "end_time": "2025-08-24T23:59:59",
                "keyword": "登录",
                "page": 1,
                "size": 20
            }
        }


class LogResponse(BaseModel):
    """
    日志响应DTO
    """
    id: int = Field(..., description="日志ID")
    timestamp: datetime = Field(..., description="时间戳")
    level: LogLevel = Field(..., description="日志级别")
    module: str = Field(..., description="模块名称")
    message: str = Field(..., description="日志消息")
    user: Optional[str] = Field(None, description="用户名")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    details: Optional[str] = Field(None, description="详细信息")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "timestamp": "2025-08-24T14:30:00",
                "level": "INFO",
                "module": "auth",
                "message": "用户登录成功",
                "user": "admin",
                "ip_address": "127.0.0.1",
                "user_agent": "Mozilla/5.0...",
                "details": "登录详细信息"
            }
        }


class LogListResponse(BaseModel):
    """
    日志列表响应DTO
    """
    items: List[LogResponse] = Field(default=[], description="日志列表")
    total: int = Field(0, description="总数量")
    page: int = Field(1, description="当前页码")
    size: int = Field(20, description="每页大小")
    pages: int = Field(0, description="总页数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "size": 20,
                "pages": 5
            }
        }


class LogStatsResponse(BaseModel):
    """
    日志统计响应DTO
    """
    total_count: int = Field(0, description="总日志数")
    debug_count: int = Field(0, description="DEBUG级别数量")
    info_count: int = Field(0, description="INFO级别数量")
    warning_count: int = Field(0, description="WARNING级别数量")
    error_count: int = Field(0, description="ERROR级别数量")
    critical_count: int = Field(0, description="CRITICAL级别数量")
    today_count: int = Field(0, description="今日日志数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_count": 1000,
                "debug_count": 100,
                "info_count": 600,
                "warning_count": 200,
                "error_count": 80,
                "critical_count": 20,
                "today_count": 50
            }
        }
