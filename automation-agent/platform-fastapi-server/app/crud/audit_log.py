"""
审计日志 CRUD 操作
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.audit_log import AuditLog


class CRUDAuditLog(CRUDBase[AuditLog, dict, dict]):
    """审计日志 CRUD"""
    
    async def get_by_page(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        module: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> tuple[List[AuditLog], int]:
        """分页查询审计日志"""
        query = select(AuditLog)
        
        # 条件过滤
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if username:
            query = query.where(AuditLog.username.like(f"%{username}%"))
        if module:
            query = query.where(AuditLog.module.like(f"%{module}%"))
        if method:
            query = query.where(AuditLog.method == method.upper())
        if path:
            query = query.where(AuditLog.path.like(f"%{path}%"))
        if status is not None:
            query = query.where(AuditLog.status == status)
        if start_time:
            query = query.where(AuditLog.created_at >= start_time)
        if end_time:
            query = query.where(AuditLog.created_at <= end_time)
        
        # 获取总数
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # 获取数据（按创建时间倒序）
        result = await db.execute(
            query.offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
        )
        items = result.scalars().all()
        
        return items, total
    
    async def create_audit(
        self,
        db: AsyncSession,
        user_id: Optional[int],
        username: Optional[str],
        module: Optional[str],
        summary: Optional[str],
        method: Optional[str],
        path: Optional[str],
        status: int,
        response_time: Optional[float],
        request_args: Optional[dict],
        response_body: Optional[dict]
    ) -> AuditLog:
        """创建审计日志"""
        import json
        
        db_obj = AuditLog(
            user_id=user_id,
            username=username,
            module=module,
            summary=summary,
            method=method,
            path=path,
            status=status,
            response_time=response_time,
            request_args=json.dumps(request_args) if request_args else None,
            response_body=json.dumps(response_body) if response_body else None
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def clear_old_logs(
        self,
        db: AsyncSession,
        days: int = 180
    ) -> int:
        """清除旧日志（默认保留6个月）"""
        from sqlalchemy import delete
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        stmt = delete(AuditLog).where(AuditLog.created_at < cutoff_date)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount


# 创建全局实例
audit_log = CRUDAuditLog(AuditLog)
