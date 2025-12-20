"""
请求历史Controller
提供请求历史的查询、收藏、回放等功能
"""
from datetime import datetime, timedelta

from apitest.service.api_request_history_service import RequestHistoryService
from apitest.model.ApiRequestHistoryModel import ApiRequestHistory
from apitest.schemas.api_request_history_schema import (
    ApiRequestHistoryQuery,
    ApiRequestHistoryCreate,
    ApiRequestHistoryBatchDelete,
    ApiRequestHistoryClearParams
)
from core.database import get_session
from core.dependencies import check_permission
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

module_name = "ApiRequestHistory"
module_model = ApiRequestHistory
module_route = APIRouter(prefix=f"/{module_name}", tags=["请求历史管理"])


@module_route.post("/queryByPage", summary="分页查询请求历史",
                   dependencies=[Depends(check_permission("apitest:history:query"))])
async def query_by_page(query: ApiRequestHistoryQuery, session: Session = Depends(get_session)):
    """分页查询请求历史"""
    service = RequestHistoryService(session)
    datas, total = service.query_by_page(
        page=query.page,
        page_size=query.pageSize,
        project_id=query.project_id,
        api_id=query.api_id,
        request_method=query.request_method,
        request_url=query.request_url,
        is_success=query.is_success,
        is_favorite=query.is_favorite,
        start_time=query.start_time,
        end_time=query.end_time
    )
    return respModel.ok_resp_list(lst=datas, total=total)


@module_route.get("/queryById", summary="根据ID查询历史",
                  dependencies=[Depends(check_permission("apitest:history:query"))])
async def query_by_id(id: int = Query(..., description="历史ID"),
                      session: Session = Depends(get_session)):
    """根据ID查询历史详情"""
    service = RequestHistoryService(session)
    data = service.get_by_id(id)
    if not data:
        return respModel.error_resp(msg="记录不存在")
    return respModel.ok_resp(obj=data)


@module_route.get("/queryRecent", summary="查询最近的请求",
                  dependencies=[Depends(check_permission("apitest:history:query"))])
async def query_recent(project_id: int = Query(..., description="项目ID"),
                       limit: int = Query(10, description="数量限制"),
                       session: Session = Depends(get_session)):
    """查询最近的请求历史"""
    service = RequestHistoryService(session)
    datas = service.query_recent(project_id, limit)
    return respModel.ok_resp_list(lst=datas, total=len(datas))


@module_route.get("/queryFavorites", summary="查询收藏的请求",
                  dependencies=[Depends(check_permission("apitest:history:query"))])
async def query_favorites(project_id: int = Query(..., description="项目ID"),
                          session: Session = Depends(get_session)):
    """查询收藏的请求历史"""
    service = RequestHistoryService(session)
    datas = service.query_favorites(project_id)
    return respModel.ok_resp_list(lst=datas, total=len(datas))


@module_route.post("/insert", summary="新增历史记录",
                   dependencies=[Depends(check_permission("apitest:history:add"))])
async def insert(history: ApiRequestHistoryCreate, session: Session = Depends(get_session)):
    """新增请求历史记录"""
    service = RequestHistoryService(session)
    data = service.create(**history.model_dump())
    return respModel.ok_resp(msg="记录成功", dic_t={"id": data.id})


@module_route.delete("/delete", summary="删除历史记录",
                     dependencies=[Depends(check_permission("apitest:history:delete"))])
async def delete(id: int = Query(..., description="历史ID"),
                 session: Session = Depends(get_session)):
    """删除历史记录"""
    service = RequestHistoryService(session)
    if not service.delete(id):
        return respModel.error_resp(msg="记录不存在")
    return respModel.ok_resp(msg="删除成功")


@module_route.post("/batchDelete", summary="批量删除历史",
                   dependencies=[Depends(check_permission("apitest:history:delete"))])
async def batch_delete(params: ApiRequestHistoryBatchDelete, session: Session = Depends(get_session)):
    """批量删除历史记录"""
    service = RequestHistoryService(session)
    deleted_count = service.batch_delete(params.ids)
    return respModel.ok_resp(msg=f"已删除 {deleted_count} 条记录")


@module_route.put("/toggleFavorite", summary="切换收藏状态",
                  dependencies=[Depends(check_permission("apitest:history:edit"))])
async def toggle_favorite(id: int = Query(..., description="历史ID"),
                          session: Session = Depends(get_session)):
    """切换收藏状态"""
    service = RequestHistoryService(session)
    is_favorite = service.toggle_favorite(id)
    if is_favorite is None:
        return respModel.error_resp(msg="记录不存在")
    status = "已收藏" if is_favorite == 1 else "已取消收藏"
    return respModel.ok_resp(msg=status)


@module_route.post("/clear", summary="清空历史记录",
                   dependencies=[Depends(check_permission("apitest:history:delete"))])
async def clear(params: ApiRequestHistoryClearParams, session: Session = Depends(get_session)):
    """清空历史记录"""
    service = RequestHistoryService(session)
    deleted_count = service.clear(
        project_id=params.project_id,
        keep_favorites=params.keep_favorites,
        days=params.days
    )
    return respModel.ok_resp(msg=f"已清空 {deleted_count} 条记录")


@module_route.get("/statistics", summary="历史统计",
                  dependencies=[Depends(check_permission("apitest:history:query"))])
async def statistics(project_id: int = Query(..., description="项目ID"),
                     days: int = Query(7, description="统计天数"),
                     session: Session = Depends(get_session)):
    """获取请求历史统计"""
    service = RequestHistoryService(session)
    result = service.get_statistics(project_id, days)
    return respModel.ok_resp(dic_t=result)
