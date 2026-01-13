"""
自定义异常类模块
"""
from fastapi import HTTPException, status


class UnauthorizedException(HTTPException):
    """未授权异常"""
    def __init__(self, detail: str = "未登录或 Token 失效"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(HTTPException):
    """禁止访问异常"""
    def __init__(self, detail: str = "权限不足"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(HTTPException):
    """资源未找到异常"""
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(HTTPException):
    """请求参数错误异常"""
    def __init__(self, detail: str = "请求参数错误"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InternalServerException(HTTPException):
    """服务器内部错误异常"""
    def __init__(self, detail: str = "服务器内部错误"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
