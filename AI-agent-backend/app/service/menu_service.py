# Copyright (c) 2025 左岚. All rights reserved.
"""
菜单Service
实现菜单相关的业务逻辑
"""

from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.entity.menu import Menu
from app.repository.menu_repository import MenuRepository
from app.repository.role_menu_repository import RoleMenuRepository
from app.utils.redis_client import get_cache_client

logger = get_logger(__name__)


class MenuService:
    """
    菜单Service类
    提供菜单相关的业务逻辑处理
    """

    def __init__(self, db: Session):
        """
        初始化菜单Service
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.menu_repository = MenuRepository(db)
        self.role_menu_repository = RoleMenuRepository(db)

    def create_menu(self, parent_id: int, menu_name: str, menu_type: str,
                   path: str = None, component: str = None, perms: str = None,
                   icon: str = None, order_num: float = None) -> Menu:
        """
        创建菜单
        
        Args:
            parent_id: 上级菜单ID，0表示顶级菜单
            menu_name: 菜单/按钮名称
            menu_type: 类型，'0'菜单 '1'按钮
            path: 路由路径
            component: 路由组件
            perms: 权限标识
            icon: 图标
            order_num: 排序号
            
        Returns:
            创建的菜单对象
        """
        menu = Menu(
            parent_id=parent_id,
            menu_name=menu_name,
            menu_type=menu_type,
            path=path,
            component=component,
            perms=perms,
            icon=icon,
            order_num=order_num
        )
        
        created_menu = self.menu_repository.create(menu)
        logger.info(f"Created menu: {menu_name}")
        return created_menu

    def get_menu_by_id(self, menu_id: int) -> Optional[Menu]:
        """
        根据ID获取菜单
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            菜单对象或None
        """
        return self.menu_repository.get_by_id(menu_id)

    def get_menu_tree(self) -> List[Dict[str, Any]]:
        """
        获取菜单树结构
        
        Returns:
            菜单树列表
        """
        all_menus = self.menu_repository.get_menu_tree()
        
        # 构建菜单树
        menu_dict = {}
        for menu in all_menus:
            menu_dict[menu.id] = {  # 修复：使用正确的属性名
                "menu_id": menu.id,  # 修复：使用正确的属性名
                "parent_id": menu.parent_id,
                "menu_name": menu.menu_name,
                "path": menu.PATH,
                "component": menu.COMPONENT,
                "perms": menu.perms,
                "icon": menu.icon,
                "type": menu.TYPE,
                "order_num": menu.order_num,
                "children": []
            }
        
        # 构建父子关系
        tree = []
        for menu_data in menu_dict.values():
            if menu_data["parent_id"] == 0:
                tree.append(menu_data)
            else:
                parent = menu_dict.get(menu_data["parent_id"])
                if parent:
                    parent["children"].append(menu_data)
        
        return tree

    def get_menus_only(self) -> List[Menu]:
        """
        只获取菜单类型的记录
        
        Returns:
            菜单列表
        """
        return self.menu_repository.get_menus_only()

    def get_buttons_only(self) -> List[Menu]:
        """
        只获取按钮类型的记录
        
        Returns:
            按钮列表
        """
        return self.menu_repository.get_buttons_only()

    def get_top_level_menus(self) -> List[Menu]:
        """
        获取顶级菜单
        
        Returns:
            顶级菜单列表
        """
        return self.menu_repository.get_top_level_menus()

    def get_children_menus(self, parent_id: int) -> List[Menu]:
        """
        获取子菜单
        
        Args:
            parent_id: 父级菜单ID
            
        Returns:
            子菜单列表
        """
        return self.menu_repository.get_by_parent_id(parent_id)

    def update_menu(self, menu_id: int, menu_name: str = None, path: str = None,
                   component: str = None, perms: str = None, icon: str = None,
                   order_num: float = None) -> Optional[Menu]:
        """
        更新菜单信息
        
        Args:
            menu_id: 菜单ID
            menu_name: 菜单名称
            path: 路由路径
            component: 路由组件
            perms: 权限标识
            icon: 图标
            order_num: 排序号
            
        Returns:
            更新后的菜单对象或None
        """
        menu = self.menu_repository.get_by_id(menu_id)
        if not menu:
            logger.warning(f"Menu not found with id: {menu_id}")
            return None
        
        # 准备更新数据
        update_data = {}
        if menu_name is not None:
            update_data['menu_name'] = menu_name
        if path is not None:
            update_data['PATH'] = path
        if component is not None:
            update_data['COMPONENT'] = component
        if perms is not None:
            update_data['perms'] = perms
        if icon is not None:
            update_data['icon'] = icon
        if order_num is not None:
            update_data['order_num'] = order_num

        # 如果没有要更新的数据，直接返回原菜单
        if not update_data:
            return menu

        updated_menu = self.menu_repository.update(menu_id, update_data)
        logger.info(f"Updated menu: {menu_id}")
        return updated_menu

    def delete_menu(self, menu_id: int) -> bool:
        """
        删除菜单
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            是否删除成功
            
        Raises:
            ValueError: 菜单仍有子菜单或角色关联
        """
        # 检查是否有子菜单
        children = self.menu_repository.get_by_parent_id(menu_id)
        if children:
            raise ValueError(f"菜单仍有 {len(children)} 个子菜单，无法删除")
        
        # 检查是否有角色关联
        role_menus = self.role_menu_repository.get_by_menu_id(menu_id)
        if role_menus:
            raise ValueError(f"菜单仍有 {len(role_menus)} 个角色关联，无法删除")
        
        # 删除菜单
        success = self.menu_repository.delete(menu_id)
        
        if success:
            logger.info(f"Deleted menu: {menu_id}")
        
        return success

    def search_menus(self, keyword: str) -> List[Menu]:
        """
        搜索菜单
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的菜单列表
        """
        return self.menu_repository.search_by_name(keyword)

    def get_user_menus(self, user_id: int) -> List[Menu]:
        """
        获取用户的菜单权限
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户可访问的菜单列表
        """
        from app.repository.user_role_repository import UserRoleRepository
        
        # 获取用户的所有角色
        user_role_repository = UserRoleRepository(self.db)
        roles = user_role_repository.get_roles_by_user_id(user_id)
        
        # 获取所有角色的菜单权限
        all_menus = []
        for role in roles:
            menus = self.role_menu_repository.get_menus_by_role_id(role.id)  # 修复：使用正确的属性名
            all_menus.extend(menus)

        # 去重
        unique_menus = {}
        for menu in all_menus:
            unique_menus[menu.id] = menu  # 修复：使用正确的属性名
        
        return list(unique_menus.values())

    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        获取用户的权限标识列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            权限标识列表
        """
        cache_key = f"user_permissions_{user_id}"
        cache_client = get_cache_client()  # 获取缓存客户端实例
        cached_permissions = cache_client.get(cache_key)
        if cached_permissions is not None:
            logger.debug(f"Returning cached permissions for user {user_id}")
            return cached_permissions

        from app.repository.user_role_repository import UserRoleRepository

        # 获取用户的所有角色
        user_role_repository = UserRoleRepository(self.db)
        roles = user_role_repository.get_roles_by_user_id(user_id)

        # 获取所有角色的权限
        all_permissions = []
        for role in roles:
            permissions = self.role_menu_repository.get_permissions_by_role_id(role.id)  # 修复：使用正确的属性名
            all_permissions.extend(permissions)

        # 去重
        unique_permissions = list(set(all_permissions))

        # 存入缓存
        cache_client.set(cache_key, unique_permissions, ttl=3600)  # 缓存1小时
        logger.debug(f"Cached new permissions for user {user_id}")

        return unique_permissions
