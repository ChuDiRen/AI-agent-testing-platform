"""全局异常处理中间件"""
import traceback
import logging
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.core.exceptions import BaseAPIException

# 配置日志
logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理器
    
    统一处理所有未捕获的异常,返回友好的错误信息
    """
    # 获取请求信息
    request_info = {
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", ""),
    }
    
    # 自定义API异常
    if isinstance(exc, BaseAPIException):
        logger.warning(
            f"API异常: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "request": request_info,
                "exception_type": type(exc).__name__
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "data": None,
                "error_type": type(exc).__name__
            }
        )
    
    # FastAPI 请求验证错误
    if isinstance(exc, RequestValidationError):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"请求验证失败: {errors}",
            extra={"request": request_info}
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "请求参数验证失败",
                "data": None,
                "errors": errors
            }
        )
    
    # Pydantic 验证错误
    if isinstance(exc, ValidationError):
        logger.warning(
            f"数据验证失败: {exc.errors()}",
            extra={"request": request_info}
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "数据验证失败",
                "data": None,
                "errors": exc.errors()
            }
        )
    
    # 数据库错误
    if isinstance(exc, SQLAlchemyError):
        logger.error(
            f"数据库错误: {str(exc)}",
            extra={
                "request": request_info,
                "traceback": traceback.format_exc()
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "数据库操作失败",
                "data": None,
                "error_type": "DatabaseError"
            }
        )
    
    # 未知异常
    logger.error(
        f"未处理的异常: {str(exc)}",
        extra={
            "request": request_info,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
    )
    
    # 开发环境返回详细错误信息
    from app.core.config import settings
    error_detail = str(exc) if settings.DEBUG else "服务器内部错误"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": error_detail,
            "data": None,
            "error_type": type(exc).__name__
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """验证异常处理器"""
    return await global_exception_handler(request, exc)


async def http_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """HTTP异常处理器"""
    return await global_exception_handler(request, exc)


