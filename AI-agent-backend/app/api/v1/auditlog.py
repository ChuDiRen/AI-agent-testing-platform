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
        
        # 构建响应数据 - 字段名匹配前端期望
        log_list = []
        for log in logs:
            log_data = {
                "id": log.id,
                "username": log.USERNAME or "",  # 前端期望username
                "summary": log.OPERATION_DESC or "",  # 前端期望summary(接口概要)
                "module": log.RESOURCE_TYPE or "",  # 前端期望module(功能模块)
                "method": log.REQUEST_METHOD or "",  # 前端期望method(请求方法)
                "path": log.REQUEST_URL or "",  # 前端期望path(请求路径)
                "status": log.RESPONSE_STATUS or 0,  # 前端期望status(状态码)
                "request_body": log.REQUEST_PARAMS or "",  # 前端期望request_body(请求体)
                "response_body": log.RESPONSE_MESSAGE or "",  # 前端期望response_body(响应体)
                "response_time": log.EXECUTION_TIME or 0,  # 前端期望response_time(响应时间)
                "created_at": log.OPERATION_TIME.strftime("%Y-%m-%d %H:%M:%S") if log.OPERATION_TIME else ""  # 前端期望created_at
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

