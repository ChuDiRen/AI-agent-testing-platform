# Copyright (c) 2025 左岚. All rights reserved.
"""
RBAC权限验证中间件
实现细粒度权限控制、数据权限过滤和审计日志记录
"""

import json
import time
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from functools import wraps

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.logger import get_logger
from app.core.security import verify_token
from app.db.session import get_db
from app.service.rbac_user_service import RBACUserService
from app.service.audit_log_service import AuditLogService
from app.service.data_permission_service import DataPermissionService
from app.service.permission_cache_service import PermissionCacheService
from app.entity.audit_log import AuditLog
from app.entity.permission_cache import DataPermissionRule

logger = get_logger(__name__)
security = HTTPBearer()


class RBACAuth:
    """
    RBAC权限验证类
    提供用户认证、权限验证、数据权限过滤和审计日志记录功能
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        # 服务将在需要时延迟初始化，因为它们需要数据库会话
        self.permission_cache_service = None

    async def get_current_user_with_audit(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        """
        获取当前用户并记录审计日志
        
        Args:
            request: HTTP请求对象
            credentials: HTTP认证凭据
            db: 数据库会话
            
        Returns:
            当前用户对象
            
        Raises:
            HTTPException: 认证失败时抛出401错误
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # 验证token
            payload = verify_token(credentials.credentials)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的token",
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

            # 记录访问审计日志
            await self._log_user_access(request, user, db)
            
            return user

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"用户认证失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证失败",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        """
        获取当前用户（不记录审计日志）
        
        Args:
            credentials: HTTP认证凭据
            db: 数据库会话
            
        Returns:
            当前用户对象
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # 验证token
            payload = verify_token(credentials.credentials)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的token",
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
            
            return user

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"用户认证失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证失败",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def require_permission(self, permission: str) -> Callable:
        """
        权限验证装饰器
        
        Args:
            permission: 需要的权限标识
            
        Returns:
            装饰器函数
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 从kwargs中获取current_user和db
                current_user = kwargs.get('current_user')
                db = kwargs.get('db')
                
                if not current_user or not db:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="认证信息缺失"
                    )
                
                # 检查权限
                user_service = RBACUserService(db)
                user_permissions = user_service.get_user_permissions(current_user.user_id)
                
                if permission not in user_permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"权限不足，需要权限: {permission}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    def require_permission_with_audit(self, permission: str, resource_type: str) -> Callable:
        """
        带审计日志的权限验证装饰器
        
        Args:
            permission: 需要的权限标识
            resource_type: 资源类型
            
        Returns:
            装饰器函数
        """
        async def dependency(
            request: Request,
            current_user = Depends(self.get_current_user_with_audit),
            db: Session = Depends(get_db)
        ):
            # 检查权限
            user_service = RBACUserService(db)
            user_permissions = user_service.get_user_permissions(current_user.user_id)
            
            if permission not in user_permissions:
                # 记录权限拒绝审计日志
                await self._log_permission_denied(request, current_user, permission, resource_type, db)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要权限: {permission}"
                )
            
            # 记录权限验证成功审计日志
            await self._log_permission_granted(request, current_user, permission, resource_type, db)
            
            return current_user
        
        return dependency

    def require_data_permission(self, resource_type: str, operation: str) -> Callable:
        """
        数据权限验证装饰器
        
        Args:
            resource_type: 资源类型 (USER/ROLE/DEPT/MENU)
            operation: 操作类型 (VIEW/ADD/UPDATE/DELETE)
            
        Returns:
            装饰器函数
        """
        async def dependency(
            request: Request,
            current_user = Depends(self.get_current_user_with_audit),
            db: Session = Depends(get_db)
        ):
            # 获取数据权限规则
            data_permission_service = DataPermissionService(db)
            rules = data_permission_service.get_user_data_permission_rules(
                current_user.user_id, resource_type, operation
            )
            
            if not rules:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"无权限访问{resource_type}资源"
                )
            
            # 将数据权限规则添加到请求上下文
            request.state.data_permission_rules = rules
            
            return current_user
        
        return dependency

    async def _log_user_access(self, request: Request, user, db: Session):
        """记录用户访问审计日志"""
        try:
            audit_service = AuditLogService(db)
            await audit_service.log_user_access(
                user_id=user.user_id,
                username=user.username,
                ip_address=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", ""),
                endpoint=str(request.url.path),
                method=request.method
            )
        except Exception as e:
            self.logger.error(f"记录用户访问审计日志失败: {str(e)}")

    async def _log_permission_granted(self, request: Request, user, permission: str, resource_type: str, db: Session):
        """记录权限验证成功审计日志"""
        try:
            audit_service = AuditLogService(db)
            await audit_service.log_permission_check(
                user_id=user.user_id,
                username=user.username,
                permission=permission,
                resource_type=resource_type,
                result="GRANTED",
                ip_address=request.client.host if request.client else "unknown",
                endpoint=str(request.url.path)
            )
        except Exception as e:
            self.logger.error(f"记录权限验证审计日志失败: {str(e)}")

    async def _log_permission_denied(self, request: Request, user, permission: str, resource_type: str, db: Session):
        """记录权限拒绝审计日志"""
        try:
            audit_service = AuditLogService(db)
            await audit_service.log_permission_check(
                user_id=user.user_id,
                username=user.username,
                permission=permission,
                resource_type=resource_type,
                result="DENIED",
                ip_address=request.client.host if request.client else "unknown",
                endpoint=str(request.url.path)
            )
        except Exception as e:
            self.logger.error(f"记录权限拒绝审计日志失败: {str(e)}")


# 创建全局RBAC认证实例
rbac_auth = RBACAuth()

# 常用的依赖函数
get_current_user_with_audit = rbac_auth.get_current_user_with_audit
get_current_user = rbac_auth.get_current_user

# 常用权限验证函数（带审计日志）
def require_user_view_with_audit():
    """需要用户查看权限（带审计日志）"""
    return rbac_auth.require_permission_with_audit("user:view", "USER")

def require_user_add_with_audit():
    """需要用户新增权限（带审计日志）"""
    return rbac_auth.require_permission_with_audit("user:add", "USER")

def require_user_update_with_audit():
    """需要用户修改权限（带审计日志）"""
    return rbac_auth.require_permission_with_audit("user:update", "USER")

def require_user_delete_with_audit():
    """需要用户删除权限（带审计日志）"""
    return rbac_auth.require_permission_with_audit("user:delete", "USER")

def require_user_data_permission():
    """需要用户数据权限"""
    return rbac_auth.require_data_permission("USER", "VIEW")

def require_role_data_permission():
    """需要角色数据权限"""
    return rbac_auth.require_data_permission("ROLE", "VIEW")

def require_dept_data_permission():
    """需要部门数据权限"""
    return rbac_auth.require_data_permission("DEPT", "VIEW")



