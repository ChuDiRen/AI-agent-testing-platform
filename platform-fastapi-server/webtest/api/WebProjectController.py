"""
Web项目Controller - 按照ApiTest标准实现
"""
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session

from ..schemas.WebProjectSchema import (
    WebProjectCreate, WebProjectUpdate, WebProjectQuery, 
    WebProjectResponse, BatchDeleteRequest
)
from ..service.WebProjectService import WebProjectService

module_name = "WebProject"
module_route = APIRouter(prefix=f"/{module_name}", tags=["Web项目管理"])
logger = get_logger(__name__)


@module_route.post("/queryByPage", summary="分页查询Web项目", dependencies=[Depends(check_permission("webtest:project:query"))])
async def queryByPage(query: WebProjectQuery, session: Session = Depends(get_session)):
    """分页查询Web项目"""
    try:
        projects, total = WebProjectService.query_by_page(session, query)
        
        # 转换为响应格式
        project_responses = []
        for project in projects:
            project_dict = project.dict()
            project_responses.append(project_dict)
        
        return respModel.ok_resp_list(lst=project_responses, total=total)
    except Exception as e:
        logger.error(f"分页查询Web项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败:{e}")


@module_route.get("/queryAll", summary="查询所有Web项目", dependencies=[Depends(check_permission("webtest:project:query"))])
async def queryAll(session: Session = Depends(get_session)):
    """查询所有Web项目"""
    try:
        projects = WebProjectService.query_all(session)
        
        # 转换为响应格式
        project_responses = []
        for project in projects:
            project_dict = project.dict()
            project_responses.append(project_dict)
        
        return respModel.ok_resp_list(lst=project_responses, total=len(project_responses))
    except Exception as e:
        logger.error(f"查询所有Web项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败:{e}")


@module_route.get("/queryById", summary="根据ID查询Web项目", dependencies=[Depends(check_permission("webtest:project:query"))])
async def queryById(id: int = Query(..., description="项目ID"), session: Session = Depends(get_session)):
    """根据ID查询Web项目"""
    try:
        project = WebProjectService.get_by_id(session, id)
        if not project:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        
        # 转换为响应格式
        project_dict = project.dict()
        return respModel.ok_resp(obj=project_dict)
    except Exception as e:
        logger.error(f"根据ID查询Web项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败:{e}")


@module_route.post("/insert", summary="新增Web项目", dependencies=[Depends(check_permission("webtest:project:add"))])
async def insert(project_data: WebProjectCreate, session: Session = Depends(get_session)):
    """新增Web项目"""
    try:
        project = WebProjectService.create(session, project_data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": project.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增Web项目失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.put("/update", summary="更新Web项目", dependencies=[Depends(check_permission("webtest:project:edit"))])
async def update(project_data: WebProjectUpdate, session: Session = Depends(get_session)):
    """更新Web项目"""
    try:
        success = WebProjectService.update(session, project_data.id, project_data)
        if success:
            return respModel.ok_resp(msg="更新成功")
        else:
            return respModel.error_resp("项目不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新Web项目失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"更新失败，请联系管理员:{e}")


@module_route.delete("/delete", summary="删除Web项目", dependencies=[Depends(check_permission("webtest:project:delete"))])
async def delete(id: int = Query(..., description="项目ID"), session: Session = Depends(get_session)):
    """删除Web项目"""
    try:
        success = WebProjectService.delete(session, id)
        if success:
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp("项目不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除Web项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"删除失败，请联系管理员:{e}")


@module_route.delete("/batchDelete", summary="批量删除Web项目", dependencies=[Depends(check_permission("webtest:project:delete"))])
async def batchDelete(request: BatchDeleteRequest, session: Session = Depends(get_session)):
    """批量删除Web项目"""
    try:
        deleted_count = WebProjectService.batch_delete(session, request.ids)
        if deleted_count > 0:
            return respModel.ok_resp(msg=f"成功删除{deleted_count}个项目")
        else:
            return respModel.error_resp("没有找到要删除的项目")
    except Exception as e:
        session.rollback()
        logger.error(f"批量删除Web项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"批量删除失败，请联系管理员:{e}")
