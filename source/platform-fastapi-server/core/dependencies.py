"""依赖注入函数"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Generator
from core.database import get_session
from core.JwtUtil import JwtUtils
from core.MinioUtils import MinioUtils
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

def get_minio_client() -> MinioUtils: # 获取MinIO客户端
    return MinioUtils(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE
    )

