"""自定义异常类"""
from typing import Optional, Any


class APIException(Exception):
    """API异常基类"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "API_ERROR"
        self.details = details
        super().__init__(self.message)


class AuthenticationError(APIException):
    """认证错误"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(APIException):
    """授权错误"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundError(APIException):
    """资源不存在"""
    
    def __init__(self, resource: str = "资源"):
        super().__init__(
            message=f"{resource}不存在",
            status_code=404,
            error_code="NOT_FOUND"
        )


class ValidationError(APIException):
    """验证错误"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"field": field} if field else None
        )


class BusinessError(APIException):
    """业务逻辑错误"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BUSINESS_ERROR"
        )

