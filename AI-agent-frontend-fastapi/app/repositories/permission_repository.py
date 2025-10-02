"""权限数据访问层"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.permission import Permission


class PermissionRepository:
    """权限数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, permission_id: int) -> Optional[Permission]:
        """根据ID获取权限"""
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[Permission]:
        """根据代码获取权限"""
        result = await self.db.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, permission_ids: List[int]) -> List[Permission]:
        """根据ID列表获取权限"""
        result = await self.db.execute(
            select(Permission).where(Permission.id.in_(permission_ids))
        )
        return result.scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Permission]:
        """获取所有权限"""
        result = await self.db.execute(
            select(Permission).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, permission: Permission) -> Permission:
        """创建权限"""
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission
    
    async def update(self, permission: Permission) -> Permission:
        """更新权限"""
        await self.db.commit()
        await self.db.refresh(permission)
        return permission
    
    async def delete(self, permission: Permission) -> None:
        """删除权限"""
        await self.db.delete(permission)
        await self.db.commit()

