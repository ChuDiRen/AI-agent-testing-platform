"""
请求历史Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ApiRequestHistoryQuery(BaseModel):
    """历史查询参数"""
    page: int = 1
    pageSize: int = 20
    project_id: Optional[int] = None
    api_id: Optional[int] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    is_success: Optional[int] = None
    is_favorite: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ApiRequestHistoryCreate(BaseModel):
    """创建历史记录"""
    project_id: int
    api_id: Optional[int] = None
    api_name: Optional[str] = None
    request_method: str
    request_url: str
    request_headers: Optional[str] = None
    request_body: Optional[str] = None
    request_body_type: Optional[str] = None
    response_status: Optional[int] = None
    response_headers: Optional[str] = None
    response_body: Optional[str] = None
    response_time: Optional[int] = None
    response_size: Optional[int] = None
    is_success: int = 1
    error_message: Optional[str] = None


class ApiRequestHistoryBatchDelete(BaseModel):
    """批量删除"""
    ids: List[int]


class ApiRequestHistoryClearParams(BaseModel):
    """清空历史参数"""
    project_id: int
    keep_favorites: bool = True  # 是否保留收藏
    days: Optional[int] = None  # 保留最近N天的记录
