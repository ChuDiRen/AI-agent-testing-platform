"""
审计日志管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.core.deps import get_db
from app.models.audit_log import AuditLog
from app.core.resp_model import respModel
from sqlalchemy import select, func, and_, or_
from app.services.audit_log import audit_log as audit_log_crud

router = APIRouter(prefix="/auditlog", tags=["审计日志管理"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有审计日志"""
    try:
        result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()))
        items = result.scalars().all()
        return respModel().ok_resp_list(lst=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    pageSize: int = Query(10, ge=1, le=100, description='每页数量'),
    user_id: Optional[int] = Query(None, description='用户ID'),
    username: Optional[str] = Query(None, description='用户名'),
    action: Optional[str] = Query(None, description='操作类型'),
    resource_type: Optional[str] = Query(None, description='资源类型'),
    status_code: Optional[int] = Query(None, description='状态码'),
    startTime: Optional[str] = Query(None, description='开始时间'),
    endTime: Optional[str] = Query(None, description='结束时间'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询审计日志"""
    try:
        query = select(AuditLog)
        
        # 添加筛选条件
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if username:
            query = query.where(AuditLog.username.like(f"%{username}%"))
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if status_code is not None:
            query = query.where(AuditLog.status_code == status_code)
        if startTime:
            start_datetime = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
            query = query.where(AuditLog.created_at >= start_datetime)
        if endTime:
            end_datetime = datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')
            query = query.where(AuditLog.created_at <= end_datetime)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        skip = (page - 1) * pageSize
        query = query.offset(skip).limit(pageSize).order_by(AuditLog.created_at.desc())
        result = await db.execute(query)
        items = result.scalars().all()
        
        return respModel().ok_resp_list(lst=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=respModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='日志ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询审计日志"""
    try:
        result = await db.execute(select(AuditLog).where(AuditLog.id == id))
        item = result.scalars().first()
        if not item:
            raise NotFoundException("审计日志不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.delete("/delete", response_model=respModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='日志ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除审计日志"""
    try:
        result = await db.execute(select(AuditLog).where(AuditLog.id == id))
        log = result.scalars().first()
        if not log:
            raise NotFoundException("审计日志不存在")
        
        await db.delete(log)
        await db.commit()
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.delete("/batchDelete", response_model=respModel)
async def batch_delete(
    *,
    ids: List[int] = Query(..., description='日志ID列表'),
    db: AsyncSession = Depends(get_db)
):
    """批量删除审计日志"""
    try:
        result = await db.execute(
            AuditLog.__table__.delete().where(AuditLog.id.in_(ids))
        )
        await db.commit()
        return respModel().ok_resp(msg=f"成功删除{result.rowcount}条记录")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")


@router.delete("/clearBefore", response_model=respModel)
async def clear_before(
    *,
    date: str = Query(..., description='日期(YYYY-MM-DD)'),
    db: AsyncSession = Depends(get_db)
):
    """清除指定日期之前的审计日志"""
    try:
        target_date = datetime.strptime(date, '%Y-%m-%d')
        result = await db.execute(
            AuditLog.__table__.delete().where(AuditLog.created_at < target_date)
        )
        await db.commit()
        return respModel().ok_resp(msg=f"成功清除{result.rowcount}条记录")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"清除失败: {str(e)}")


@router.post("/clear", response_model=respModel)
async def clear(
    *,
    data: dict = None,
    db: AsyncSession = Depends(get_db)
):
    """清除所有审计日志"""
    try:
        result = await db.execute(AuditLog.__table__.delete())
        await db.commit()
        return respModel().ok_resp(msg=f"成功清除{result.rowcount}条记录")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"清除失败: {str(e)}")


@router.get("/statistics", response_model=respModel)
async def statistics(
    *,
    startTime: Optional[str] = Query(None, description='开始时间'),
    endTime: Optional[str] = Query(None, description='结束时间'),
    db: AsyncSession = Depends(get_db)
):
    """审计日志统计"""
    try:
        query = select(AuditLog)
        
        if startTime:
            start_datetime = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
            query = query.where(AuditLog.created_at >= start_datetime)
        if endTime:
            end_datetime = datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')
            query = query.where(AuditLog.created_at <= end_datetime)
        
        # 总数
        result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = result.scalar()
        
        # 按操作类型统计
        query_action = query
        result = await db.execute(
            select(AuditLog.action, func.count()).select_from(query_action.subquery()).group_by(AuditLog.action)
        )
        action_stats = [{"action": row[0], "count": row[1]} for row in result.all()]
        
        # 按状态码统计
        query_status = query
        result = await db.execute(
            select(AuditLog.status_code, func.count()).select_from(query_status.subquery()).group_by(AuditLog.status_code)
        )
        status_stats = [{"status_code": row[0], "count": row[1]} for row in result.all()]
        
        return respModel().ok_resp_simple(
            data={
                "total": total,
                "action_stats": action_stats,
                "status_stats": status_stats
            },
            msg="统计成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")
