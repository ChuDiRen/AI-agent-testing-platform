"""角色相关的 Pydantic 模式"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    """角色基础模型"""
    role_name: str = Field(..., min_length=1, max_length=10, description="角色名称")
    remark: Optional[str] = Field(None, max_length=100, description="角色描述")


class RoleCreate(RoleBase):
    """角色创建模型"""
    pass


class RoleUpdate(BaseModel):
    """角色更新模型"""
    role_name: Optional[str] = Field(None, min_length=1, max_length=10, description="角色名称")
    remark: Optional[str] = Field(None, max_length=100, description="角色描述")


class RoleResponse(BaseModel):
    """角色响应模型 - 对应t_role表结构"""
    role_id: int = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    remark: Optional[str] = Field(None, description="角色描述")
    create_time: datetime = Field(..., description="创建时间")
    modify_time: Optional[datetime] = Field(None, description="修改时间")

    class Config:
        from_attributes = True

