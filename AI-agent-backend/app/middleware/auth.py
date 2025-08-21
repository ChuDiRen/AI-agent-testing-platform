"""
认证中间件
处理JWT令牌验证和用户认证
"""

from typing import Optional

from app.repository.user_repository import UserRepository
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.core.security import verify_token
from app.db.session import get_db
from app.utils.exceptions import AuthenticationException, InvalidTokenException

logger = get_logger(__name__)

# HTTP Bearer认证方案
security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """
    认证中间件类
    """
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
    
    async def __call__(self, request: Request, call_next):
        """
        中间件处理函数
        
        Args:
            request: HTTP请求
            call_next: 下一个处理函数
            
        Returns:
            HTTP响应
        """
        # 获取Authorization头
        authorization = request.headers.get("Authorization")
        
        if authorization:
            try:
                # 解析Bearer令牌
                scheme, token = authorization.split(" ", 1)
                if scheme.lower() == "bearer":
                    # 验证令牌
                    payload = verify_token(token)
                    if payload:
                        # 将用户信息添加到请求状态
                        request.state.user_id = payload.get("sub")
                        request.state.token_payload = payload
                    else:
                        request.state.user_id = None
                        request.state.token_payload = None
                else:
                    request.state.user_id = None
                    request.state.token_payload = None
            except Exception as e:
                logger.warning(f"Token parsing error: {str(e)}")
                request.state.user_id = None
                request.state.token_payload = None
        else:
            request.state.user_id = None
            request.state.token_payload = None
        
        # 继续处理请求
        response = await call_next(request)
        return response


def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[int]:
    """
    获取当前用户ID（可选）
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        用户ID或None
    """
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        if payload:
            return payload.get("sub")
        return None
    except Exception as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return None


def require_authentication(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    要求用户认证（必需）
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        用户ID
        
    Raises:
        AuthenticationException: 认证失败异常
    """
    if not credentials:
        raise AuthenticationException("Authentication required")
    
    try:
        payload = verify_token(credentials.credentials)
        if not payload:
            raise InvalidTokenException()
        
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenException()
        
        return user_id
        
    except AuthenticationException:
        raise
    except Exception as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise AuthenticationException("Invalid authentication credentials")


def get_current_user(
    user_id: int = Depends(require_authentication),
    db: Session = Depends(get_db)
):
    """
    获取当前用户对象
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        
    Returns:
        用户对象
        
    Raises:
        AuthenticationException: 用户不存在异常
    """
    try:
        repository = UserRepository(db)
        user = repository.get_by_id(user_id)
        
        if not user:
            raise AuthenticationException("User not found")
        
        if not user.can_login():
            raise AuthenticationException("User account is disabled")
        
        return user
        
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise AuthenticationException("Failed to get user information")


def require_admin(
    current_user = Depends(get_current_user)
):
    """
    要求管理员权限
    
    Args:
        current_user: 当前用户
        
    Returns:
        用户对象
        
    Raises:
        HTTPException: 权限不足异常
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user


def require_superuser(
    current_user = Depends(get_current_user)
):
    """
    要求超级用户权限
    
    Args:
        current_user: 当前用户
        
    Returns:
        用户对象
        
    Raises:
        HTTPException: 权限不足异常
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required"
        )
    
    return current_user


def require_verified_user(
    current_user = Depends(get_current_user)
):
    """
    要求已验证用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        用户对象
        
    Raises:
        HTTPException: 用户未验证异常
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return current_user


def optional_authentication(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    """
    可选认证（不强制要求登录）
    
    Args:
        credentials: HTTP认证凭据
        db: 数据库会话
        
    Returns:
        用户对象或None
    """
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        repository = UserRepository(db)
        user = repository.get_by_id(user_id)
        
        if user and user.can_login():
            return user
        
        return None
        
    except Exception as e:
        logger.debug(f"Optional authentication failed: {str(e)}")
        return None


# 创建认证中间件实例
auth_middleware = AuthMiddleware()

# 导出认证相关函数和中间件
__all__ = [
    "AuthMiddleware",
    "auth_middleware",
    "get_current_user_id",
    "require_authentication",
    "get_current_user",
    "require_admin",
    "require_superuser",
    "require_verified_user",
    "optional_authentication",
]
