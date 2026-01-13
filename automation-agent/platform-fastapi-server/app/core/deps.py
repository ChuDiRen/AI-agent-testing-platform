"""
依赖注入模块
提供数据库会话、当前用户等依赖
"""
from typing import Optional
from fastapi import Request, HTTPException, status
from app.db.session import get_db
from app.core.security import verify_token
from app.core.exceptions import UnauthorizedException


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
