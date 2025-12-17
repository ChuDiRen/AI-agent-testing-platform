"""
请求历史Controller
提供请求历史的查询、收藏、回放等功能
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, and_, or_
from typing import Optional

from core.database import get_session
from core.dependencies import check_permission
from core.resp_model import respModel

from apitest.model.ApiRequestHistoryModel import ApiRequestHistory
from apitest.schemas.api_request_history_schema import (
    ApiRequestHistoryQuery,
    ApiRequestHistoryCreate,
    ApiRequestHistoryBatchDelete,
    ApiRequestHistoryClearParams
)

module_name = "ApiRequestHistory"
module_model = ApiRequestHistory
module_route = APIRouter(prefix=f"/{module_name}", tags=["请求历史管理"])


@module_route.post("/queryByPage", summary="分页查询请求历史",
                   dependencies=[Depends(check_permission("apitest:history:query"))])
async def query_by_page(query: ApiRequestHistoryQuery, session: Session = Depends(get_session)):
    """分页查询请求历史"""
    offset = (query.page - 1) * query.pageSize
    statement = select(module_model)
    
    # 条件筛选
    if query.project_id:
        statement = statement.where(module_model.project_id == query.project_id)
    if query.api_id:
        statement = statement.where(module_model.api_id == query.api_id)
    if query.request_method:
        statement = statement.where(module_model.request_method == query.request_method)
    if query.request_url:
        statement = statement.where(module_model.request_url.contains(query.request_url))
    if query.is_success is not None:
        statement = statement.where(module_model.is_success == query.is_success)
    if query.is_favorite is not None:
        statement = statement.where(module_model.is_favorite == query.is_favorite)
    if query.start_time:
        statement = statement.where(module_model.create_time >= query.start_time)
    if query.end_time:
        statement = statement.where(module_model.create_time <= query.end_time)
    
    # 按时间倒序
    statement = statement.order_by(module_model.create_time.desc())
    
    # 查询总数
    count_statement = select(module_model)
    if query.project_id:
        count_statement = count_statement.where(module_model.project_id == query.project_id)
    total = len(session.exec(count_statement).all())
    
    # 分页查询
    datas = session.exec(statement.limit(query.pageSize).offset(offset)).all()
    
    return respModel.ok_resp_list(lst=datas, total=total)


@module_route.get("/queryById", summary="根据ID查询历史",
                  dependencies=[Depends(check_permission("apitest:history:query"))])
async def query_by_id(id: int = Query(..., description="历史ID"),
                      session: Session = Depends(get_session)):
    """根据ID查询历史详情"""
    data = session.get(module_model, id)
    if not data:
        return respModel.error_resp(msg="记录不存在")
    return respModel.ok_resp(obj=data)


@module_route.get("/queryRecent", summary="查询最近的请求",
                  dependencies=[Depends(check_permission("apitest:history:query"))])
async def query_recent(project_id: int = Query(..., description="项目ID"),
                       limit: int = Query(10, description="数量限制"),
                       session: Session = Depends(get_session)):
    """查询最近的请求历史"""
    statement = select(module_model).where(
        module_model.project_id == project_id
    ).order_by(module_model.create_time.desc()).limit(limit)
    
    datas = session.exec(statement).all()
    return respModel.ok_resp_list(lst=datas, total=len(datas))


@module_route.get("/queryFavorites", summary="查询收藏的请求",
                  dependencies=[Depends(check_permission("apitest:history:query"))])
async def query_favorites(project_id: int = Query(..., description="项目ID"),
                          session: Session = Depends(get_session)):
    """查询收藏的请求历史"""
    statement = select(module_model).where(
        and_(
            module_model.project_id == project_id,
            module_model.is_favorite == 1
        )
    ).order_by(module_model.create_time.desc())
    
    datas = session.exec(statement).all()
    return respModel.ok_resp_list(lst=datas, total=len(datas))


@module_route.post("/insert", summary="新增历史记录",
                   dependencies=[Depends(check_permission("apitest:history:add"))])
async def insert(history: ApiRequestHistoryCreate, session: Session = Depends(get_session)):
    """新增请求历史记录"""
    data = module_model(
        **history.model_dump(),
        create_time=datetime.now()
    )
    session.add(data)
    session.commit()
    session.refresh(data)
    
    return respModel.ok_resp(msg="记录成功", dic_t={"id": data.id})


@module_route.delete("/delete", summary="删除历史记录",
                     dependencies=[Depends(check_permission("apitest:history:delete"))])
async def delete(id: int = Query(..., description="历史ID"),
                 session: Session = Depends(get_session)):
    """删除历史记录"""
    data = session.get(module_model, id)
    if not data:
        return respModel.error_resp(msg="记录不存在")
    
    session.delete(data)
    session.commit()
    
    return respModel.ok_resp(msg="删除成功")


@module_route.post("/batchDelete", summary="批量删除历史",
                   dependencies=[Depends(check_permission("apitest:history:delete"))])
async def batch_delete(params: ApiRequestHistoryBatchDelete, session: Session = Depends(get_session)):
    """批量删除历史记录"""
    deleted_count = 0
    for id in params.ids:
        data = session.get(module_model, id)
        if data:
            session.delete(data)
            deleted_count += 1
    
    session.commit()
    
    return respModel.ok_resp(msg=f"已删除 {deleted_count} 条记录")


@module_route.put("/toggleFavorite", summary="切换收藏状态",
                  dependencies=[Depends(check_permission("apitest:history:edit"))])
async def toggle_favorite(id: int = Query(..., description="历史ID"),
                          session: Session = Depends(get_session)):
    """切换收藏状态"""
    data = session.get(module_model, id)
    if not data:
        return respModel.error_resp(msg="记录不存在")
    
    data.is_favorite = 0 if data.is_favorite == 1 else 1
    session.add(data)
    session.commit()
    
    status = "已收藏" if data.is_favorite == 1 else "已取消收藏"
    return respModel.ok_resp(msg=status)


@module_route.post("/clear", summary="清空历史记录",
                   dependencies=[Depends(check_permission("apitest:history:delete"))])
async def clear(params: ApiRequestHistoryClearParams, session: Session = Depends(get_session)):
    """清空历史记录"""
    statement = select(module_model).where(
        module_model.project_id == params.project_id
    )
    
    # 保留收藏
    if params.keep_favorites:
        statement = statement.where(module_model.is_favorite == 0)
    
    # 保留最近N天
    if params.days:
        cutoff_date = datetime.now() - timedelta(days=params.days)
        statement = statement.where(module_model.create_time < cutoff_date)
    
    records = session.exec(statement).all()
    deleted_count = len(records)
    
    for record in records:
        session.delete(record)
    
    session.commit()
    
    return respModel.ok_resp(msg=f"已清空 {deleted_count} 条记录")


@module_route.get("/statistics", summary="历史统计",
                  dependencies=[Depends(check_permission("apitest:history:query"))])
async def statistics(project_id: int = Query(..., description="项目ID"),
                     days: int = Query(7, description="统计天数"),
                     session: Session = Depends(get_session)):
    """获取请求历史统计"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    statement = select(module_model).where(
        and_(
            module_model.project_id == project_id,
            module_model.create_time >= cutoff_date
        )
    )
    records = session.exec(statement).all()
    
    # 统计数据
    total = len(records)
    success_count = sum(1 for r in records if r.is_success == 1)
    fail_count = total - success_count
    avg_response_time = sum(r.response_time or 0 for r in records) / total if total > 0 else 0
    
    # 按方法统计
    method_stats = {}
    for record in records:
        method = record.request_method
        if method not in method_stats:
            method_stats[method] = 0
        method_stats[method] += 1
    
    return respModel.ok_resp(dic_t={
        "total": total,
        "success_count": success_count,
        "fail_count": fail_count,
        "success_rate": round(success_count / total * 100, 2) if total > 0 else 0,
        "avg_response_time": round(avg_response_time, 2),
        "method_stats": method_stats
    })
