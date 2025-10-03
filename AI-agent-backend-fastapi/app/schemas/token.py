"""Token 相关的 Pydantic 模式"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Token 响应模型"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 数据模型"""
    username: Optional[str] = None

