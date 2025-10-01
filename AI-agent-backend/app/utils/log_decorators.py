"""
日志装饰器
用于自动记录接口调用日志和用户操作行为
"""

import json
import time
import traceback
from functools import wraps
from typing import Any, Callable, Dict, Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.service.log_service import LogService
from app.service.audit_log_service import AuditLogService
from app.entity.user import User

logger = get_logger(__name__)


def log_operation(
    operation_type: str,
    resource_type: str,
    operation_desc: str = "",
    log_level: str = "INFO",
    include_request: bool = True,
    include_response: bool = False
):
    """
    操作日志装饰器
    
    Args:
        operation_type: 操作类型 (CREATE, UPDATE, DELETE, VIEW, etc.)
        resource_type: 资源类型 (USER, ROLE, MENU, etc.)
        operation_desc: 操作描述
        log_level: 日志级别
        include_request: 是否包含请求参数
        include_response: 是否包含响应数据
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 提取参数
            request: Optional[Request] = None
            current_user: Optional[User] = None
            db: Optional[Session] = None
            
            # 从kwargs中提取常用参数
            for key, value in kwargs.items():
                if isinstance(value, Request):
                    request = value
                elif isinstance(value, User):
                    current_user = value
                elif isinstance(value, Session):
                    db = value
            
            # 记录请求信息
            request_info = {}
            if request and include_request:
                request_info = {
                    "method": request.method,
                    "url": str(request.url),
                    "client_ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "")
                }
            
            try:
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 计算执行时间
                execution_time = int((time.time() - start_time) * 1000)  # 毫秒
                
                # 记录成功日志
                if db:
                    await _log_success_operation(
                        db=db,
                        operation_type=operation_type,
                        resource_type=resource_type,
                        operation_desc=operation_desc,
                        log_level=log_level,
                        current_user=current_user,
                        request_info=request_info,
                        execution_time=execution_time,
                        response_data=result if include_response else None
                    )
                
                return result
                
            except Exception as e:
                # 计算执行时间
                execution_time = int((time.time() - start_time) * 1000)  # 毫秒
                
                # 记录失败日志
                if db:
                    await _log_error_operation(
                        db=db,
                        operation_type=operation_type,
                        resource_type=resource_type,
                        operation_desc=operation_desc,
                        current_user=current_user,
                        request_info=request_info,
                        execution_time=execution_time,
                        error=e
                    )
                
                raise
                
        return wrapper
    return decorator


def log_user_action(
    action: str,
    resource_type: str = "SYSTEM",
    description: str = ""
):
    """
    用户行为日志装饰器
    
    Args:
        action: 用户行为 (LOGIN, LOGOUT, ACCESS, etc.)
        resource_type: 资源类型
        description: 行为描述
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 提取参数
            request: Optional[Request] = None
            current_user: Optional[User] = None
            db: Optional[Session] = None
            
            for key, value in kwargs.items():
                if isinstance(value, Request):
                    request = value
                elif isinstance(value, User):
                    current_user = value
                elif isinstance(value, Session):
                    db = value
            
            try:
                # 执行原函数
                result = await func(*args, **kwargs)

                # 记录用户行为
                if db and current_user:
                    execution_time = int((time.time() - start_time) * 1000)

                    audit_service = AuditLogService(db)
                    audit_service.create_audit_log(  # 移除await,因为create_audit_log不是async方法
                        user_id=current_user.id,
                        username=current_user.username,
                        operation_type=action,
                        resource_type=resource_type,
                        operation_desc=description or f"用户{action}操作",
                        request_method=request.method if request else None,
                        request_url=str(request.url) if request else None,
                        response_status=200,
                        ip_address=request.client.host if request and request.client else "unknown",
                        user_agent=request.headers.get("user-agent", "") if request else "",
                        execution_time=execution_time,
                        is_success=True
                    )

                return result
                
            except Exception as e:
                # 记录失败的用户行为
                if db and current_user:
                    execution_time = int((time.time() - start_time) * 1000)

                    audit_service = AuditLogService(db)
                    audit_service.create_audit_log(  # 移除await,因为create_audit_log不是async方法
                        user_id=current_user.id,
                        username=current_user.username,
                        operation_type=action,
                        resource_type=resource_type,
                        operation_desc=f"{description or action}操作失败",
                        request_method=request.method if request else None,
                        request_url=str(request.url) if request else None,
                        response_status=500,
                        ip_address=request.client.host if request and request.client else "unknown",
                        user_agent=request.headers.get("user-agent", "") if request else "",
                        execution_time=execution_time,
                        is_success=False,
                        error_message=str(e)
                    )

                raise
                
        return wrapper
    return decorator


async def _log_success_operation(
    db: Session,
    operation_type: str,
    resource_type: str,
    operation_desc: str,
    log_level: str,
    current_user: Optional[User],
    request_info: Dict[str, Any],
    execution_time: int,
    response_data: Any = None
):
    """记录成功操作日志"""
    try:
        log_service = LogService(db)
        
        # 构建日志消息
        user_info = f"用户{current_user.username}" if current_user else "系统"
        message = f"{user_info}执行{operation_desc or operation_type}操作成功"
        
        # 构建详细信息
        details = {
            "operation_type": operation_type,
            "resource_type": resource_type,
            "execution_time": execution_time,
            "request_info": request_info
        }
        
        if response_data:
            details["response_data"] = str(response_data)[:1000]  # 限制长度
        
        # 创建系统日志
        log_service.create_log(
            level=log_level,
            module=f"{resource_type.lower()}_operation",
            message=message,
            user=current_user.username if current_user else None,
            user_id=current_user.id if current_user else None,
            ip_address=request_info.get("client_ip"),
            user_agent=request_info.get("user_agent"),
            request_method=request_info.get("method"),
            request_url=request_info.get("url"),
            details=json.dumps(details, ensure_ascii=False)
        )
        
    except Exception as e:
        logger.error(f"Failed to log success operation: {str(e)}")


async def _log_error_operation(
    db: Session,
    operation_type: str,
    resource_type: str,
    operation_desc: str,
    current_user: Optional[User],
    request_info: Dict[str, Any],
    execution_time: int,
    error: Exception
):
    """记录失败操作日志"""
    try:
        log_service = LogService(db)
        
        # 构建日志消息
        user_info = f"用户{current_user.username}" if current_user else "系统"
        message = f"{user_info}执行{operation_desc or operation_type}操作失败: {str(error)}"
        
        # 构建详细信息
        details = {
            "operation_type": operation_type,
            "resource_type": resource_type,
            "execution_time": execution_time,
            "request_info": request_info,
            "error": str(error)
        }
        
        # 创建错误日志
        log_service.create_log(
            level="ERROR",
            module=f"{resource_type.lower()}_operation",
            message=message,
            user=current_user.username if current_user else None,
            user_id=current_user.id if current_user else None,
            ip_address=request_info.get("client_ip"),
            user_agent=request_info.get("user_agent"),
            request_method=request_info.get("method"),
            request_url=request_info.get("url"),
            details=json.dumps(details, ensure_ascii=False),
            stack_trace=traceback.format_exc()
        )
        
    except Exception as e:
        logger.error(f"Failed to log error operation: {str(e)}")


# 导出装饰器
__all__ = ["log_operation", "log_user_action"]
