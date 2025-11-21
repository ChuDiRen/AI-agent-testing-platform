"""依赖注入函数"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Generator
from .database import get_session
from .JwtUtil import JwtUtils
from .MinioUtils import MinioUtils
from config.dev_settings import settings

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict: # JWT认证依赖
    token = credentials.credentials
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

