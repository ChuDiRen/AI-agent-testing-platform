"""
用户 Schema 模型
用于请求和响应验证
"""
from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., description="用户名")


class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=6, description="密码")


class UserUpdate(BaseModel):
    """更新用户"""
    password: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    username: str
    create_time: str
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., min_length=6, description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    code: int
    token: str
    refreshToken: Optional[str] = None
