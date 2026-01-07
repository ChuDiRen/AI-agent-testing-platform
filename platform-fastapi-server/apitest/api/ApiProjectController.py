"""
API项目Controller - 已重构为使用静态Service层
"""
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..service.ApiProjectService import ApiProjectService
from ..schemas.ApiProjectSchema import ApiProjectQuery, ApiProjectCreate, ApiProjectUpdate, BatchDeleteRequest

module_name = "ApiProject"
module_route = APIRouter(prefix=f"/{module_name}", tags=["API项目管理"])
logger = get_logger(__name__)

@module_route.post("/queryByPage", summary="分页查询API项目", dependencies=[Depends(check_permission("apitest:project:query"))])
async def queryByPage(query: ApiProjectQuery, session: Session = Depends(get_session)):
    """分页查询API项目"""
    try:
        datas, total = ApiProjectService.query_by_page(session, query)
        logger.info(f"分页查询API项目成功，共{total}条记录")
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"分页查询API项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询API项目", dependencies=[Depends(check_permission("apitest:project:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询API项目"""
    try:
        data = ApiProjectService.query_by_id(session, id)
        if data:
            logger.info(f"查询API项目成功: ID={id}")
            return respModel.ok_resp(obj=data)
        else:
            logger.warning(f"查询API项目不存在: ID={id}")
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"根据ID查询API项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增API项目", dependencies=[Depends(check_permission("apitest:project:add"))])
async def insert(project: ApiProjectCreate, session: Session = Depends(get_session)):
    """新增API项目"""
    try:
        data = ApiProjectService.create(session, project)
        logger.info(f"新增API项目成功: ID={data.id}, 名称={data.project_name}")
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增API项目失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", summary="更新API项目", dependencies=[Depends(check_permission("apitest:project:edit"))])
async def update(project: ApiProjectUpdate, session: Session = Depends(get_session)):
    """更新API项目"""
    try:
        db_project = ApiProjectService.update(session, project)
        if db_project:
            logger.info(f"更新API项目成功: ID={project.id}")
            return respModel.ok_resp(msg="修改成功")
        else:
            logger.warning(f"更新API项目失败，项目不存在: ID={project.id}")
            return respModel.error_resp(msg="项目不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新API项目失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete", summary="删除项目", dependencies=[Depends(check_permission("apitest:project:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除API项目"""
    try:
        service = ApiProjectService(session)
        if service.delete(id):
            logger.info(f"删除API项目成功: ID={id}")
            return respModel.ok_resp(msg="删除成功")
        else:
            logger.warning(f"删除API项目失败，项目不存在: ID={id}")
            return respModel.error_resp(msg="项目不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除API项目失败: ID={id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

@module_route.delete("/batchDelete", summary="批量删除项目", dependencies=[Depends(check_permission("apitest:project:delete"))])
async def batch_delete(request: BatchDeleteRequest, session: Session = Depends(get_session)):
    try:
        deleted_count = ApiProjectService.batch_delete(session, request.ids)
        if deleted_count > 0:
            return respModel.ok_resp(msg=f"成功删除{deleted_count}个项目")
        else:
            return respModel.error_resp(msg="没有找到要删除的项目")
    except Exception as e:
        session.rollback()
        logger.error(f"批量删除失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"批量删除失败：{e}")

@module_route.get("/queryAll", summary="查询所有API项目", dependencies=[Depends(check_permission("apitest:project:query"))])
async def queryAll(session: Session = Depends(get_session)):
    try:
        datas = ApiProjectService.query_all(session)
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        logger.error(f"查询所有API项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
