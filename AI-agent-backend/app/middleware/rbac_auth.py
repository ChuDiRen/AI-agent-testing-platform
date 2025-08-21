# Copyright (c) 2025 左岚. All rights reserved.
"""
RBAC权限验证中间件
实现基于角色的访问控制
"""

from typing import List

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.core.security import verify_token
from app.db.session import get_db
from app.service.rbac_user_service import RBACUserService

logger = get_logger(__name__)

# HTTP Bearer认证方案
security = HTTPBearer()


class RBACAuth:
    """
    RBAC权限验证类
    提供用户认证和权限验证功能
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        """
        获取当前用户
        
        Args:
            credentials: HTTP认证凭据
            db: 数据库会话
            
        Returns:
            当前用户对象
            
        Raises:
            HTTPException: 认证失败
        """
        try:
            # 验证令牌
            payload = verify_token(credentials.credentials)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的访问令牌",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 获取用户ID
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="令牌中缺少用户信息",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 获取用户信息
            user_service = RBACUserService(db)
            user = user_service.get_user_by_id(int(user_id))
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if not user.is_active():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户已被锁定",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            self.logger.debug(f"User authenticated: {user.USERNAME}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证失败",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def require_permission(self, permission: str):
        """
        权限验证装饰器
        
        Args:
            permission: 需要的权限标识
            
        Returns:
            依赖函数
        """
        async def permission_checker(
            current_user=Depends(self.get_current_user),
            db: Session = Depends(get_db)
        ):
            """
            检查用户是否有指定权限
            
            Args:
                current_user: 当前用户
                db: 数据库会话
                
            Returns:
                当前用户对象
                
            Raises:
                HTTPException: 权限不足
            """
            try:
                user_service = RBACUserService(db)
                has_permission = user_service.has_permission(current_user.USER_ID, permission)
                
                if not has_permission:
                    self.logger.warning(f"Permission denied for user {current_user.USERNAME}: {permission}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"权限不足，需要权限: {permission}"
                    )
                
                self.logger.debug(f"Permission granted for user {current_user.USERNAME}: {permission}")
                return current_user
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Permission check error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="权限验证失败"
                )
        
        return permission_checker

    def require_permissions(self, permissions: List[str], require_all: bool = True):
        """
        多权限验证装饰器
        
        Args:
            permissions: 需要的权限标识列表
            require_all: 是否需要所有权限（True）还是任一权限（False）
            
        Returns:
            依赖函数
        """
        async def permissions_checker(
            current_user=Depends(self.get_current_user),
            db: Session = Depends(get_db)
        ):
            """
            检查用户是否有指定权限
            
            Args:
                current_user: 当前用户
                db: 数据库会话
                
            Returns:
                当前用户对象
                
            Raises:
                HTTPException: 权限不足
            """
            try:
                user_service = RBACUserService(db)
                user_permissions = user_service.get_user_permissions(current_user.USER_ID)
                
                if require_all:
                    # 需要所有权限
                    missing_permissions = [p for p in permissions if p not in user_permissions]
                    if missing_permissions:
                        self.logger.warning(
                            f"Permission denied for user {current_user.USERNAME}: "
                            f"missing {missing_permissions}"
                        )
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"权限不足，缺少权限: {', '.join(missing_permissions)}"
                        )
                else:
                    # 需要任一权限
                    has_any_permission = any(p in user_permissions for p in permissions)
                    if not has_any_permission:
                        self.logger.warning(
                            f"Permission denied for user {current_user.USERNAME}: "
                            f"none of {permissions}"
                        )
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"权限不足，需要以下任一权限: {', '.join(permissions)}"
                        )
                
                self.logger.debug(f"Permissions granted for user {current_user.USERNAME}: {permissions}")
                return current_user
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Permissions check error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="权限验证失败"
                )
        
        return permissions_checker

    def require_role(self, role_name: str):
        """
        角色验证装饰器
        
        Args:
            role_name: 需要的角色名称
            
        Returns:
            依赖函数
        """
        async def role_checker(
            current_user=Depends(self.get_current_user),
            db: Session = Depends(get_db)
        ):
            """
            检查用户是否有指定角色
            
            Args:
                current_user: 当前用户
                db: 数据库会话
                
            Returns:
                当前用户对象
                
            Raises:
                HTTPException: 角色不匹配
            """
            try:
                user_service = RBACUserService(db)
                user_roles = user_service.get_user_roles(current_user.USER_ID)
                
                has_role = any(role.ROLE_NAME == role_name for role in user_roles)
                
                if not has_role:
                    self.logger.warning(f"Role denied for user {current_user.USERNAME}: {role_name}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"角色不匹配，需要角色: {role_name}"
                    )
                
                self.logger.debug(f"Role granted for user {current_user.USERNAME}: {role_name}")
                return current_user
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Role check error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="角色验证失败"
                )
        
        return role_checker


# 创建全局RBAC认证实例
rbac_auth = RBACAuth()

# 常用的依赖函数
get_current_user = rbac_auth.get_current_user

# 常用权限验证函数
def require_user_view():
    """需要用户查看权限"""
    return rbac_auth.require_permission("user:view")

def require_user_add():
    """需要用户新增权限"""
    return rbac_auth.require_permission("user:add")

def require_user_update():
    """需要用户修改权限"""
    return rbac_auth.require_permission("user:update")

def require_user_delete():
    """需要用户删除权限"""
    return rbac_auth.require_permission("user:delete")

def require_admin_role():
    """需要管理员角色"""
    return rbac_auth.require_role("管理员")
