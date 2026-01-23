"""
角色 Schema 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    """角色基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    desc: Optional[str] = Field(None, max_length=200, description="角色描述")


class RoleCreate(RoleBase):
    """创建角色"""
    pass


class RoleUpdate(RoleBase):
    """更新角色"""
    pass


class RoleResponse(RoleBase):
    """角色响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoleDetailResponse(RoleResponse):
    """角色详情响应（包含用户数量）"""
    user_count: int = Field(0, description="用户数量")


class RoleAssignMenus(BaseModel):
    """为角色分配菜单"""
    role_id: int = Field(..., description="角色ID")
    menu_ids: List[int] = Field(..., description="菜单ID列表")


class RoleAssignApis(BaseModel):
    """为角色分配API"""
    role_id: int = Field(..., description="角色ID")
    api_ids: List[int] = Field(..., description="API ID列表")
