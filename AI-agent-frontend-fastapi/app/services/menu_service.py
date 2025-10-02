"""菜单业务逻辑层"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.menu import Menu
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu import MenuCreate, MenuUpdate, MenuTree


class MenuService:
    """菜单服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.menu_repo = MenuRepository(db)
    
    async def create_menu(self, menu_data: MenuCreate) -> Menu:
        """创建菜单"""
        menu = Menu(
            **menu_data.model_dump(),
            create_time=datetime.now()
        )
        return await self.menu_repo.create(menu)
    
    async def get_menu_by_id(self, menu_id: int) -> Menu:
        """根据ID获取菜单"""
        menu = await self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail="菜单不存在")
        return menu
    
    async def get_all_menus(self, skip: int = 0, limit: int = 100) -> List[Menu]:
        """获取所有菜单"""
        return await self.menu_repo.get_all(skip=skip, limit=limit)
    
    async def update_menu(self, menu_id: int, menu_data: MenuUpdate) -> Menu:
        """更新菜单"""
        menu = await self.get_menu_by_id(menu_id)
        
        update_data = menu_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(menu, field, value)
        
        menu.modify_time = datetime.now()
        return await self.menu_repo.update(menu)
    
    async def delete_menu(self, menu_id: int) -> bool:
        """删除菜单"""
        # 检查是否有子菜单
        children = await self.menu_repo.get_by_parent_id(menu_id)
        if children:
            raise HTTPException(status_code=400, detail="存在子菜单，无法删除")
        
        return await self.menu_repo.delete(menu_id)
    
    async def get_menu_tree(self) -> List[MenuTree]:
        """获取菜单树"""
        all_menus = await self.menu_repo.get_all()
        return self._build_tree(all_menus, 0)
    
    def _build_tree(self, menus: List[Menu], parent_id: int) -> List[MenuTree]:
        """构建菜单树"""
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                menu_tree = MenuTree.model_validate(menu)
                menu_tree.children = self._build_tree(menus, menu.menu_id)
                tree.append(menu_tree)
        return tree
    
    async def get_user_menus(self, user_id: int) -> List[Menu]:
        """获取用户菜单（根据用户角色）"""
        from app.repositories.user_repository import UserRepository
        
        user_repo = UserRepository(self.db)
        user = await user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        all_menus = []
        for role in user.roles:
            role_menus = await self.menu_repo.get_menus_by_role_id(role.role_id)
            all_menus.extend(role_menus)
        
        # 去重
        unique_menus = {menu.menu_id: menu for menu in all_menus}
        return list(unique_menus.values())

