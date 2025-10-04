"""用户相关的 Pydantic 模式"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱地址")
    mobile: Optional[str] = Field(None, description="手机号")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, description="密码")
    dept_id: Optional[int] = Field(None, description="部门ID")
    ssex: Optional[str] = Field(None, description="性别 0男 1女 2保密")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应模型 - 对应t_user表结构"""
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    mobile: Optional[str] = Field(None, description="手机号")
    dept_id: Optional[int] = Field(None, description="部门ID")
    status: str = Field(..., description="状态 0锁定 1有效")
    ssex: Optional[str] = Field(None, description="性别 0男 1女 2保密")
    avatar: Optional[str] = Field(None, description="头像")
    description: Optional[str] = Field(None, description="描述")
    create_time: datetime = Field(..., description="创建时间")
    modify_time: Optional[datetime] = Field(None, description="修改时间")
    last_login_time: Optional[datetime] = Field(None, description="最近登录时间")

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[str] = None
    mobile: Optional[str] = None
    password: Optional[str] = None
    dept_id: Optional[int] = None
    ssex: Optional[str] = None
    avatar: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class PasswordChange(BaseModel):
    """修改密码模型"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('新密码长度至少6位')
        if len(v) > 20:
            raise ValueError('新密码长度最多20位')
        return v


class ProfileUpdate(BaseModel):
    """个人资料更新模型"""
    email: Optional[str] = Field(None, description="邮箱")
    mobile: Optional[str] = Field(None, description="手机号")
    description: Optional[str] = Field(None, max_length=200, description="个人简介")

