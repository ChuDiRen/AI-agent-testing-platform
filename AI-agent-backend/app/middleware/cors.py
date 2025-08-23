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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=False,  # 使用通配符时必须为False
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
        expose_headers=["X-Total-Count", "X-Page-Count"],
        max_age=3600,  # 预检请求缓存时间
    )
    
    logger.info(f"CORS middleware configured with origins: {settings.ALLOWED_ORIGINS}")


# 导出CORS设置函数
__all__ = ["setup_cors"]
