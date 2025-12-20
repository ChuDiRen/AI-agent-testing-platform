from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..service.api_project_service import ApiProjectService
from ..schemas.api_project_schema import ApiProjectQuery, ApiProjectCreate, ApiProjectUpdate

module_name = "ApiProject"
module_route = APIRouter(prefix=f"/{module_name}", tags=["API项目管理"])
logger = get_logger(__name__)

@module_route.post("/queryByPage", summary="分页查询API项目", dependencies=[Depends(check_permission("apitest:project:query"))])
async def queryByPage(query: ApiProjectQuery, session: Session = Depends(get_session)):
    try:
        service = ApiProjectService(session)
        datas, total = service.query_by_page(
            page=query.page,
            page_size=query.pageSize,
            project_name=query.project_name
        )
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"分页查询API项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询API项目", dependencies=[Depends(check_permission("apitest:project:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        service = ApiProjectService(session)
        data = service.get_by_id(id)
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"根据ID查询API项目失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增API项目", dependencies=[Depends(check_permission("apitest:project:add"))])
async def insert(project: ApiProjectCreate, session: Session = Depends(get_session)):
    try:
        service = ApiProjectService(session)
        data = service.create(
            project_name=project.project_name,
            project_desc=project.project_desc
        )
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", summary="更新API项目", dependencies=[Depends(check_permission("apitest:project:edit"))])
async def update(project: ApiProjectUpdate, session: Session = Depends(get_session)):
    try:
        service = ApiProjectService(session)
        update_data = project.model_dump(exclude_unset=True, exclude={'id'})
        updated = service.update(project.id, update_data)
        if updated:
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="项目不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新API项目失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete", summary="删除API项目", dependencies=[Depends(check_permission("apitest:project:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        service = ApiProjectService(session)
        if service.delete(id):
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="项目不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除API项目失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

@module_route.get("/queryAll", summary="查询所有API项目", dependencies=[Depends(check_permission("apitest:project:query"))])
async def queryAll(session: Session = Depends(get_session)):
    service = ApiProjectService(session)
    datas = service.query_all()
    return respModel.ok_resp_list(lst=datas, msg="查询成功")
