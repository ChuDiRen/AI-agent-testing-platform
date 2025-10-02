"""菜单数据访问层"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.menu import Menu


class MenuRepository:
    """菜单仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, menu: Menu) -> Menu:
        """创建菜单"""
        self.db.add(menu)
        await self.db.commit()
        await self.db.refresh(menu)
        return menu
    
    async def get_by_id(self, menu_id: int) -> Optional[Menu]:
        """根据ID获取菜单"""
        result = await self.db.execute(
            select(Menu).where(Menu.menu_id == menu_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Menu]:
        """获取所有菜单"""
        result = await self.db.execute(
            select(Menu).offset(skip).limit(limit).order_by(Menu.order_num)
        )
        return list(result.scalars().all())
    
    async def get_by_parent_id(self, parent_id: int) -> List[Menu]:
        """根据父级ID获取菜单"""
        result = await self.db.execute(
            select(Menu).where(Menu.parent_id == parent_id).order_by(Menu.order_num)
        )
        return list(result.scalars().all())
    
    async def update(self, menu: Menu) -> Menu:
        """更新菜单"""
        await self.db.commit()
        await self.db.refresh(menu)
        return menu
    
    async def delete(self, menu_id: int) -> bool:
        """删除菜单"""
        result = await self.db.execute(
            delete(Menu).where(Menu.menu_id == menu_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_menus_by_role_id(self, role_id: int) -> List[Menu]:
        """根据角色ID获取菜单列表"""
        from app.models.role_menu import t_role_menu
        
        query = (
            select(Menu)
            .join(t_role_menu, Menu.menu_id == t_role_menu.c.menu_id)
            .where(t_role_menu.c.role_id == role_id)
            .order_by(Menu.order_num)
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

