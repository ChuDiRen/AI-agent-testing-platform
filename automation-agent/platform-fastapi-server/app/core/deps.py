"""
依赖注入模块
提供数据库会话、当前用户等依赖
"""
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import verify_token
from app.core.exceptions import UnauthorizedException
from app.models.user import User


async def get_current_user(request: Request) -> Optional[dict]:
    """
    获取当前用户（从 JWT Token 中解析）
    
    Args:
        request: FastAPI 请求对象
    
    Returns:
        dict: 用户信息字典
        
    Raises:
        UnauthorizedException: 如果 Token 验证失败
    """
    # 白名单路径
    whitelist = [
        "/api/v1/login",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/health",
        "/"
    ]
    
    if request.url.path in whitelist:
        return None
    
    # 获取 Token
    token = request.headers.get("token")
    if not token:
        raise UnauthorizedException("未登录")
    
    # 验证 Token
    payload = verify_token(token)
    if not payload:
        raise UnauthorizedException("Token 失效")
    
    # 保存到 request.state
    request.state.username = payload.get('username')
    request.state.payload = payload
    
    return payload


async def get_current_user_model(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前用户模型对象
    
    Args:
        request: FastAPI 请求对象
        db: 数据库会话
    
    Returns:
        User: 用户模型对象
        
    Raises:
        UnauthorizedException: 如果用户不存在或Token无效
    """
    # 获取token payload
    payload = await get_current_user(request)
    if not payload:
        raise UnauthorizedException("未登录")
    
    # 查询用户
    user_id = payload.get('user_id')
    if not user_id:
        raise UnauthorizedException("Token无效")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise UnauthorizedException("用户不存在")
    
    if not user.is_active:
        raise UnauthorizedException("用户已被禁用")
    
    return user
