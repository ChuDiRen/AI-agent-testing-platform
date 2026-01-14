from app.database.database import get_session
from app.dependencies.dependencies import check_permission, get_current_user
from app.logger.logger import get_logger
from app.responses.resp_model import respModel
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.MenuSchema import MenuCreate, MenuUpdate
from app.services.MenuService import MenuService

logger = get_logger(__name__)

router = APIRouter(prefix="/menus", tags=["菜单管理"])


@router.get("/tree", summary="获取菜单树（仅用于菜单配置管理）", dependencies=[Depends(check_permission("system:menu:query"))])
async def getTree(session: Session = Depends(get_session)):
    """
    获取菜单树
    注意: 前端已使用静态菜单配置，此接口仅用于后台菜单管理功能
    """
    try:
        tree = MenuService.get_tree(session, logger=logger)
        return respModel.ok_resp_tree(treeData=tree, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.get("/queryById", summary="根据ID查询菜单", dependencies=[Depends(check_permission("system:menu:query"))])
async def queryById(id: int, session: Session = Depends(get_session)):
    """根据ID查询菜单"""
    try:
        obj = MenuService.query_by_id(session, id)
        return respModel.ok_resp(obj=obj) if obj else respModel.error_resp("数据不存在")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.post("/insert", summary="新增菜单", dependencies=[Depends(check_permission("system:menu:add"))])
async def insert(request: MenuCreate, session: Session = Depends(get_session)):
    """新增菜单"""
    try:
        obj = MenuService.create(session, request)
        return respModel.ok_resp(obj=obj, msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.put("/update", summary="更新菜单", dependencies=[Depends(check_permission("system:menu:edit"))])
async def update(request: MenuUpdate, session: Session = Depends(get_session)):
    """更新菜单"""
    try:
        obj = MenuService.update(session, request)
        if obj:
            return respModel.ok_resp(obj=obj, msg="更新成功")
        else:
            return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.delete("/delete", summary="删除菜单", dependencies=[Depends(check_permission("system:menu:delete"))])
async def delete(id: int, session: Session = Depends(get_session)):
    """删除菜单"""
    try:
        error = MenuService.delete(session, id)
        if error:
            return respModel.error_resp(error)
        return respModel.ok_resp_text(msg="删除成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.get("/user/menus", summary="获取当前用户的菜单树（用于前端动态菜单）")
async def get_user_menus(current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """获取当前登录用户有权限的菜单树（用于前端动态菜单）"""
    try:
        # 从 current_user 中获取角色ID列表
        user_roles = current_user.get("user_roles", [])
        role_ids = [ur["role_id"] for ur in user_roles] if user_roles else []
        
        # 如果没有角色，返回空菜单
        if not role_ids:
            return respModel.ok_resp_tree(treeData=[], msg="查询成功")
        
        # 获取用户菜单树
        tree = MenuService.get_user_menu_tree(session, role_ids, logger=logger)
        return respModel.ok_resp_tree(treeData=tree, msg="查询成功")
    except Exception as e:
        logger.error(f"获取用户菜单失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取用户菜单失败: {e}")


