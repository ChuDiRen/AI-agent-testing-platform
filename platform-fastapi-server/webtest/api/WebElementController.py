"""
Web元素Controller - 按照ApiTest标准实现
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import Session

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel

from ..schemas.WebElementSchema import (
    WebElementCreate, WebElementUpdate, WebElementQuery, WebElementResponse,
    WebElementImport, WebElementExport, ModuleElementList, BatchDeleteRequest
)
from ..service.WebElementService import WebElementService

module_name = "WebElement"
module_route = APIRouter(prefix=f"/{module_name}", tags=["Web元素管理"])
logger = get_logger(__name__)


@module_route.post("/queryByPage", summary="分页查询Web元素", dependencies=[Depends(check_permission("webtest:element:query"))])
async def queryByPage(query: WebElementQuery, session: Session = Depends(get_session)):
    """分页查询Web元素"""
    try:
        elements, total = WebElementService.query_by_page(session, query)
        
        # 转换为响应格式
        element_responses = []
        for element in elements:
            element_dict = element.dict()
            element_responses.append(element_dict)
        
        return respModel.ok_resp_list(lst=element_responses, total=total)
    except Exception as e:
        logger.error(f"分页查询Web元素失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败:{e}")


@module_route.get("/queryById", summary="根据ID查询Web元素", dependencies=[Depends(check_permission("webtest:element:query"))])
async def queryById(id: int = Query(..., description="元素ID"), session: Session = Depends(get_session)):
    """根据ID查询Web元素"""
    try:
        element = WebElementService.get_by_id(session, id)
        if not element:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        
        # 转换为响应格式
        element_dict = element.dict()
        return respModel.ok_resp(obj=element_dict)
    except Exception as e:
        logger.error(f"根据ID查询Web元素失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败:{e}")


@module_route.post("/insert", summary="新增Web元素", dependencies=[Depends(check_permission("webtest:element:add"))])
async def insert(element_data: WebElementCreate, session: Session = Depends(get_session)):
    """新增Web元素"""
    try:
        element = WebElementService.create(session, element_data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": element.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增Web元素失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.put("/update", summary="更新Web元素", dependencies=[Depends(check_permission("webtest:element:edit"))])
async def update(element_data: WebElementUpdate, session: Session = Depends(get_session)):
    """更新Web元素"""
    try:
        success = WebElementService.update(session, element_data.id, element_data)
        if success:
            return respModel.ok_resp(msg="更新成功")
        else:
            return respModel.error_resp("元素不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新Web元素失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"更新失败，请联系管理员:{e}")


@module_route.delete("/delete", summary="删除Web元素", dependencies=[Depends(check_permission("webtest:element:delete"))])
async def delete(id: int = Query(..., description="元素ID"), session: Session = Depends(get_session)):
    """删除Web元素"""
    try:
        success = WebElementService.delete(session, id)
        if success:
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp("元素不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除Web元素失败: {e}", exc_info=True)
        return respModel.error_resp(f"删除失败，请联系管理员:{e}")


@module_route.delete("/batchDelete", summary="批量删除Web元素", dependencies=[Depends(check_permission("webtest:element:delete"))])
async def batchDelete(request: BatchDeleteRequest, session: Session = Depends(get_session)):
    """批量删除Web元素"""
    try:
        deleted_count = WebElementService.batch_delete(session, request.ids)
        if deleted_count > 0:
            return respModel.ok_resp(msg=f"成功删除{deleted_count}个元素")
        else:
            return respModel.error_resp("没有找到要删除的元素")
    except Exception as e:
        session.rollback()
        logger.error(f"批量删除Web元素失败: {e}", exc_info=True)
        return respModel.error_resp(f"批量删除失败，请联系管理员:{e}")


@module_route.post("/import", summary="导入Web元素", dependencies=[Depends(check_permission("webtest:element:import"))])
async def importElements(
    file: UploadFile = File(..., description="导入文件"),
    project_id: int = Query(..., description="项目ID"),
    session: Session = Depends(get_session)
):
    """导入Web元素"""
    try:
        import_data = WebElementImport(
            project_id=project_id,
            file_name=file.filename,
            file_content=file.file.read()
        )
        
        result = WebElementService.import_elements(session, import_data)
        return respModel.ok_resp(msg=f"导入成功，共{result.total}条记录，成功{result.success}条，失败{result.failed}条")
    except Exception as e:
        session.rollback()
        logger.error(f"导入Web元素失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"导入失败:{e}")


@module_route.post("/export", summary="导出Web元素", dependencies=[Depends(check_permission("webtest:element:export"))])
async def exportElements(
    request: WebElementExport,
    session: Session = Depends(get_session)
):
    """导出Web元素"""
    try:
        file_path = WebElementService.export_elements(session, request)
        
        if file_path and os.path.exists(file_path):
            return FileResponse(
                path=file_path,
                filename=f"web_elements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            return respModel.error_resp("导出失败，文件不存在")
    except Exception as e:
        logger.error(f"导出Web元素失败: {e}", exc_info=True)
        return respModel.error_resp(f"导出失败:{e}")


@module_route.get("/queryByModule", summary="按模块查询Web元素", dependencies=[Depends(check_permission("webtest:element:query"))])
async def queryByModule(
    module: str = Query(..., description="模块名称"),
    project_id: int = Query(None, description="项目ID"),
    session: Session = Depends(get_session)
):
    """按模块查询Web元素"""
    try:
        elements = WebElementService.query_by_module(session, module, project_id)
        
        # 转换为响应格式
        element_responses = []
        for element in elements:
            element_dict = element.dict()
            element_responses.append(element_dict)
        
        return respModel.ok_resp_list(lst=element_responses, total=len(element_responses))
    except Exception as e:
        logger.error(f"按模块查询Web元素失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败:{e}")
