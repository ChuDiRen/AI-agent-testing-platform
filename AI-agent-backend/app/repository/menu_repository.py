# Copyright (c) 2025 左岚. All rights reserved.
"""
菜单Repository
实现菜单相关的数据访问操作
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.entity.menu import Menu
from app.repository.base import BaseRepository


class MenuRepository(BaseRepository[Menu]):
    """
    菜单Repository类
    提供菜单相关的数据库操作方法
    """

    def __init__(self, db: Session):
        """
        初始化菜单Repository
        
        Args:
            db: 数据库会话
        """
        super().__init__(db, Menu)

    def get_by_parent_id(self, parent_id: int) -> List[Menu]:
        """
        根据父级ID查询子菜单
        
        Args:
            parent_id: 父级菜单ID
            
        Returns:
            子菜单列表
        """
        return self.db.query(Menu).filter(
            Menu.parent_id == parent_id
        ).order_by(Menu.order_num).all()

    def get_top_level_menus(self) -> List[Menu]:
        """
        获取顶级菜单（父级ID为0）
        
        Returns:
            顶级菜单列表
        """
        return self.get_by_parent_id(0)

    def get_menus_only(self) -> List[Menu]:
        """
        只获取菜单类型的记录（TYPE='0'）
        
        Returns:
            菜单列表
        """
        return self.db.query(Menu).filter(
            Menu.TYPE == '0'
        ).order_by(Menu.order_num).all()

    def get_buttons_only(self) -> List[Menu]:
        """
        只获取按钮类型的记录（TYPE='1'）
        
        Returns:
            按钮列表
        """
        return self.db.query(Menu).filter(
            Menu.TYPE == '1'
        ).order_by(Menu.order_num).all()

    def get_by_permission(self, permission: str) -> Optional[Menu]:
        """
        根据权限标识查询菜单
        
        Args:
            permission: 权限标识
            
        Returns:
            菜单对象或None
        """
        return self.db.query(Menu).filter(Menu.perms == permission).first()

    def get_menu_tree(self) -> List[Menu]:
        """
        获取完整的菜单树结构
        
        Returns:
            菜单树列表
        """
        # 获取所有菜单，按ORDER_NUM排序
        all_menus = self.db.query(Menu).order_by(Menu.order_num).all()
        
        # 构建菜单树（这里返回所有菜单，前端可以根据PARENT_ID构建树形结构）
        return all_menus

    def search_by_name(self, keyword: str) -> List[Menu]:
        """
        根据菜单名称搜索
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的菜单列表
        """
        return self.db.query(Menu).filter(
            Menu.menu_name.like(f"%{keyword}%")
        ).order_by(Menu.order_num).all()

    def get_permissions_by_role_id(self, role_id: int) -> List[str]:
        """
        根据角色ID获取权限标识列表
        
        Args:
            role_id: 角色ID
            
        Returns:
            权限标识列表
        """
        from app.entity.role_menu import RoleMenu
        
        # 联表查询获取角色对应的权限
        permissions = self.db.query(Menu.perms).join(
            RoleMenu, Menu.id == RoleMenu.menu_id  # 修复：使用正确的属性名
        ).filter(
            RoleMenu.role_id == role_id,
            Menu.perms.isnot(None)  # 只获取有权限标识的菜单
        ).all()
        
        # 提取权限标识字符串
        return [perm[0] for perm in permissions if perm[0]]

    def get_menus_by_role_id(self, role_id: int) -> List[Menu]:
        """
        根据角色ID获取菜单列表
        
        Args:
            role_id: 角色ID
            
        Returns:
            菜单列表
        """
        from app.entity.role_menu import RoleMenu
        
        return self.db.query(Menu).join(
            RoleMenu, Menu.menu_id == RoleMenu.menu_id
        ).filter(
            RoleMenu.role_id == role_id
        ).order_by(Menu.order_num).all()
