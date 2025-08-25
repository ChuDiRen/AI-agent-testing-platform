# Copyright (c) 2025 左岚. All rights reserved.
"""
用户DTO
定义用户相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, validator


class UserIdRequest(BaseModel):
    """
    用户ID请求DTO
    """
    user_id: int = Field(..., description="用户ID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1
            }
        }


class UserListRequest(BaseModel):
    """
    用户列表请求DTO
    """
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")
    username: Optional[str] = Field(None, description="用户名筛选")
    dept_id: Optional[int] = Field(None, description="部门ID筛选")
    status: Optional[str] = Field(None, description="状态筛选")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 20,
                "username": "admin",
                "dept_id": 1,
                "status": "1"
            }
        }


class UserCreateRequest(BaseModel):
    """
    创建用户请求DTO
    """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    email: Optional[str] = Field(None, max_length=128, description="邮箱")
    mobile: Optional[str] = Field(None, max_length=20, description="手机号")
    dept_id: Optional[int] = Field(None, description="部门ID")
    ssex: Optional[str] = Field(None, pattern="^[012]$", description="性别：0男 1女 2保密")
    avatar: Optional[str] = Field(None, max_length=100, description="头像")
    description: Optional[str] = Field(None, max_length=100, description="描述")

    @validator('ssex')
    def validate_ssex(cls, v):
        if v is not None and v not in ['0', '1', '2']:
            raise ValueError('性别必须是 0(男)、1(女) 或 2(保密)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "testuser",
                "password": "123456",
                "email": "test@example.com",
                "mobile": "13800138000",
                "dept_id": 1,
                "ssex": "0",
                "avatar": "default.jpg",
                "description": "测试用户"
            }
        }


class UserUpdateRequest(BaseModel):
    """
    更新用户请求DTO
    """
    user_id: int = Field(..., description="用户ID")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, max_length=128, description="邮箱")
    mobile: Optional[str] = Field(None, max_length=20, description="手机号")
    dept_id: Optional[int] = Field(None, description="部门ID")
    ssex: Optional[str] = Field(None, pattern="^[012]$", description="性别：0男 1女 2保密")
    avatar: Optional[str] = Field(None, max_length=100, description="头像")
    description: Optional[str] = Field(None, max_length=100, description="描述")

    @validator('ssex')
    def validate_ssex(cls, v):
        if v is not None and v not in ['0', '1', '2']:
            raise ValueError('性别必须是 0(男)、1(女) 或 2(保密)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "mobile": "13800138000",
                "dept_id": 1,
                "ssex": "0",
                "avatar": "default.jpg",
                "description": "测试用户"
            }
        }


class UserDeleteRequest(BaseModel):
    """
    删除用户请求DTO
    """
    user_id: int = Field(..., description="用户ID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1
            }
        }
    email: Optional[str] = Field(None, max_length=128, description="邮箱")
    mobile: Optional[str] = Field(None, max_length=20, description="手机号")
    ssex: Optional[str] = Field(None, pattern="^[012]$", description="性别：0男 1女 2保密")
    avatar: Optional[str] = Field(None, max_length=100, description="头像")
    description: Optional[str] = Field(None, max_length=100, description="描述")

    @validator('ssex')
    def validate_ssex(cls, v):
        if v is not None and v not in ['0', '1', '2']:
            raise ValueError('性别必须是 0(男)、1(女) 或 2(保密)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "mobile": "13900139000",
                "ssex": "1",
                "avatar": "new_avatar.jpg",
                "description": "更新后的描述"
            }
        }


class PasswordChangeRequest(BaseModel):
    """
    修改密码请求DTO
    """
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "123456",
                "new_password": "newpassword123"
            }
        }


class UserResponse(BaseModel):
    """
    用户响应DTO
    """
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    mobile: Optional[str] = Field(None, description="手机号")
    dept_id: Optional[int] = Field(None, description="部门ID")
    status: str = Field(..., description="状态：0锁定 1有效")
    ssex: Optional[str] = Field(None, description="性别：0男 1女 2保密")
    avatar: Optional[str] = Field(None, description="头像")
    description: Optional[str] = Field(None, description="描述")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    modify_time: Optional[datetime] = Field(None, description="修改时间")
    last_login_time: Optional[datetime] = Field(None, description="最后登录时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "mobile": "13800138000",
                "dept_id": 1,
                "status": "1",
                "ssex": "0",
                "avatar": "default.jpg",
                "description": "测试用户",
                "create_time": "2025-01-01T00:00:00",
                "modify_time": "2025-01-01T00:00:00",
                "last_login_time": "2025-01-01T00:00:00"
            }
        }


class UserListResponse(BaseModel):
    """
    用户列表响应DTO
    """
    users: List[UserResponse] = Field(..., description="用户列表")

    class Config:
        json_schema_extra = {
            "example": {
                "users": [
                    {
                        "user_id": 1,
                        "username": "testuser",
                        "email": "test@example.com",
                        "mobile": "13800138000",
                        "dept_id": 1,
                        "status": "1",
                        "ssex": "0",
                        "avatar": "default.jpg",
                        "description": "测试用户",
                        "create_time": "2025-01-01T00:00:00",
                        "modify_time": "2025-01-01T00:00:00",
                        "last_login_time": "2025-01-01T00:00:00"
                    }
                ]
            }
        }


class UserRoleAssignRequest(BaseModel):
    """
    用户角色分配请求DTO
    """
    user_id: int = Field(..., description="用户ID")
    role_ids: List[int] = Field(..., description="角色ID列表")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "role_ids": [1, 2, 3]
            }
        }


class UserRoleResponse(BaseModel):
    """
    用户角色响应DTO
    """
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    roles: List[dict] = Field(..., description="角色列表")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "testuser",
                "roles": [
                    {
                        "role_id": 1,
                        "role_name": "管理员",
                        "remark": "系统管理员"
                    }
                ]
            }
        }


class LoginRequest(BaseModel):
    """
    登录请求DTO
    """
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
    """
    登录响应DTO
    """
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user_info: UserResponse = Field(..., description="用户信息")
    permissions: List[str] = Field(..., description="用户权限列表")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_info": {
                    "user_id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "status": "1"
                },
                "permissions": ["user:view", "user:add", "user:update", "user:delete"]
            }
        }
