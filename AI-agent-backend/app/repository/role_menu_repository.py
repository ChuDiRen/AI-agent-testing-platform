# Copyright (c) 2025 左岚. All rights reserved.
"""
角色菜单关联Repository
实现角色菜单关联相关的数据访问操作
"""

from typing import List

from sqlalchemy.orm import Session

from app.entity.menu import Menu
from app.entity.role_menu import RoleMenu
from app.repository.base import BaseRepository


class RoleMenuRepository(BaseRepository[RoleMenu]):
    """
    角色菜单关联Repository类
    提供角色菜单关联相关的数据库操作方法
    """

    def __init__(self, db: Session):
        """
        初始化角色菜单关联Repository
        
        Args:
            db: 数据库会话
        """
        super().__init__(db, RoleMenu)

    def get_by_role_id(self, role_id: int) -> List[RoleMenu]:
        """
        根据角色ID查询角色菜单关联
        
        Args:
            role_id: 角色ID
            
        Returns:
            角色菜单关联列表
        """
        return self.db.query(RoleMenu).filter(RoleMenu.role_id == role_id).all()

    def get_by_menu_id(self, menu_id: int) -> List[RoleMenu]:
        """
        根据菜单ID查询角色菜单关联
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            角色菜单关联列表
        """
        return self.db.query(RoleMenu).filter(RoleMenu.menu_id == menu_id).all()

    def get_menus_by_role_id(self, role_id: int) -> List[Menu]:
        """
        根据角色ID获取角色的所有菜单
        
        Args:
            role_id: 角色ID
            
        Returns:
            菜单列表
        """
        return self.db.query(Menu).join(
            RoleMenu, Menu.id == RoleMenu.menu_id
        ).filter(RoleMenu.role_id == role_id).order_by(Menu.ORDER_NUM).all()

    def get_menu_ids_by_role_id(self, role_id: int) -> List[int]:
        """
        根据角色ID获取菜单ID列表
        
        Args:
            role_id: 角色ID
            
        Returns:
            菜单ID列表
        """
        result = self.db.query(RoleMenu.menu_id).filter(RoleMenu.role_id == role_id).all()
        return [menu_id[0] for menu_id in result]

    def exists(self, role_id: int, menu_id: int) -> bool:
        """
        检查角色菜单关联是否存在
        
        Args:
            role_id: 角色ID
            menu_id: 菜单ID
            
        Returns:
            True表示存在，False表示不存在
        """
        return self.db.query(RoleMenu).filter(
            RoleMenu.role_id == role_id,
            RoleMenu.menu_id == menu_id
        ).first() is not None

    def delete_by_role_id(self, role_id: int) -> int:
        """
        删除角色的所有菜单关联
        
        Args:
            role_id: 角色ID
            
        Returns:
            删除的记录数
        """
        count = self.db.query(RoleMenu).filter(RoleMenu.role_id == role_id).count()
        self.db.query(RoleMenu).filter(RoleMenu.role_id == role_id).delete()
        return count

    def delete_by_menu_id(self, menu_id: int) -> int:
        """
        删除菜单的所有角色关联
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            删除的记录数
        """
        count = self.db.query(RoleMenu).filter(RoleMenu.menu_id == menu_id).count()
        self.db.query(RoleMenu).filter(RoleMenu.menu_id == menu_id).delete()
        return count

    def delete_specific(self, role_id: int, menu_id: int) -> bool:
        """
        删除特定的角色菜单关联
        
        Args:
            role_id: 角色ID
            menu_id: 菜单ID
            
        Returns:
            True表示删除成功，False表示记录不存在
        """
        result = self.db.query(RoleMenu).filter(
            RoleMenu.role_id == role_id,
            RoleMenu.menu_id == menu_id
        ).delete()
        return result > 0

    def assign_menus_to_role(self, role_id: int, menu_ids: List[int]) -> None:
        """
        为角色分配菜单权限（先清除原有权限，再分配新权限）
        
        Args:
            role_id: 角色ID
            menu_ids: 菜单ID列表
        """
        # 先删除角色的所有菜单权限
        self.delete_by_role_id(role_id)
        
        # 分配新的菜单权限
        for menu_id in menu_ids:
            role_menu = RoleMenu(role_id=role_id, menu_id=menu_id)
            self.db.add(role_menu)

    def add_menu_to_role(self, role_id: int, menu_id: int) -> bool:
        """
        为角色添加菜单权限（如果不存在的话）
        
        Args:
            role_id: 角色ID
            menu_id: 菜单ID
            
        Returns:
            True表示添加成功，False表示已存在
        """
        if self.exists(role_id, menu_id):
            return False
        
        role_menu = RoleMenu(role_id=role_id, menu_id=menu_id)
        self.db.add(role_menu)
        return True

    def get_permissions_by_role_id(self, role_id: int) -> List[str]:
        """
        根据角色ID获取权限标识列表
        
        Args:
            role_id: 角色ID
            
        Returns:
            权限标识列表
        """
        permissions = self.db.query(Menu.perms).join(
            RoleMenu, Menu.id == RoleMenu.menu_id  # 修复：使用正确的属性名
        ).filter(
            RoleMenu.role_id == role_id,
            Menu.perms.isnot(None)  # 只获取有权限标识的菜单
        ).all()
        
        # 提取权限标识字符串
        return [perm[0] for perm in permissions if perm[0]]
