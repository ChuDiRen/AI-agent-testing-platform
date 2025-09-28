# Copyright (c) 2025 左岚. All rights reserved.
"""
RBAC权限验证中间件
实现细粒度权限控制、数据权限过滤和审计日志记录
"""

from functools import wraps
from typing import Callable

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.core.security import verify_token
from app.db.session import get_db
from app.service.audit_log_service import AuditLogService
from app.service.data_permission_service import DataPermissionService
from app.service.user_service import RBACUserService
from app.core.token_blacklist import is_blacklisted

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
        获取当前用户并记录审计日志 - 增强版本，包含更详细的错误处理
        """
        if not credentials:
            self.logger.warning("Authentication failed: No credentials provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials
        if not token or not isinstance(token, str):
            self.logger.warning("Authentication failed: Invalid token format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的token格式",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # 检查黑名单
            if is_blacklisted(token):
                self.logger.warning(f"Authentication failed: Token is blacklisted")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token已失效",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 验证token
            payload = verify_token(token)
            if payload is None:
                self.logger.warning("Authentication failed: Token verification returned None")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token验证失败",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user_id_str = payload.get("sub")
            if not user_id_str:
                self.logger.warning("Authentication failed: Token missing user ID (sub)")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token中缺少用户ID",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 转换用户ID为整数
            try:
                user_id = int(user_id_str)
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Authentication failed: Invalid user ID format: {user_id_str}, error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的用户ID格式",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 获取用户信息
            try:
                user_service = RBACUserService(db)
                user = user_service.get_user_by_id(user_id)
            except Exception as e:
                self.logger.error(f"Database error while fetching user {user_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据库查询失败",
                )
            
            if not user:
                self.logger.warning(f"Authentication failed: User {user_id} not found in database")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 记录访问审计日志 (暂时禁用以解决403问题)
            try:
                await self._log_user_access(request, user, db)
            except Exception as e:
                self.logger.warning(f"审计日志记录失败，但不影响请求: {str(e)}")
            
            self.logger.debug(f"User {user_id} authenticated successfully")
            return user

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during authentication: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="认证过程中发生内部错误",
            )

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        """
        获取当前用户（不记录审计日志）- 增强版本，包含更详细的错误处理
        """
        if not credentials:
            self.logger.warning("Authentication failed: No credentials provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials
        if not token or not isinstance(token, str):
            self.logger.warning("Authentication failed: Invalid token format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的token格式",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # 检查黑名单
            if is_blacklisted(token):
                self.logger.warning(f"Authentication failed: Token is blacklisted")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token已失效",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 验证token
            payload = verify_token(token)
            if payload is None:
                self.logger.warning("Authentication failed: Token verification returned None")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token验证失败",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user_id_str = payload.get("sub")
            if not user_id_str:
                self.logger.warning("Authentication failed: Token missing user ID (sub)")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token中缺少用户ID",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 转换用户ID为整数
            try:
                user_id = int(user_id_str)
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Authentication failed: Invalid user ID format: {user_id_str}, error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的用户ID格式",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 获取用户信息
            try:
                user_service = RBACUserService(db)
                user = user_service.get_user_by_id(user_id)
            except Exception as e:
                self.logger.error(f"Database error while fetching user {user_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据库查询失败",
                )
            
            if not user:
                self.logger.warning(f"Authentication failed: User {user_id} not found in database")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            self.logger.debug(f"User {user_id} authenticated successfully")
            return user

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during authentication: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="认证过程中发生内部错误",
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
                user_permissions = user_service.get_user_permissions(current_user.id)
                
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
            user_permissions = user_service.get_user_permissions(current_user.id)

            # 添加调试日志
            self.logger.info(f"User {current_user.id} permissions: {user_permissions}")
            self.logger.info(f"Required permission: {permission}")

            if permission not in user_permissions:
                # 记录权限拒绝审计日志
                await self._log_permission_denied(request, current_user, permission, resource_type, db)
                self.logger.warning(f"Permission denied for user {current_user.id}: required {permission}, has {user_permissions}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要权限: {permission}"
                )

            # 记录权限验证成功审计日志
            await self._log_permission_granted(request, current_user, permission, resource_type, db)
            self.logger.info(f"Permission granted for user {current_user.id}: {permission}")

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
                current_user.id, resource_type, operation
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
                user_id=user.id,  # 修复：使用正确的属性名
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
                user_id=user.id,
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
                user_id=user.id,
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

def require_log_view_with_audit():
    """需要日志查看权限（带审计日志）"""
    return rbac_auth.require_permission_with_audit("log:view", "LOG")

def require_log_delete_with_audit():
    """需要日志删除权限（带审计日志）"""
    return rbac_auth.require_permission_with_audit("log:delete", "LOG")



