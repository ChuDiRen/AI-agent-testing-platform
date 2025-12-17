"""
请求历史模型
记录接口调试的请求历史
"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiRequestHistory(SQLModel, table=True):
    """请求历史表"""
    __tablename__ = "t_api_request_history"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='历史ID')
    project_id: int = Field(description='所属项目ID')
    api_id: Optional[int] = Field(default=None, description='关联接口ID')
    api_name: Optional[str] = Field(default=None, max_length=255, description='接口名称')
    request_method: str = Field(max_length=20, description='请求方法')
    request_url: str = Field(max_length=2000, description='请求URL')
    request_headers: Optional[str] = Field(default=None, description='请求头JSON')
    request_body: Optional[str] = Field(default=None, description='请求体')
    request_body_type: Optional[str] = Field(default=None, max_length=50, description='请求体类型')
    response_status: Optional[int] = Field(default=None, description='响应状态码')
    response_headers: Optional[str] = Field(default=None, description='响应头JSON')
    response_body: Optional[str] = Field(default=None, description='响应体')
    response_time: Optional[int] = Field(default=None, description='响应时间(ms)')
    response_size: Optional[int] = Field(default=None, description='响应大小(bytes)')
    is_success: int = Field(default=1, description='是否成功(1是/0否)')
    error_message: Optional[str] = Field(default=None, max_length=1000, description='错误信息')
    is_favorite: int = Field(default=0, description='是否收藏(1是/0否)')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
