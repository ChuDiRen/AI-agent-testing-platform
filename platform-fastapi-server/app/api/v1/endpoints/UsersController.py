from app.database.database import get_session
from app.dependencies.dependencies import check_permission, get_current_user
from app.logger.logger import get_logger
from app.responses.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.schemas.UserSchema import (
    UserQuery, UserCreate, UserUpdate, UserRoleAssign, 
    UserStatusUpdate, BatchUserStatusUpdate, BatchUserDelete
)
from app.services.UserService import UserService

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/queryByPage", summary="分页查询用户", dependencies=[Depends(check_permission("system:user:query"))])
async def queryByPage(query: UserQuery, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    """分页查询用户（应用数据权限过滤）"""
    try:
        current_user_id = current_user.get("id")
        datas, total = UserService.query_by_page(session, query, current_user_id)
        logger.info(f"分页查询用户成功，共{total}条记录")
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"分页查询用户失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.get("/queryById", summary="根据ID查询用户", dependencies=[Depends(check_permission("system:user:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询用户"""
    try:
        data = UserService.query_by_id(session, id)
        if data:
            logger.info(f"查询用户成功: ID={id}")
            return respModel.ok_resp(obj=data)
        else:
            logger.warning(f"查询用户不存在: ID={id}")
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"查询用户失败: ID={id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.post("/insert", summary="新增用户", dependencies=[Depends(check_permission("system:user:add"))])
async def insert(user: UserCreate, session: Session = Depends(get_session)):
    """新增用户"""
    try:
        data = UserService.create(session, user)
        logger.info(f"新增用户成功: ID={data.id}, 用户名={data.username}")
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增用户失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")


@router.put("/update", summary="更新用户", dependencies=[Depends(check_permission("system:user:edit"))])
async def update(user: UserUpdate, session: Session = Depends(get_session)):
    """更新用户"""
    try:
        db_user = UserService.update(session, user)
        if db_user:
            logger.info(f"更新用户成功: ID={user.id}")
            return respModel.ok_resp(msg="修改成功")
        else:
            logger.warning(f"更新用户失败，用户不存在: ID={user.id}")
            return respModel.error_resp(msg="用户不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新用户失败: ID={user.id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@router.delete("/delete", summary="删除用户", dependencies=[Depends(check_permission("system:user:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除用户"""
    try:
        success = UserService.delete(session, id)
        if success:
            logger.info(f"删除用户成功: ID={id}")
            return respModel.ok_resp(msg="删除成功")
        else:
            logger.warning(f"删除用户失败，用户不存在: ID={id}")
            return respModel.error_resp(msg="用户不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除用户失败: ID={id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


@router.post("/assignRoles", summary="为用户分配角色", dependencies=[Depends(check_permission("system:user:edit"))])
async def assignRoles(request: UserRoleAssign, session: Session = Depends(get_session)):
    """为用户分配角色"""
    try:
        success, message = UserService.assign_roles(session, request)
        if success:
            return respModel.ok_resp_text(msg=message)
        else:
            return respModel.error_resp(message)
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.get("/roles/{user_id}", summary="获取用户的角色", dependencies=[Depends(check_permission("system:user:query"))])
async def getRoles(user_id: int, session: Session = Depends(get_session)):
    """获取用户的角色"""
    try:
        role_ids = UserService.get_roles(session, user_id)
        return respModel.ok_resp_simple(lst=role_ids, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.put("/updateStatus", summary="更新用户状态（锁定/启用）", dependencies=[Depends(check_permission("system:user:edit"))])
async def updateStatus(request: UserStatusUpdate, session: Session = Depends(get_session)):
    """更新用户状态（锁定/启用）"""
    try:
        status_text = UserService.update_status(session, request)
        if status_text:
            return respModel.ok_resp_text(msg=f"用户{status_text}成功")
        else:
            return respModel.error_resp("用户不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.post("/batchUpdateStatus", summary="批量更新用户状态", dependencies=[Depends(check_permission("system:user:edit"))])
async def batchUpdateStatus(request: BatchUserStatusUpdate, session: Session = Depends(get_session)):
    """批量更新用户状态"""
    try:
        count = UserService.batch_update_status(session, request)
        status_text = "启用" if request.status == "1" else "锁定"
        return respModel.ok_resp_text(msg=f"批量{status_text}成功，共{count}条记录")
    except Exception as e:
        session.rollback()
        logger.error(f"批量更新状态失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.post("/batchDelete", summary="批量删除用户", dependencies=[Depends(check_permission("system:user:delete"))])
async def batchDelete(request: BatchUserDelete, session: Session = Depends(get_session)):
    """批量删除用户"""
    try:
        count = UserService.batch_delete(session, request)
        return respModel.ok_resp_text(msg=f"批量删除成功，共{count}条记录")
    except Exception as e:
        session.rollback()
        logger.error(f"批量删除失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
