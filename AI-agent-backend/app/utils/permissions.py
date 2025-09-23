"""
权限验证装饰器和工具
"""

import functools
from typing import List, Optional, Callable, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.session import get_db
from app.entity.user import User
from app.repository.user_repository import UserRepository
from app.core.logger import get_logger

logger = get_logger(__name__)

# HTTP Bearer 认证
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前用户
    """
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌"
            )
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(int(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户账号已被禁用"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证验证失败"
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    """
    return current_user


def require_permissions(permissions: List[str]):
    """
    权限验证装饰器
    
    Args:
        permissions: 需要的权限列表
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_user
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要用户认证"
                )
            
            # 检查权限
            if not has_permissions(current_user, permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_roles(roles: List[str]):
    """
    角色验证装饰器
    
    Args:
        roles: 需要的角色列表
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要用户认证"
                )
            
            # 检查角色
            if not has_roles(current_user, roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="角色权限不足"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_admin():
    """
    管理员权限验证装饰器
    """
    return require_roles(['admin', 'super_admin'])


def require_owner_or_admin(resource_user_id_field: str = 'user_id'):
    """
    资源所有者或管理员权限验证装饰器
    
    Args:
        resource_user_id_field: 资源中用户ID字段名
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要用户认证"
                )
            
            # 管理员可以访问所有资源
            if has_roles(current_user, ['admin', 'super_admin']):
                return await func(*args, **kwargs)
            
            # 检查是否为资源所有者
            resource_user_id = kwargs.get(resource_user_id_field)
            if resource_user_id and resource_user_id == current_user.id:
                return await func(*args, **kwargs)
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能访问自己的资源"
            )
        
        return wrapper
    return decorator


def has_permissions(user: User, permissions: List[str]) -> bool:
    """
    检查用户是否具有指定权限
    
    Args:
        user: 用户对象
        permissions: 权限列表
    
    Returns:
        bool: 是否具有权限
    """
    if not user or not user.is_active:
        return False
    
    # 超级管理员拥有所有权限
    if has_roles(user, ['super_admin']):
        return True
    
    # 检查用户权限
    user_permissions = get_user_permissions(user)
    return all(perm in user_permissions for perm in permissions)


def has_roles(user: User, roles: List[str]) -> bool:
    """
    检查用户是否具有指定角色
    
    Args:
        user: 用户对象
        roles: 角色列表
    
    Returns:
        bool: 是否具有角色
    """
    if not user or not user.is_active:
        return False
    
    user_roles = get_user_roles(user)
    return any(role in user_roles for role in roles)


def get_user_roles(user: User) -> List[str]:
    """
    获取用户角色列表
    
    Args:
        user: 用户对象
    
    Returns:
        List[str]: 角色列表
    """
    if not user or not hasattr(user, 'user_roles'):
        return []
    
    return [ur.role.role_code for ur in user.user_roles if ur.role and ur.role.is_active]


def get_user_permissions(user: User) -> List[str]:
    """
    获取用户权限列表
    
    Args:
        user: 用户对象
    
    Returns:
        List[str]: 权限列表
    """
    if not user:
        return []
    
    permissions = set()
    
    # 通过角色获取权限
    for user_role in getattr(user, 'user_roles', []):
        if user_role.role and user_role.role.is_active:
            for role_menu in getattr(user_role.role, 'role_menus', []):
                if role_menu.menu and role_menu.menu.permission_code:
                    permissions.add(role_menu.menu.permission_code)
    
    return list(permissions)


def check_api_access(user: User, api_path: str, method: str) -> bool:
    """
    检查用户是否可以访问指定API
    
    Args:
        user: 用户对象
        api_path: API路径
        method: HTTP方法
    
    Returns:
        bool: 是否可以访问
    """
    if not user or not user.is_active:
        return False
    
    # 超级管理员可以访问所有API
    if has_roles(user, ['super_admin']):
        return True
    
    # 这里可以实现更复杂的API权限控制逻辑
    # 例如：基于角色、权限、资源等进行判断
    
    return True  # 临时返回True，实际项目中需要实现具体逻辑


class PermissionChecker:
    """
    权限检查器类
    """
    
    def __init__(self, user: User):
        self.user = user
        self._permissions = None
        self._roles = None
    
    @property
    def permissions(self) -> List[str]:
        """获取用户权限"""
        if self._permissions is None:
            self._permissions = get_user_permissions(self.user)
        return self._permissions
    
    @property
    def roles(self) -> List[str]:
        """获取用户角色"""
        if self._roles is None:
            self._roles = get_user_roles(self.user)
        return self._roles
    
    def has_permission(self, permission: str) -> bool:
        """检查是否有指定权限"""
        return has_permissions(self.user, [permission])
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        """检查是否有任意一个权限"""
        return any(perm in self.permissions for perm in permissions)
    
    def has_all_permissions(self, permissions: List[str]) -> bool:
        """检查是否有所有权限"""
        return has_permissions(self.user, permissions)
    
    def has_role(self, role: str) -> bool:
        """检查是否有指定角色"""
        return has_roles(self.user, [role])
    
    def has_any_role(self, roles: List[str]) -> bool:
        """检查是否有任意一个角色"""
        return has_roles(self.user, roles)
    
    def is_admin(self) -> bool:
        """检查是否为管理员"""
        return self.has_any_role(['admin', 'super_admin'])
    
    def is_super_admin(self) -> bool:
        """检查是否为超级管理员"""
        return self.has_role('super_admin')
    
    def can_access_api(self, api_path: str, method: str = 'GET') -> bool:
        """检查是否可以访问指定API"""
        return check_api_access(self.user, api_path, method)


# 常用权限常量
class Permissions:
    """权限常量"""
    
    # 用户管理
    USER_VIEW = 'user:view'
    USER_CREATE = 'user:create'
    USER_UPDATE = 'user:update'
    USER_DELETE = 'user:delete'
    
    # 角色管理
    ROLE_VIEW = 'role:view'
    ROLE_CREATE = 'role:create'
    ROLE_UPDATE = 'role:update'
    ROLE_DELETE = 'role:delete'
    
    # AI代理管理
    AGENT_VIEW = 'agent:view'
    AGENT_CREATE = 'agent:create'
    AGENT_UPDATE = 'agent:update'
    AGENT_DELETE = 'agent:delete'
    
    # 测试用例管理
    TEST_CASE_VIEW = 'test_case:view'
    TEST_CASE_CREATE = 'test_case:create'
    TEST_CASE_UPDATE = 'test_case:update'
    TEST_CASE_DELETE = 'test_case:delete'
    TEST_CASE_RUN = 'test_case:run'
    
    # 系统管理
    SYSTEM_VIEW = 'system:view'
    SYSTEM_MANAGE = 'system:manage'
    
    # 日志管理
    LOG_VIEW = 'log:view'
    LOG_DELETE = 'log:delete'


# 常用角色常量
class Roles:
    """角色常量"""
    
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'


# 导出
__all__ = [
    'get_current_user',
    'get_current_active_user',
    'require_permissions',
    'require_roles',
    'require_admin',
    'require_owner_or_admin',
    'has_permissions',
    'has_roles',
    'get_user_roles',
    'get_user_permissions',
    'check_api_access',
    'PermissionChecker',
    'Permissions',
    'Roles'
]
