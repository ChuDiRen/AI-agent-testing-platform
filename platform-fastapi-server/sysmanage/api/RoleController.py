from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..schemas.role_schema import RoleQuery, RoleCreate, RoleUpdate, RoleMenuAssign
from ..service.role_service import RoleService

module_name = "role"
module_route = APIRouter(prefix=f"/{module_name}", tags=["角色管理"])
logger = get_logger(__name__)

@module_route.post("/queryByPage", summary="分页查询角色", dependencies=[Depends(check_permission("system:role:query"))]) # 分页查询角色
async def queryByPage(query: RoleQuery, session: Session = Depends(get_session)):
    try:
        datas, total = RoleService.query_by_page(session, query)
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询角色", dependencies=[Depends(check_permission("system:role:query"))]) # 根据ID查询角色
async def queryById(id: int, session: Session = Depends(get_session)):
    try:
        obj = RoleService.query_by_id(session, id)
        if obj:
            return respModel.ok_resp(obj=obj)
        else:
            return respModel.error_resp("数据不存在")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增角色", dependencies=[Depends(check_permission("system:role:add"))]) # 新增角色
async def insert(request: RoleCreate, session: Session = Depends(get_session)):
    try:
        if RoleService.check_name_exists(session, request.role_name):
            return respModel.error_resp("角色名称已存在")
        
        obj = RoleService.create(session, request)
        return respModel.ok_resp(obj=obj, msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/update", summary="更新角色", dependencies=[Depends(check_permission("system:role:edit"))]) # 更新角色
async def update(request: RoleUpdate, session: Session = Depends(get_session)):
    try:
        obj = RoleService.update(session, request)
        if obj:
            return respModel.ok_resp(obj=obj, msg="更新成功")
        else:
            return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete", summary="删除角色", dependencies=[Depends(check_permission("system:role:delete"))]) # 删除角色
async def delete(id: int, session: Session = Depends(get_session)):
    try:
        success = RoleService.delete(session, id)
        if success:
            return respModel.ok_resp_text(msg="删除成功")
        else:
            return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/assignMenus", summary="为角色分配菜单权限", dependencies=[Depends(check_permission("system:role:edit"))]) # 为角色分配菜单权限
async def assignMenus(request: RoleMenuAssign, session: Session = Depends(get_session)):
    try:
        success = RoleService.assign_menus(session, request)
        if success:
            return respModel.ok_resp_text(msg="分配权限成功")
        else:
            return respModel.error_resp("角色不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/menus/{role_id}", summary="获取角色的菜单权限", dependencies=[Depends(check_permission("system:role:query"))]) # 获取角色的菜单权限
async def getMenus(role_id: int, session: Session = Depends(get_session)):
    try:
        menu_ids = RoleService.get_menus(session, role_id)
        return respModel.ok_resp_simple(lst=menu_ids, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

