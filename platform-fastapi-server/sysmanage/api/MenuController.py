from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from core.resp_model import respModel
from core.logger import get_logger
from ..model.menu import Menu
from ..model.user_role import UserRole
from ..model.role_menu import RoleMenu
from ..schemas.menu_schema import MenuQuery, MenuCreate, MenuUpdate, MenuTree
from core.database import get_session
from core.time_utils import TimeFormatter
from datetime import datetime

module_name = "menu"
module_model = Menu
module_route = APIRouter(prefix=f"/{module_name}", tags=["菜单管理"])
logger = get_logger(__name__)

@module_route.get("/tree")
def getTree(session: Session = Depends(get_session)):
    """获取菜单树"""
    try:
        statement = select(module_model)
        menus = session.exec(statement).all()

        # 构建菜单树（内联实现，参考RuoYi-Vue-Plus）
        def _build_tree(menu_list, parent_id=0, visited=None):
            if visited is None:
                visited = set()
            tree = []
            for menu in menu_list:
                if menu.parent_id == parent_id:
                    if menu.id in visited and menu.id != 0:
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
                        "children": _build_tree(menu_list, menu.id, new_visited)
                    }
                    tree.append(node)
            return sorted(tree, key=lambda x: x["order_num"])

        tree = _build_tree(menus)
        return respModel.ok_resp_tree(treeData=tree, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById")
def queryById(id: int, session: Session = Depends(get_session)):
    """根据ID查询菜单"""
    try:
        obj = session.get(module_model, id)
        return respModel.ok_resp(obj=obj) if obj else respModel.error_resp("数据不存在")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert")
def insert(request: MenuCreate, session: Session = Depends(get_session)):
    """新增菜单"""
    try:
        obj = module_model(**request.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return respModel.ok_resp(obj=obj, msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/update")
def update(request: MenuUpdate, session: Session = Depends(get_session)):
    """更新菜单"""
    try:
        obj = session.get(module_model, request.id)
        if not obj:
            return respModel.error_resp("数据不存在")
        update_data = request.model_dump(exclude_unset=True, exclude={"id"})
        update_data["modify_time"] = datetime.now()
        for key, value in update_data.items():
            setattr(obj, key, value)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return respModel.ok_resp(obj=obj, msg="更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete")
def delete(id: int, session: Session = Depends(get_session)):
    """删除菜单"""
    try:
        obj = session.get(module_model, id)
        if not obj:
            return respModel.error_resp("数据不存在")
        statement = select(module_model).where(module_model.parent_id == id)
        children = session.exec(statement).all()
        if children:
            return respModel.error_resp("存在子菜单，无法删除")
        statement = select(RoleMenu).where(RoleMenu.menu_id == id)
        role_menus = session.exec(statement).all()
        for rm in role_menus:
            session.delete(rm)
        session.delete(obj)
        session.commit()
        return respModel.ok_resp_text(msg="删除成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/user/{user_id}")
def getUserMenus(user_id: int, session: Session = Depends(get_session)):
    """获取用户的菜单权限（用于前端路由）"""
    try:
        statement = select(UserRole).where(UserRole.user_id == user_id)
        user_roles = session.exec(statement).all()
        role_ids = [ur.role_id for ur in user_roles]
        if not role_ids:
            return respModel.ok_resp_tree(treeData=[], msg="查询成功")
        statement = select(RoleMenu).where(RoleMenu.role_id.in_(role_ids))
        role_menus = session.exec(statement).all()
        menu_ids = list(set([rm.menu_id for rm in role_menus]))
        if not menu_ids:
            return respModel.ok_resp_tree(treeData=[], msg="查询成功")
        statement = select(Menu).where(Menu.id.in_(menu_ids))
        menus = session.exec(statement).all()

        # 构建菜单树（内联实现）
        def _build_tree(menu_list, parent_id=0, visited=None):
            if visited is None:
                visited = set()
            tree = []
            for menu in menu_list:
                if menu.parent_id == parent_id:
                    if menu.id in visited and menu.id != 0:
                        continue
                    if menu.id == 0 and menu.parent_id == 0:
                        tree.append({"id": menu.id, "parent_id": menu.parent_id, "menu_name": menu.menu_name,
                                   "path": menu.path, "component": menu.component, "query": menu.query,
                                   "perms": menu.perms, "icon": menu.icon, "menu_type": menu.menu_type,
                                   "visible": menu.visible, "status": menu.status, "is_cache": menu.is_cache,
                                   "is_frame": menu.is_frame, "order_num": menu.order_num, "remark": menu.remark,
                                   "create_time": menu.create_time.strftime("%Y-%m-%d %H:%M:%S") if menu.create_time else None,
                                   "children": []})
                        continue
                    new_visited = visited.copy()
                    new_visited.add(menu.id)
                    tree.append({"id": menu.id, "parent_id": menu.parent_id, "menu_name": menu.menu_name,
                               "path": menu.path, "component": menu.component, "query": menu.query,
                               "perms": menu.perms, "icon": menu.icon, "menu_type": menu.menu_type,
                               "visible": menu.visible, "status": menu.status, "is_cache": menu.is_cache,
                               "is_frame": menu.is_frame, "order_num": menu.order_num, "remark": menu.remark,
                               "create_time": menu.create_time.strftime("%Y-%m-%d %H:%M:%S") if menu.create_time else None,
                               "children": _build_tree(menu_list, menu.id, new_visited)})
            return sorted(tree, key=lambda x: x["order_num"])

        tree = _build_tree(menus)
        return respModel.ok_resp_tree(treeData=tree, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

