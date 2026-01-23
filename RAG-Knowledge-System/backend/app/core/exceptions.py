"""
自定义异常类
"""
from typing import Optional
from core.resp_model import ErrorResponseModel


class PlatformBaseException(Exception):
    """平台基础异常类"""

    def __init__(self, message: str, code: int = 500, errors: list = None):
        self.message = message
        self.code = code
        self.errors = errors or []
        super().__init__(self.message)

    def to_response(self) -> ErrorResponseModel:
        """转换为响应模型"""
        return ErrorResponseModel(
            code=self.code,
            message=self.message,
            errors=self.errors
        )


class BusinessException(PlatformBaseException):
    """业务异常（可恢复）"""

    def __init__(self, message: str, code: int = 400, errors: list = None):
        super().__init__(message, code, errors)


class ValidationException(BusinessException):
    """数据验证异常"""

    def __init__(self, message: str, field: Optional[str] = None):
        errors = [{"field": field, "message": message}] if field else []
        super().__init__(message, code=400, errors=errors)


class ResourceNotFoundException(BusinessException):
    """资源不存在异常"""

    def __init__(self, message: str):
        super().__init__(message, code=404)


class PermissionDeniedException(BusinessException):
    """权限拒绝异常"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(message, code=403)


class UnauthorizedException(BusinessException):
    """未认证异常"""

    def __init__(self, message: str = "未认证，请先登录"):
        super().__init__(message, code=401)


class DuplicateResourceException(BusinessException):
    """资源重复异常"""

    def __init__(self, message: str):
        super().__init__(message, code=409)


class TechnicalException(PlatformBaseException):
    """技术异常（系统级，不可恢复）"""

    def __init__(self, message: str, code: int = 500):
        super().__init__(message, code)


class DatabaseException(TechnicalException):
    """数据库异常"""

    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message, code=500)


class ExternalServiceException(TechnicalException):
    """外部服务异常"""

    def __init__(self, message: str, service_name: Optional[str] = None):
        msg = f"{service_name} 服务异常: {message}" if service_name else message
        super().__init__(msg, code=503)


class ConfigurationException(TechnicalException):
    """配置异常"""

    def __init__(self, message: str = "配置错误"):
        super().__init__(message, code=500)


class QueueException(TechnicalException):
    """消息队列异常"""

    def __init__(self, message: str = "消息队列异常"):
        super().__init__(message, code=500)
