from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from core.resp_model import respModel
from core.logger import get_logger


from ..model.role import Role
from ..model.role_menu import RoleMenu
from ..schemas.role_schema import RoleQuery, RoleCreate, RoleUpdate, RoleMenuAssign
from core.database import get_session
from core.time_utils import TimeFormatter
from datetime import datetime
from typing import List

module_name = "role"
module_model = Role
module_route = APIRouter(prefix=f"/{module_name}", tags=["角色管理"])
logger = get_logger(__name__)

@module_route.post("/queryByPage") # 分页查询角色
def queryByPage(query: RoleQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        
        # 模糊查询角色名称
        if query.role_name:
            statement = statement.where(module_model.role_name.like(f"%{query.role_name}%"))
        
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(module_model)
        if query.role_name:
            count_statement = count_statement.where(module_model.role_name.like(f"%{query.role_name}%"))
        total = len(session.exec(count_statement).all())
        
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById") # 根据ID查询角色
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

@module_route.post("/insert") # 新增角色
def insert(request: RoleCreate, session: Session = Depends(get_session)):
    try:
        # 检查角色名是否重复
        statement = select(module_model).where(module_model.role_name == request.role_name)
        existing = session.exec(statement).first()
        if existing:
            return respModel.error_resp("角色名称已存在")
        
        obj = module_model(**request.model_dump())
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return respModel.ok_resp(obj=obj, msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/update") # 更新角色
def update(request: RoleUpdate, session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, request.id)
        if not obj:
            return respModel.error_resp("数据不存在")
        
        # 更新字段
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

@module_route.delete("/delete") # 删除角色
def delete(id: int, session: Session = Depends(get_session)):
    try:
        obj = session.get(module_model, id)
        if not obj:
            return respModel.error_resp("数据不存在")
        
        # 删除角色关联的菜单权限
        statement = select(RoleMenu).where(RoleMenu.role_id == id)
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

@module_route.post("/assignMenus") # 为角色分配菜单权限
def assignMenus(request: RoleMenuAssign, session: Session = Depends(get_session)):
    try:
        # 检查角色是否存在
        role = session.get(Role, request.id)
        if not role:
            return respModel.error_resp("角色不存在")
        
        # 删除该角色原有的菜单权限
        statement = select(RoleMenu).where(RoleMenu.role_id == request.id)
        old_role_menus = session.exec(statement).all()
        for rm in old_role_menus:
            session.delete(rm)
        
        # 添加新的菜单权限
        for menu_id in request.menu_ids:
            role_menu = RoleMenu(role_id=request.id, menu_id=menu_id)
            session.add(role_menu)
        
        session.commit()
        return respModel.ok_resp_text(msg="分配权限成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/menus/{role_id}") # 获取角色的菜单权限
def getMenus(role_id: int, session: Session = Depends(get_session)):
    try:
        statement = select(RoleMenu).where(RoleMenu.role_id == role_id)
        role_menus = session.exec(statement).all()
        menu_ids = [rm.menu_id for rm in role_menus]
        return respModel.ok_resp_simple(lst=menu_ids, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

