"""
AuditLog模块API - 完全按照vue-fastapi-admin标准实现
提供审计日志查询功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.service.audit_log_service import AuditLogService

router = APIRouter()


@router.get("/list", summary="获取审计日志列表")
async def get_auditlog_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="用户名"),
    operation: Optional[str] = Query(None, description="操作类型"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取审计日志列表（分页）
    
    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        audit_log_service = AuditLogService(db)
        
        # 构建查询条件
        filters = {}
        if username:
            filters['username'] = username
        if operation:
            filters['operation'] = operation
        if start_time:
            filters['start_time'] = start_time
        if end_time:
            filters['end_time'] = end_time
        
        # 获取审计日志列表
        logs, total = await audit_log_service.get_audit_log_list(
            page=page,
            page_size=page_size,
            filters=filters
        )
        
        # 构建响应数据
        log_list = []
        for log in logs:
            log_data = {
                "log_id": log.id,
                "username": log.username or "",
                "operation": log.operation or "",
                "method": log.method or "",
                "path": log.path or "",
                "ip": log.ip or "",
                "status": log.status or 0,
                "duration": log.duration or 0,
                "created_at": log.create_time.strftime("%Y-%m-%d %H:%M:%S") if log.create_time else ""
            }
            log_list.append(log_data)
        
        # 按照vue-fastapi-admin的分页格式
        response_data = {
            "items": log_list,
            "total": total
        }
        
        return Success(data=response_data)
        
    except Exception as e:
        return Fail(msg=f"获取审计日志列表失败: {str(e)}")

