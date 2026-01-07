"""
Web关键字Controller - 按照ApiTest标准实现
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File
from sqlmodel import Session

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel

from ..schemas.WebKeywordSchema import (
    WebKeywordCreate, WebKeywordUpdate, WebKeywordQuery, WebKeywordResponse,
    WebKeywordGenerateRequest, WebKeywordGenerateResponse, WebKeywordImport,
    WebKeywordExport, WebKeywordTestRequest, WebKeywordTestResponse
)
from ..service.WebKeywordService import WebKeywordService

module_name = "WebKeyword"
module_route = APIRouter(prefix=f"/{module_name}", tags=["Web关键字管理"])
logger = get_logger(__name__)


@module_route.post("/queryByPage", summary="分页查询Web关键字", dependencies=[Depends(check_permission("webtest:keyword:query"))])
async def queryByPage(query: WebKeywordQuery, session: Session = Depends(get_session)):
    """分页查询Web关键字"""
    try:
        keywords, total = WebKeywordService.query_by_page(session, query)
        
        # 转换为响应格式
        keyword_responses = []
        for keyword in keywords:
            keyword_dict = keyword.dict()
            keyword_responses.append(keyword_dict)
        
        return respModel.ok_resp_list(lst=keyword_responses, total=total)
    except Exception as e:
        logger.error(f"分页查询Web关键字失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败:{e}")


@module_route.get("/queryById", summary="根据ID查询Web关键字", dependencies=[Depends(check_permission("webtest:keyword:query"))])
async def queryById(id: int = Query(..., description="关键字ID"), session: Session = Depends(get_session)):
    """根据ID查询Web关键字"""
    try:
        keyword = WebKeywordService.get_keyword_by_id(session, id)
        if not keyword:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        
        # 转换为响应格式
        keyword_dict = keyword.dict()
        return respModel.ok_resp(obj=keyword_dict)
    except Exception as e:
        logger.error(f"根据ID查询Web关键字失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败:{e}")


@module_route.post("/insert", summary="新增Web关键字", dependencies=[Depends(check_permission("webtest:keyword:add"))])
async def insert(keyword_data: WebKeywordCreate, session: Session = Depends(get_session)):
    """新增Web关键字"""
    try:
        keyword = WebKeywordService.create_keyword(session, keyword_data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": keyword.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增Web关键字失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.put("/update", summary="更新Web关键字", dependencies=[Depends(check_permission("webtest:keyword:edit"))])
async def update(keyword_data: WebKeywordUpdate, session: Session = Depends(get_session)):
    """更新Web关键字"""
    try:
        success = WebKeywordService.update_keyword(session, keyword_data.id, keyword_data)
        if success:
            return respModel.ok_resp(msg="更新成功")
        else:
            return respModel.error_resp("关键字不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新Web关键字失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"更新失败，请联系管理员:{e}")


@module_route.delete("/delete", summary="删除Web关键字", dependencies=[Depends(check_permission("webtest:keyword:delete"))])
async def delete(id: int = Query(..., description="关键字ID"), session: Session = Depends(get_session)):
    """删除Web关键字"""
    try:
        success = WebKeywordService.delete_keyword(session, id)
        if success:
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp("关键字不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除Web关键字失败: {e}", exc_info=True)
        return respModel.error_resp(f"删除失败，请联系管理员:{e}")


@module_route.delete("/batchDelete", summary="批量删除Web关键字", dependencies=[Depends(check_permission("webtest:keyword:delete"))])
async def batchDelete(ids: List[int], session: Session = Depends(get_session)):
    """批量删除Web关键字"""
    try:
        deleted_count = WebKeywordService.batch_delete_keywords(session, ids)
        if deleted_count > 0:
            return respModel.ok_resp(msg=f"成功删除{deleted_count}个关键字")
        else:
            return respModel.error_resp("没有找到要删除的关键字")
    except Exception as e:
        session.rollback()
        logger.error(f"批量删除Web关键字失败: {e}", exc_info=True)
        return respModel.error_resp(f"批量删除失败，请联系管理员:{e}")


@module_route.post("/generateFile", summary="生成关键字文件", dependencies=[Depends(check_permission("webtest:keyword:generate"))])
async def generateFile(request: WebKeywordGenerateRequest, session: Session = Depends(get_session)):
    """生成关键字文件"""
    try:
        result = WebKeywordService.generate_keyword_file(session, request)
        return respModel.ok_resp(msg="生成成功", obj=result)
    except Exception as e:
        logger.error(f"生成关键字文件失败: {e}", exc_info=True)
        return respModel.error_resp(f"生成失败:{e}")


@module_route.post("/import", summary="导入Web关键字", dependencies=[Depends(check_permission("webtest:keyword:import"))])
async def importKeywords(
    file: UploadFile = File(..., description="导入文件"),
    session: Session = Depends(get_session)
):
    """导入Web关键字"""
    try:
        import_data = WebKeywordImport(
            overwrite=False,
            keywords=[]  # 需要从文件中解析关键字
        )
        
        success_count, error_count = WebKeywordService.import_keywords(session, import_data.keywords, import_data.overwrite)
        return respModel.ok_resp(msg=f"导入成功，共{success_count + error_count}条记录，成功{success_count}条，失败{error_count}条")
    except Exception as e:
        session.rollback()
        logger.error(f"导入Web关键字失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"导入失败:{e}")


@module_route.post("/export", summary="导出Web关键字", dependencies=[Depends(check_permission("webtest:keyword:export"))])
async def exportKeywords(ids: List[int], session: Session = Depends(get_session)):
    """导出Web关键字"""
    try:
        export_request = WebKeywordExport(ids=ids)
        keywords = WebKeywordService.export_keywords(session, export_request)
        
        if keywords:
            # 简单返回关键字列表，不生成文件
            return respModel.ok_resp_list(lst=keywords, total=len(keywords))
        else:
            return respModel.error_resp("导出失败，没有找到数据")
    except Exception as e:
        logger.error(f"导出Web关键字失败: {e}", exc_info=True)
        return respModel.error_resp(f"导出失败:{e}")
