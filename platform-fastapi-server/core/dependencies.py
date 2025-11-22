"""依赖注入函数"""
from typing import Optional

from config.dev_settings import settings
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .JwtUtil import JwtUtils
from .MinioUtils import MinioUtils

security = HTTPBearer(auto_error=False)

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    l_token: Optional[str] = Cookie(None, alias="l-token")
) -> dict: # JWT认证依赖
    token = None
    
    # 1. 尝试从 Authorization Header 获取
    if credentials:
        token = credentials.credentials
    
    # 2. 尝试从 Cookie 获取
    if not token and l_token:
        token = l_token
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = JwtUtils.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def check_permission(permission: str): # 权限检查依赖
    """
    权限检查依赖生成器
    :param permission: 需要的权限标识，如 'user:add'
    :return: 依赖函数
    """
    def _check_permission(user: dict = Depends(get_current_user)):
        # 超级管理员直接放行
        if user.get("username") == "admin":
            return True
            
        # 获取用户权限列表
        permissions = user.get("permissions", [])
        
        # 检查权限
        if permission not in permissions:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要权限: {permission}"
            )
        return True
    return _check_permission

def get_minio_client() -> MinioUtils: # 获取MinIO客户端
    return MinioUtils(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE
    )

