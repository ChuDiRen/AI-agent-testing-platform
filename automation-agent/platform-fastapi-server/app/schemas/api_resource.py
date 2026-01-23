"""
API资源 Schema 模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApiResourceBase(BaseModel):
    """API资源基础模型"""
    path: str = Field(..., max_length=500, description="API路径")
    method: str = Field(..., max_length=10, description="HTTP方法")
    summary: Optional[str] = Field(None, max_length=200, description="API说明")
    tags: Optional[str] = Field(None, max_length=200, description="API标签")


class ApiResourceCreate(ApiResourceBase):
    """创建API资源"""
    pass


class ApiResourceUpdate(ApiResourceBase):
    """更新API资源"""
    pass


class ApiResourceResponse(ApiResourceBase):
    """API资源响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApiRefreshRequest(BaseModel):
    """刷新API列表请求"""
    pass
