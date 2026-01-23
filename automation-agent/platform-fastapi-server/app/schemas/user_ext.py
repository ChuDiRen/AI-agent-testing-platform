"""
用户扩展 Schema 模型
用于 RBAC 权限系统的用户相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserCreateExt(BaseModel):
    """创建用户（扩展版）"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    alias: Optional[str] = Field(None, max_length=50, description="用户昵称")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    is_active: bool = Field(True, description="是否激活")
    is_superuser: bool = Field(False, description="是否超级管理员")
    dept_id: Optional[int] = Field(None, description="所属部门ID")
    role_ids: Optional[List[int]] = Field([], description="角色ID列表")


class UserUpdateExt(BaseModel):
    """更新用户（扩展版）"""
    alias: Optional[str] = Field(None, max_length=50, description="用户昵称")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_superuser: Optional[bool] = Field(None, description="是否超级管理员")
    dept_id: Optional[int] = Field(None, description="所属部门ID")
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表")


class UserResponseExt(BaseModel):
    """用户响应（扩展版）"""
    id: int
    username: str
    alias: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    is_active: bool
    is_superuser: bool
    dept_id: Optional[int]
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserChangePassword(BaseModel):
    """修改密码"""
    old_password: str = Field(..., min_length=6, description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")


class UserResetPassword(BaseModel):
    """重置密码"""
    user_id: int = Field(..., description="用户ID")
    new_password: str = Field(..., min_length=6, description="新密码")


class UserAssignRoles(BaseModel):
    """为用户分配角色"""
    user_id: int = Field(..., description="用户ID")
    role_ids: List[int] = Field(..., description="角色ID列表")
