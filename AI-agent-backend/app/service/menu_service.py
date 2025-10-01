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
                   icon: str = None, order_num: float = None, is_active: bool = True) -> Menu:
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
            is_active: 是否启用

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
            order_num=order_num,
            is_active=is_active
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

    def get_menu_tree(self, keyword: str = None, is_active: bool = None) -> List[Dict[str, Any]]:
        """
        获取菜单树结构

        Args:
            keyword: 搜索关键词
            is_active: 是否启用状态过滤

        Returns:
            菜单树列表
        """
        all_menus = self.menu_repository.get_menu_tree()

        # 应用过滤条件
        if keyword:
            # 去除关键词前后空格
            keyword = keyword.strip()
            if keyword:  # 确保去除空格后还有内容
                all_menus = [menu for menu in all_menus if keyword.lower() in menu.menu_name.lower()]

        if is_active is not None:
            all_menus = [menu for menu in all_menus if menu.is_active == is_active]

        # 构建菜单树
        menu_dict = {}
        for menu in all_menus:
            menu_dict[menu.id] = {
                "id": menu.id,  # 前端期望id字段
                "parent_id": menu.parent_id,
                "name": menu.menu_name,  # 前端期望name字段
                "menu_name": menu.menu_name,  # 保留原字段兼容性
                "path": menu.path,
                "component": menu.component,
                "perms": menu.perms,
                "icon": menu.icon,
                "menu_type": menu.menu_type,
                "order": menu.order_num,  # 前端期望order字段
                "order_num": menu.order_num,  # 保留原字段兼容性
                "is_active": menu.is_active,
                "created_at": menu.create_time.isoformat() if menu.create_time else None,  # 前端期望created_at字段
                "create_time": menu.create_time.isoformat() if menu.create_time else None,  # 保留原字段兼容性
                "modify_time": menu.modify_time.isoformat() if menu.modify_time else None,
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
                   order_num: float = None, is_active: bool = None) -> Optional[Menu]:
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
            is_active: 是否启用

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
            update_data['path'] = path
        if component is not None:
            update_data['component'] = component
        if perms is not None:
            update_data['perms'] = perms
        if icon is not None:
            update_data['icon'] = icon
        if order_num is not None:
            update_data['order_num'] = order_num
        if is_active is not None:
            update_data['is_active'] = is_active

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

    def get_user_menu_tree(self, user_id: int) -> List[dict]:
        """
        获取用户的菜单树结构 - 用于动态路由

        Args:
            user_id: 用户ID

        Returns:
            用户可访问的菜单树结构
        """
        # 获取用户可访问的菜单
        user_menus = self.get_user_menus(user_id)

        # 只获取菜单类型的项（menu_type='0'），排除按钮
        menu_items = [menu for menu in user_menus if menu.menu_type == '0']

        # 按order_num排序
        menu_items.sort(key=lambda x: x.order_num or 999)

        # 构建菜单树
        menu_tree = self._build_user_menu_tree(menu_items)

        return menu_tree

    def _build_user_menu_tree(self, menus: List) -> List[dict]:
        """
        构建用户菜单树结构

        Args:
            menus: 菜单列表

        Returns:
            菜单树结构
        """
        # 创建菜单字典，以ID为键
        menu_dict = {}
        for menu in menus:
            menu_dict[menu.id] = {
                "id": menu.id,
                "name": self._generate_route_name(menu.menu_name),
                "path": menu.path or f"/menu-{menu.id}",
                "component": menu.component or "Layout",
                "redirect": None,
                "meta": {
                    "title": menu.menu_name,
                    "icon": menu.icon,
                    "order": menu.order_num,
                    "hidden": False,
                    "keepAlive": False,
                    "permission": menu.perms
                },
                "children": []
            }

        # 构建树形结构
        root_menus = []
        for menu in menus:
            menu_node = menu_dict[menu.id]

            if menu.parent_id == 0:
                # 顶级菜单
                root_menus.append(menu_node)
            else:
                # 子菜单
                parent = menu_dict.get(menu.parent_id)
                if parent:
                    parent["children"].append(menu_node)

        # 为有子菜单的父菜单设置重定向
        for menu_node in self._flatten_menu_tree(root_menus):
            if menu_node["children"]:
                # 设置重定向到第一个子菜单
                first_child = menu_node["children"][0]
                menu_node["redirect"] = first_child["path"]

        return root_menus

    def _generate_route_name(self, menu_name: str) -> str:
        """
        生成路由名称

        Args:
            menu_name: 菜单名称

        Returns:
            路由名称
        """
        # 简单的名称转换，可以根据需要优化
        name_map = {
            "系统管理": "System",
            "用户管理": "User",
            "角色管理": "Role",
            "菜单管理": "Menu",
            "部门管理": "Department",
            "仪表板": "Dashboard",
            "代理管理": "Agent",
            "代理列表": "AgentList",
            "代理配置": "AgentConfig"
        }
        return name_map.get(menu_name, menu_name.replace(" ", ""))

    def _flatten_menu_tree(self, tree: List[dict]) -> List[dict]:
        """
        扁平化菜单树

        Args:
            tree: 菜单树

        Returns:
            扁平化的菜单列表
        """
        result = []
        for node in tree:
            result.append(node)
            if node["children"]:
                result.extend(self._flatten_menu_tree(node["children"]))
        return result
