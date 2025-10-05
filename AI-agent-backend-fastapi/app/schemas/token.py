"""Token 相关的 Pydantic 模式"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Token 响应模型"""
    access_token: str  # 访问令牌
    refresh_token: str  # 刷新令牌（必填）
    token_type: str = "bearer"  # 令牌类型


class TokenData(BaseModel):
    """Token 数据模型"""
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """刷新Token请求模型"""
    refresh_token: str

