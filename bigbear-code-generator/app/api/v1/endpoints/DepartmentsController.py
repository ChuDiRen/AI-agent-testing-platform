from app.database.database import get_session
from app.dependencies.dependencies import check_permission
from app.logger.logger import get_logger
from app.responses.resp_model import respModel
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.DeptSchema import DeptCreate, DeptUpdate
from app.services.DeptService import DeptService

logger = get_logger(__name__)

router = APIRouter(prefix="/departments", tags=["部门管理"])


@router.get("/tree", summary="获取部门树", dependencies=[Depends(check_permission("system:dept:query"))])
async def getTree(session: Session = Depends(get_session)):
    """获取部门树"""
    try:
        tree = DeptService.get_tree(session)
        return respModel.ok_resp_tree(treeData=tree, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.get("/queryById", summary="根据ID查询部门", dependencies=[Depends(check_permission("system:dept:query"))])
async def queryById(id: int, session: Session = Depends(get_session)):
    """根据ID查询部门"""
    try:
        obj = DeptService.query_by_id(session, id)
        return respModel.ok_resp(obj=obj) if obj else respModel.error_resp("数据不存在")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.post("/insert", summary="新增部门", dependencies=[Depends(check_permission("system:dept:add"))])
async def insert(request: DeptCreate, session: Session = Depends(get_session)):
    """新增部门"""
    try:
        obj = DeptService.create(session, request)
        return respModel.ok_resp(obj=obj, msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.put("/update", summary="更新部门", dependencies=[Depends(check_permission("system:dept:edit"))])
async def update(request: DeptUpdate, session: Session = Depends(get_session)):
    """更新部门"""
    try:
        obj = DeptService.update(session, request)
        if obj:
            return respModel.ok_resp(obj=obj, msg="更新成功")
        else:
            return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@router.delete("/delete", summary="删除部门", dependencies=[Depends(check_permission("system:dept:delete"))])
async def delete(id: int, session: Session = Depends(get_session)):
    """删除部门"""
    try:
        error = DeptService.delete(session, id)
        if error:
            return respModel.error_resp(error)
        return respModel.ok_resp_text(msg="删除成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
