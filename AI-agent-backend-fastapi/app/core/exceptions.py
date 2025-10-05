"""全局异常定义"""
from typing import Any, Optional
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """API异常基类"""
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = None,
        headers: Optional[dict] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(BaseAPIException):
    """资源未找到异常"""
    
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(BaseAPIException):
    """错误请求异常"""
    
    def __init__(self, detail: str = "请求参数错误"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(BaseAPIException):
    """未授权异常"""
    
    def __init__(self, detail: str = "未授权访问"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(BaseAPIException):
    """禁止访问异常"""
    
    def __init__(self, detail: str = "没有权限访问"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(BaseAPIException):
    """冲突异常"""
    
    def __init__(self, detail: str = "资源冲突"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationException(BaseAPIException):
    """验证异常"""
    
    def __init__(self, detail: str = "数据验证失败"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class RateLimitException(BaseAPIException):
    """限流异常"""
    
    def __init__(self, detail: str = "请求过于频繁,请稍后再试"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class DatabaseException(BaseAPIException):
    """数据库异常"""
    
    def __init__(self, detail: str = "数据库操作失败"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class AIServiceException(BaseAPIException):
    """AI服务异常"""
    
    def __init__(self, detail: str = "AI服务调用失败"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class FileUploadException(BaseAPIException):
    """文件上传异常"""
    
    def __init__(self, detail: str = "文件上传失败"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
