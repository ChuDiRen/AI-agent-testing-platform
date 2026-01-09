from app.database.database import get_session
from app.dependencies.dependencies import check_permission
from app.logger.logger import get_logger
from app.responses.resp_model import respModel
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.RoleSchema import RoleQuery, RoleCreate, RoleUpdate, RoleMenuAssign
from app.services.RoleService import RoleService

logger = get_logger(__name__)

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.post("/queryByPage", summary="分页查询角色", dependencies=[Depends(check_permission("system:role:query"))])
async def queryByPage(query: RoleQuery, session: Session = Depends(get_session)):
    """分页查询角色"""
    try:
        datas, total = RoleService.query_by_page(session, query)
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.get("/queryById", summary="根据ID查询角色", dependencies=[Depends(check_permission("system:role:query"))])
async def queryById(id: int, session: Session = Depends(get_session)):
    """根据ID查询角色"""
    try:
        obj = RoleService.query_by_id(session, id)
        if obj:
            return respModel.ok_resp(obj=obj)
        else:
            return respModel.error_resp("数据不存在")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.post("/insert", summary="新增角色", dependencies=[Depends(check_permission("system:role:add"))])
async def insert(request: RoleCreate, session: Session = Depends(get_session)):
    """新增角色"""
    try:
        if RoleService.check_name_exists(session, request.role_name):
            return respModel.error_resp("角色名称已存在")
        
        obj = RoleService.create(session, request)
        return respModel.ok_resp(obj=obj, msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.put("/update", summary="更新角色", dependencies=[Depends(check_permission("system:role:edit"))])
async def update(request: RoleUpdate, session: Session = Depends(get_session)):
    """更新角色"""
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


@router.delete("/delete", summary="删除角色", dependencies=[Depends(check_permission("system:role:delete"))])
async def delete(id: int, session: Session = Depends(get_session)):
    """删除角色"""
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


@router.post("/assignMenus", summary="为角色分配菜单权限", dependencies=[Depends(check_permission("system:role:assign"))])
async def assignMenus(request: RoleMenuAssign, session: Session = Depends(get_session)):
    """为角色分配菜单权限"""
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


@router.get("/menus/{role_id}", summary="获取角色的菜单权限", dependencies=[Depends(check_permission("system:role:query"))])
async def getMenus(role_id: int, session: Session = Depends(get_session)):
    """获取角色的菜单权限"""
    try:
        menu_ids = RoleService.get_menus(session, role_id)
        return respModel.ok_resp_simple(lst=menu_ids, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
