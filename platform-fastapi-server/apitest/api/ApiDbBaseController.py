from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..service.ApiDbbaseService import ApiDbbaseService
from ..schemas.ApiDbbaseSchema import ApiDbBaseQuery, ApiDbBaseCreate, ApiDbBaseUpdate

module_name = "ApiDbBase"
module_route = APIRouter(prefix=f"/{module_name}", tags=["API数据库配置管理"])
logger = get_logger(__name__)

@module_route.post("/queryByPage", summary="分页查询数据库配置", dependencies=[Depends(check_permission("apitest:database:query"))])
async def queryByPage(query: ApiDbBaseQuery, session: Session = Depends(get_session)):
    try:
        service = ApiDbbaseService(session)
        datas, total = service.query_by_page(
            page=query.page,
            page_size=query.pageSize,
            project_id=query.project_id,
            connect_name=query.connect_name
        )
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询数据库配置", dependencies=[Depends(check_permission("apitest:database:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        service = ApiDbbaseService(session)
        data = service.get_by_id(id)
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增数据库配置", dependencies=[Depends(check_permission("apitest:database:add"))])
async def insert(db_config: ApiDbBaseCreate, session: Session = Depends(get_session)):
    try:
        service = ApiDbbaseService(session)
        data = service.create(
            project_id=db_config.project_id,
            name=db_config.name,
            ref_name=db_config.ref_name,
            db_type=db_config.db_type,
            host=db_config.host,
            port=db_config.port,
            username=db_config.username,
            password=db_config.password,
            database=db_config.database,
            is_enabled=db_config.is_enabled
        )
        if data:
            return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
        else:
            return respModel.error_resp(msg="数据库已存在重复的数据库引用名，请重新输入")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", summary="更新数据库配置", dependencies=[Depends(check_permission("apitest:database:edit"))])
async def update(db_config: ApiDbBaseUpdate, session: Session = Depends(get_session)):
    try:
        service = ApiDbbaseService(session)
        update_data = db_config.model_dump(exclude_unset=True, exclude={'id'})
        updated = service.update(db_config.id, update_data)
        if updated:
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="数据库配置不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete", summary="删除数据库配置", dependencies=[Depends(check_permission("apitest:database:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        service = ApiDbbaseService(session)
        if service.delete(id):
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="数据库配置不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

@module_route.put("/toggleEnabled", summary="启用/禁用数据库配置", dependencies=[Depends(check_permission("apitest:database:edit"))])
async def toggleEnabled(id: int = Query(...), is_enabled: str = Query(...), session: Session = Depends(get_session)):
    """启用或禁用数据库配置"""
    try:
        service = ApiDbbaseService(session)
        updated = service.toggle_enabled(id, is_enabled)
        if updated:
            status_text = "启用" if is_enabled == "1" else "禁用"
            return respModel.ok_resp(msg=f"已{status_text}该配置")
        else:
            return respModel.error_resp(msg="数据库配置不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"操作失败：{e}")

@module_route.get("/queryByProject", summary="根据项目ID查询数据库配置")
async def queryByProject(project_id: int = Query(...), session: Session = Depends(get_session)):
    """根据项目ID查询启用的数据库配置列表"""
    try:
        service = ApiDbbaseService(session)
        datas = service.query_by_project(project_id)
        return respModel.ok_resp_list(lst=datas, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")