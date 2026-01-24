"""
菜单 CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.services.base import CRUDBase
from app.models.menu import Menu


class CRUDMenu(CRUDBase[Menu, dict, dict]):
    """菜单 CRUD"""
    
    async def get_tree(
        self,
        db: AsyncSession,
        parent_id: int = 0,
        is_hidden: Optional[bool] = None
    ) -> List[Menu]:
        """获取菜单树"""
        query = select(Menu).where(Menu.parent_id == parent_id)
        
        if is_hidden is not None:
            query = query.where(Menu.is_hidden == is_hidden)
        
        query = query.order_by(Menu.order.asc())
        
        result = await db.execute(query)
        menus = result.scalars().all()
        
        # 递归获取子菜单
        for menu in menus:
            menu.children = await self.get_tree(db, menu.id, is_hidden)
        
        return menus
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Menu]:
        """获取所有菜单"""
        result = await db.execute(
            select(Menu)
            .offset(skip)
            .limit(limit)
            .order_by(Menu.order.asc())
        )
        return result.scalars().all()
    
    async def get_by_path(
        self,
        db: AsyncSession,
        path: str
    ) -> Optional[Menu]:
        """根据路径获取菜单"""
        result = await db.execute(
            select(Menu).filter(Menu.path == path)
        )
        return result.scalars().first()
    
    async def get_children(
        self,
        db: AsyncSession,
        parent_id: int
    ) -> List[Menu]:
        """获取子菜单"""
        result = await db.execute(
            select(Menu)
            .where(Menu.parent_id == parent_id)
            .order_by(Menu.order.asc())
        )
        return result.scalars().all()
    
    async def has_children(
        self,
        db: AsyncSession,
        parent_id: int
    ) -> bool:
        """检查是否有子菜单"""
        from sqlalchemy import func
        
        result = await db.execute(
            select(func.count(Menu.id)).where(Menu.parent_id == parent_id)
        )
        count = result.scalar()
        return count > 0


# 创建全局实例
menu = CRUDMenu(Menu)
