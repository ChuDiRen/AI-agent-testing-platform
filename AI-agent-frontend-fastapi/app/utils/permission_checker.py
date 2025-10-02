"""权限检查工具"""
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.permission import Permission
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission
from app.api.deps import get_current_active_user


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, required_permissions: List[str]):
        """
        初始化权限检查器
        
        Args:
            required_permissions: 需要的权限代码列表
        """
        self.required_permissions = required_permissions
    
    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """检查用户是否拥有所需权限"""
        # 超级管理员拥有所有权限
        if current_user.is_superuser:
            return current_user
        
        # 获取用户的所有权限
        user_permissions = await self._get_user_permissions(current_user.id, db)
        
        # 检查是否拥有所需权限
        for required_perm in self.required_permissions:
            if required_perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少权限: {required_perm}"
                )
        
        return current_user
    
    @staticmethod
    async def _get_user_permissions(user_id: int, db: AsyncSession) -> List[str]:
        """获取用户的所有权限代码"""
        # 查询用户的角色关联的权限
        result = await db.execute(
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user_id)
            .where(Permission.is_active == True)
        )
        
        permissions = result.scalars().all()
        return list(permissions)


def require_permissions(permissions: List[str]):
    """权限验证装饰器工厂
    
    使用示例:
        @router.delete("/{user_id}", dependencies=[Depends(require_permissions(["user:delete"]))])
        async def delete_user(...):
            pass
    """
    return PermissionChecker(permissions)

