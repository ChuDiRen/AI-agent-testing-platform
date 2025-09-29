"""
认证相关DTO - 兼容vue-fastapi-admin格式
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "123456"
            }
        }


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="访问令牌")
    username: str = Field(..., description="用户名")
    token_type: str = Field(default="bearer", description="令牌类型")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "username": "admin",
                "token_type": "bearer"
            }
        }


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    avatar: str = Field(..., description="头像URL")
    roles: List[str] = Field(default=[], description="角色列表")
    is_superuser: bool = Field(default=False, description="是否超级用户")
    is_active: bool = Field(default=True, description="是否激活")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "avatar": "https://avatars.githubusercontent.com/u/54677442?v=4",
                "roles": ["管理员"],
                "is_superuser": True,
                "is_active": True
            }
        }


class UpdatePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "123456",
                "new_password": "newpassword123"
            }
        }
