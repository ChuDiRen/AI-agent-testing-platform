from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from core.resp_model import respModel
from core.logger import get_logger

logger = get_logger(__name__)
from ..model.menu import Menu
from ..model.user_role import UserRole
from ..model.role_menu import RoleMenu
from ..schemas.menu_schema import MenuQuery, MenuCreate, MenuUpdate, MenuTree
from core.database import get_session
from core.time_utils import TimeFormatter
from datetime import datetime
from typing import List, Dict

module_name = "menu"
module_model = Menu
module_route = APIRouter(prefix=f"/{module_name}", tags=["菜单管理"])

def build_tree(menus: List[Menu], parent_id: int = 0, visited: set = None) -> List[Dict]: # 构建菜单树（参考RuoYi-Vue-Plus）
    """
    构建菜单树结构
    :param menus: 菜单列表
    :param parent_id: 父菜单ID
    :param visited: 已访问的菜单ID集合，用于防止循环引用导致的无限递归
    :return: 菜单树列表
    """
    if visited is None:
        visited = set()
    
    tree = []
    for menu in menus:
        # 只处理parent_id等于指定parent_id的菜单
        if menu.parent_id == parent_id:
            # 防止循环引用：如果菜单id已经在访问路径中，跳过（除了id=0的特殊情况）
            if menu.id in visited and menu.id != 0:
                logger.warning(f"检测到循环引用，跳过菜单: id={menu.id}, parent_id={menu.parent_id}, name={menu.menu_name}")
                continue
            
            # 对于id=0且parent_id=0的特殊菜单，不递归查找子节点（避免无限递归）
            if menu.id == 0 and menu.parent_id == 0:
                node = {
                    "id": menu.id,
                    "parent_id": menu.parent_id,
                    "menu_name": menu.menu_name,
                    "path": menu.path,
                    "component": menu.component,
                    "query": menu.query,
                    "perms": menu.perms,
                    "icon": menu.icon,
                    "menu_type": menu.menu_type,
                    "visible": menu.visible,
                    "status": menu.status,
                    "is_cache": menu.is_cache,
                    "is_frame": menu.is_frame,
                    "order_num": menu.order_num,
                    "remark": menu.remark,
                    "create_time": menu.create_time.strftime("%Y-%m-%d %H:%M:%S") if menu.create_time else None,
                    "children": []  # id=0的菜单没有子节点，避免无限递归
                }
                tree.append(node)
                continue
            
            # 创建新的visited集合副本，加入当前菜单id
            new_visited = visited.copy()
            new_visited.add(menu.id)
            
            node = {
                "id": menu.id,
                "parent_id": menu.parent_id,
                "menu_name": menu.menu_name,
                "path": menu.path,
                "component": menu.component,
                "query": menu.query,
                "perms": menu.perms,
                "icon": menu.icon,
                "menu_type": menu.menu_type,
                "visible": menu.visible,
                "status": menu.status,
                "is_cache": menu.is_cache,
                "is_frame": menu.is_frame,
                "order_num": menu.order_num,
                "remark": menu.remark,
                "create_time": menu.create_time.strftime("%Y-%m-%d %H:%M:%S") if menu.create_time else None,
                "children": build_tree(menus, menu.id, new_visited)  # 递归构建子树
            }
            tree.append(node)
    
    return sorted(tree, key=lambda x: x["order_num"])

@module_route.get("/tree") # 获取菜单树
def getTree(session: Session = Depends(get_session)):
    try:
        statement = select(module_model)
        menus = session.exec(statement).all()
        tree = build_tree(menus)
        return respModel.ok_resp_tree(treeData=tree, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById") # 根据ID查询菜单
def queryById(id: int, session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, id)
        if obj:
            return respModel.ok_resp(obj=obj)
        else:
            return respModel.error_resp("数据不存在")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert") # 新增菜单
def insert(request: MenuCreate, session: Session = Depends(get_session)):
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

@module_route.put("/update") # 更新菜单
def update(request: MenuUpdate, session: Session = Depends(get_session)):
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

@module_route.delete("/delete") # 删除菜单
def delete(id: int, session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, id)
        if not obj:
            return respModel.error_resp("数据不存在")
        
        # 检查是否有子菜单
        statement = select(module_model).where(module_model.parent_id == id)
        children = session.exec(statement).all()
        if children:
            return respModel.error_resp("存在子菜单，无法删除")
        
        # 删除菜单关联的角色权限
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

@module_route.get("/user/{user_id}") # 获取用户的菜单权限（用于前端路由）
def getUserMenus(user_id: int, session: Session = Depends(get_session)):
    try:
        # 获取用户的所有角色
        statement = select(UserRole).where(UserRole.user_id == user_id)
        user_roles = session.exec(statement).all()
        role_ids = [ur.role_id for ur in user_roles]
        
        if not role_ids:
            return respModel.ok_resp_tree(treeData=[], msg="查询成功")
        
        # 获取角色的所有菜单权限
        statement = select(RoleMenu).where(RoleMenu.role_id.in_(role_ids))
        role_menus = session.exec(statement).all()
        menu_ids = list(set([rm.menu_id for rm in role_menus]))
        
        if not menu_ids:
            return respModel.ok_resp_tree(treeData=[], msg="查询成功")
        
        # 获取菜单详情
        statement = select(Menu).where(Menu.id.in_(menu_ids))
        menus = session.exec(statement).all()
        
        # 构建菜单树
        tree = build_tree(menus)
        return respModel.ok_resp_tree(treeData=tree, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

