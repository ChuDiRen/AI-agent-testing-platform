"""菜单管理 Service 层"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlmodel import Session, select

from app.models.MenuModel import Menu
from app.models.RoleMenuModel import RoleMenu
from app.schemas.MenuSchema import MenuCreate, MenuUpdate


class MenuService:
    """菜单管理服务类"""

    @staticmethod
    def _build_tree(menu_list: List[Menu], parent_id: int = 0, visited: set = None, logger=None) -> List[Dict[str, Any]]:
        """构建菜单树"""
        if visited is None:
            visited = set()
        tree = []
        for menu in menu_list:
            if menu.parent_id == parent_id:
                if menu.id in visited and menu.id != 0:
                    if logger:
                        logger.warning(f"检测到循环引用，跳过菜单: id={menu.id}, parent_id={menu.parent_id}, name={menu.menu_name}")
                    continue
                if menu.id == 0 and menu.parent_id == 0:
                    node = {
                        "id": menu.id, "parent_id": menu.parent_id, "menu_name": menu.menu_name,
                        "path": menu.path, "component": menu.component, "query": menu.query,
                        "perms": menu.perms, "icon": menu.icon, "menu_type": menu.menu_type,
                        "visible": menu.visible, "status": menu.status, "is_cache": menu.is_cache,
                        "is_frame": menu.is_frame, "order_num": menu.order_num, "remark": menu.remark,
                        "create_time": menu.create_time.strftime("%Y-%m-%d %H:%M:%S") if menu.create_time else None,
                        "children": []
                    }
                    tree.append(node)
                    continue
                new_visited = visited.copy()
                new_visited.add(menu.id)
                node = {
                    "id": menu.id, "parent_id": menu.parent_id, "menu_name": menu.menu_name,
                    "path": menu.path, "component": menu.component, "query": menu.query,
                    "perms": menu.perms, "icon": menu.icon, "menu_type": menu.menu_type,
                    "visible": menu.visible, "status": menu.status, "is_cache": menu.is_cache,
                    "is_frame": menu.is_frame, "order_num": menu.order_num, "remark": menu.remark,
                    "create_time": menu.create_time.strftime("%Y-%m-%d %H:%M:%S") if menu.create_time else None,
                    "children": MenuService._build_tree(menu_list, menu.id, new_visited, logger)
                }
                tree.append(node)
        return sorted(tree, key=lambda x: x["order_num"])

    @staticmethod
    def get_tree(session: Session, logger=None) -> List[Dict[str, Any]]:
        """获取菜单树（用于菜单配置管理）"""
        statement = select(Menu)
        menus = session.exec(statement).all()
        return MenuService._build_tree(menus, logger=logger)

    @staticmethod
    def get_user_menu_tree(session: Session, role_ids: List[int], logger=None) -> List[Dict[str, Any]]:
        """获取用户有权限的菜单树（用于前端动态菜单）"""
        from sqlmodel import select
        from app.models.RoleMenuModel import RoleMenu
        
        # 获取角色关联的菜单ID
        statement = select(RoleMenu.menu_id).where(RoleMenu.role_id.in_(role_ids))
        menu_ids = session.exec(statement).all()
        
        if not menu_ids:
            return []
        
        # 获取这些菜单的详细信息（只显示可见且启用的菜单）
        statement = select(Menu).where(
            Menu.id.in_(menu_ids),
            Menu.visible == '0',  # 0显示 1隐藏
            Menu.status == '0'    # 0正常 1停用
        ).order_by(Menu.order_num)
        
        menus = session.exec(statement).all()
        return MenuService._build_tree(menus, logger=logger)

    @staticmethod
    def query_by_id(session: Session, menu_id: int) -> Optional[Menu]:
        """根据ID查询菜单"""
        return session.get(Menu, menu_id)

    @staticmethod
    def create(session: Session, request: MenuCreate) -> Menu:
        """新增菜单"""
        obj = Menu(**request.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @staticmethod
    def update(session: Session, request: MenuUpdate) -> Optional[Menu]:
        """更新菜单"""
        obj = session.get(Menu, request.id)
        if not obj:
            return None
        update_data = request.model_dump(exclude_unset=True, exclude={"id"})
        update_data["modify_time"] = datetime.now()
        for key, value in update_data.items():
            setattr(obj, key, value)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @staticmethod
    def delete(session: Session, menu_id: int) -> Optional[str]:
        """删除菜单，返回错误信息或None（成功）"""
        obj = session.get(Menu, menu_id)
        if not obj:
            return "数据不存在"
        
        statement = select(Menu).where(Menu.parent_id == menu_id)
        children = session.exec(statement).all()
        if children:
            return "存在子菜单，无法删除"
        
        statement = select(RoleMenu).where(RoleMenu.menu_id == menu_id)
        role_menus = session.exec(statement).all()
        for rm in role_menus:
            session.delete(rm)
        
        session.delete(obj)
        session.commit()
        return None

