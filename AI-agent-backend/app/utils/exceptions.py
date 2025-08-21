"""
自定义异常类
定义应用中使用的各种异常
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """
    API异常基类
    """
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        error_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.error_data = error_data or {}


class ValidationException(BaseAPIException):
    """
    数据验证异常
    """
    def __init__(
        self,
        detail: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
        error_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code,
            error_data=error_data
        )


class BusinessException(BaseAPIException):
    """
    业务逻辑异常
    """
    def __init__(
        self,
        detail: str = "Business logic error",
        error_code: str = "BUSINESS_ERROR",
        error_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
            error_data=error_data
        )


class AuthenticationException(BaseAPIException):
    """
    认证异常
    """
    def __init__(
        self,
        detail: str = "Authentication failed",
        error_code: str = "AUTHENTICATION_ERROR",
        error_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            error_data=error_data,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationException(BaseAPIException):
    """
    授权异常
    """
    def __init__(
        self,
        detail: str = "Access denied",
        error_code: str = "AUTHORIZATION_ERROR",
        error_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
            error_data=error_data
        )


class NotFoundException(BaseAPIException):
    """
    资源不存在异常
    """
    def __init__(
        self,
        detail: str = "Resource not found",
        error_code: str = "NOT_FOUND_ERROR",
        error_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
            error_data=error_data
        )


class ConflictException(BaseAPIException):
    """
    资源冲突异常
    """
    def __init__(
        self,
        detail: str = "Resource conflict",
        error_code: str = "CONFLICT_ERROR",
        error_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
            error_data=error_data
        )


class RateLimitException(BaseAPIException):
    """
    速率限制异常
    """
    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        error_code: str = "RATE_LIMIT_ERROR",
        error_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code=error_code,
            error_data=error_data
        )


class InternalServerException(BaseAPIException):
    """
    内部服务器异常
    """
    def __init__(
        self,
        detail: str = "Internal server error",
        error_code: str = "INTERNAL_SERVER_ERROR",
        error_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code,
            error_data=error_data
        )


class ServiceUnavailableException(BaseAPIException):
    """
    服务不可用异常
    """
    def __init__(
        self,
        detail: str = "Service unavailable",
        error_code: str = "SERVICE_UNAVAILABLE_ERROR",
        error_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code=error_code,
            error_data=error_data
        )


# 特定业务异常
class UserNotFoundException(NotFoundException):
    """用户不存在异常"""
    def __init__(self, user_id: Optional[int] = None, username: Optional[str] = None):
        if user_id:
            detail = f"User with id {user_id} not found"
        elif username:
            detail = f"User with username '{username}' not found"
        else:
            detail = "User not found"
        
        super().__init__(
            detail=detail,
            error_code="USER_NOT_FOUND",
            error_data={"user_id": user_id, "username": username}
        )


class UserAlreadyExistsException(ConflictException):
    """用户已存在异常"""
    def __init__(self, field: str, value: str):
        super().__init__(
            detail=f"User with {field} '{value}' already exists",
            error_code="USER_ALREADY_EXISTS",
            error_data={"field": field, "value": value}
        )


class InvalidCredentialsException(AuthenticationException):
    """无效凭据异常"""
    def __init__(self):
        super().__init__(
            detail="Invalid username or password",
            error_code="INVALID_CREDENTIALS"
        )


class TokenExpiredException(AuthenticationException):
    """令牌过期异常"""
    def __init__(self):
        super().__init__(
            detail="Token has expired",
            error_code="TOKEN_EXPIRED"
        )


class InvalidTokenException(AuthenticationException):
    """无效令牌异常"""
    def __init__(self):
        super().__init__(
            detail="Invalid token",
            error_code="INVALID_TOKEN"
        )


class IndicatorParameterNotFoundException(NotFoundException):
    """指标参数不存在异常"""
    def __init__(self, parameter_id: Optional[int] = None, 
                 indicator_name: Optional[str] = None, 
                 parameter_name: Optional[str] = None):
        if parameter_id:
            detail = f"Indicator parameter with id {parameter_id} not found"
        elif indicator_name and parameter_name:
            detail = f"Parameter '{parameter_name}' not found for indicator '{indicator_name}'"
        else:
            detail = "Indicator parameter not found"
        
        super().__init__(
            detail=detail,
            error_code="INDICATOR_PARAMETER_NOT_FOUND",
            error_data={
                "parameter_id": parameter_id,
                "indicator_name": indicator_name,
                "parameter_name": parameter_name
            }
        )


class IndicatorParameterValidationException(ValidationException):
    """指标参数验证异常"""
    def __init__(self, field: str, message: str):
        super().__init__(
            detail=f"Validation error for field '{field}': {message}",
            error_code="INDICATOR_PARAMETER_VALIDATION_ERROR",
            error_data={"field": field, "message": message}
        )


# 异常映射字典，用于统一处理
EXCEPTION_MAPPING = {
    "validation_error": ValidationException,
    "business_error": BusinessException,
    "authentication_error": AuthenticationException,
    "authorization_error": AuthorizationException,
    "not_found_error": NotFoundException,
    "conflict_error": ConflictException,
    "rate_limit_error": RateLimitException,
    "internal_server_error": InternalServerException,
    "service_unavailable_error": ServiceUnavailableException,
}


def create_exception(exception_type: str, detail: str, **kwargs) -> BaseAPIException:
    """
    创建异常实例
    
    Args:
        exception_type: 异常类型
        detail: 异常详情
        **kwargs: 其他参数
        
    Returns:
        异常实例
    """
    exception_class = EXCEPTION_MAPPING.get(exception_type, BusinessException)
    return exception_class(detail=detail, **kwargs)


# 导出所有异常类
__all__ = [
    "BaseAPIException",
    "ValidationException",
    "BusinessException",
    "AuthenticationException",
    "AuthorizationException",
    "NotFoundException",
    "ConflictException",
    "RateLimitException",
    "InternalServerException",
    "ServiceUnavailableException",
    "UserNotFoundException",
    "UserAlreadyExistsException",
    "InvalidCredentialsException",
    "TokenExpiredException",
    "InvalidTokenException",
    "IndicatorParameterNotFoundException",
    "IndicatorParameterValidationException",
    "create_exception",
]
