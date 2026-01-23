"""
权限 Schema 模型
"""
from pydantic import BaseModel, Field
from typing import List, Any, Optional


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    alias: Optional[str]
    email: Optional[str]
    is_active: bool
    is_superuser: bool
    dept_id: Optional[int]
    roles: List[Any] = Field(default_factory=list)


class MenuNode(BaseModel):
    """菜单节点"""
    id: int
    name: str
    menu_type: str
    icon: Optional[str]
    path: str
    component: Optional[str]
    order: int
    parent_id: int
    is_hidden: bool
    keepalive: bool
    redirect: Optional[str]
    children: List[Any] = Field(default_factory=list)


class UserMenusResponse(BaseModel):
    """用户菜单响应"""
    menus: List[MenuNode]


class UserApisResponse(BaseModel):
    """用户API权限响应"""
    apis: List[str] = Field(description="API权限标识列表（格式：method+path）")


class PermissionCheckRequest(BaseModel):
    """权限检查请求"""
    api_path: str = Field(..., description="API路径")
    method: str = Field(..., description="HTTP方法")


class PermissionCheckResponse(BaseModel):
    """权限检查响应"""
    has_permission: bool = Field(description="是否有权限")
