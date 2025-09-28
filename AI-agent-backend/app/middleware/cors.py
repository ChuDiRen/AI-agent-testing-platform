# Copyright (c) 2025 左岚. All rights reserved.
"""
CORS中间件配置
处理跨域资源共享
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


def setup_cors(app: FastAPI) -> None:
    """
    设置CORS中间件
    
    Args:
        app: FastAPI应用实例
    """
    # 生产环境安全检查
    if settings.is_production and "*" in settings.ALLOWED_ORIGINS:
        logger.warning("生产环境不建议使用通配符CORS配置")
        # 生产环境默认安全配置
        allowed_origins = ["https://yourdomain.com"]  # 替换为实际域名
        allow_credentials = True
    else:
        allowed_origins = settings.ALLOWED_ORIGINS
        allow_credentials = "*" not in settings.ALLOWED_ORIGINS  # 通配符时不允许凭据
    
    # 安全的headers配置
    safe_headers = [
        "Content-Type",
        "Authorization", 
        "X-Requested-With",
        "Accept",
        "Origin",
        "Cache-Control",
        "X-File-Name"
    ]
    
    # 如果配置了通配符，使用安全的headers列表
    allowed_headers = safe_headers if "*" in settings.ALLOWED_HEADERS else settings.ALLOWED_HEADERS
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=allowed_headers,
        expose_headers=["X-Total-Count", "X-Page-Count", "X-Request-ID"],  # 暴露有用的响应头
        max_age=3600,  # 预检请求缓存时间
    )
    
    logger.info(f"CORS middleware configured - Origins: {allowed_origins}, Credentials: {allow_credentials}")


# 导出CORS设置函数
__all__ = ["setup_cors"]
