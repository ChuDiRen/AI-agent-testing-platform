"""角色数据访问层"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.role import Role


class RoleRepository:
    """角色数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        result = await self.db.execute(
            select(Role).where(Role.role_id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, role_name: str) -> Optional[Role]:
        """根据名称获取角色"""
        result = await self.db.execute(
            select(Role).where(Role.role_name == role_name)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """获取所有角色"""
        result = await self.db.execute(
            select(Role).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, role: Role) -> Role:
        """创建角色"""
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role
    
    async def update(self, role: Role) -> Role:
        """更新角色"""
        await self.db.commit()
        await self.db.refresh(role)
        return role
    
    async def delete(self, role: Role) -> None:
        """删除角色"""
        await self.db.delete(role)
        await self.db.commit()

