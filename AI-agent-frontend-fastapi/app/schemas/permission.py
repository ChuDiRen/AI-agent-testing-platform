"""权限（菜单）相关的 Pydantic 模式"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PermissionBase(BaseModel):
    """权限基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="权限名称")
    code: str = Field(..., min_length=1, max_length=100, description="权限代码")
    resource: Optional[str] = Field(None, max_length=100, description="资源标识")
    action: Optional[str] = Field(None, max_length=50, description="操作类型")
    description: Optional[str] = Field(None, max_length=200, description="权限描述")


class PermissionCreate(PermissionBase):
    """权限创建模型"""
    pass


class PermissionUpdate(BaseModel):
    """权限更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="权限名称")
    code: Optional[str] = Field(None, min_length=1, max_length=100, description="权限代码")
    resource: Optional[str] = Field(None, max_length=100, description="资源标识")
    action: Optional[str] = Field(None, max_length=50, description="操作类型")
    description: Optional[str] = Field(None, max_length=200, description="权限描述")
    is_active: Optional[bool] = Field(None, description="是否激活")


class PermissionResponse(PermissionBase):
    """权限响应模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

