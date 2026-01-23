"""
审计日志 Schema 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class AuditLogBase(BaseModel):
    """审计日志基础模型"""
    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, max_length=50, description="用户名")
    module: Optional[str] = Field(None, max_length=50, description="模块名称")
    summary: Optional[str] = Field(None, max_length=200, description="操作摘要")
    method: Optional[str] = Field(None, max_length=10, description="HTTP方法")
    path: Optional[str] = Field(None, max_length=500, description="请求路径")
    status: int = Field(0, description="响应状态码")
    response_time: Optional[float] = Field(None, description="响应时间（毫秒）")
    request_args: Optional[Any] = Field(None, description="请求参数")
    response_body: Optional[Any] = Field(None, description="响应体")


class AuditLogResponse(AuditLogBase):
    """审计日志响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
