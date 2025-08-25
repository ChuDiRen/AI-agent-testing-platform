# Copyright (c) 2025 左岚. All rights reserved.
"""
日志Controller
处理日志相关的HTTP请求
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.db.session import get_db
from app.dto.base import ApiResponse
from app.dto.log_dto import (
    LogQueryRequest,
    LogResponse,
    LogListResponse,
    LogStatsResponse,
    LogIdRequest,
    LogClearRequest
)
from app.entity.user import User
from app.middleware.auth import get_current_user, require_log_view_with_audit
from app.service.log_service import LogService

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/logs", tags=["日志管理"])


@router.get("", response_model=ApiResponse[LogListResponse], summary="获取日志列表")
async def get_logs(
    request: LogQueryRequest,
    current_user: User = Depends(require_log_view_with_audit()),
    db: Session = Depends(get_db)
):
    """
    获取日志列表

    Args:
        level: 日志级别
        start_time: 开始时间
        end_time: 结束时间
        keyword: 关键词搜索
        module: 模块名称
        user: 用户名
        page: 页码
        size: 每页大小
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        日志列表
    """
    try:
        logger.info(f"Log controller called by user {current_user.id}")
        log_service = LogService(db)

        query_request = request

        result = log_service.query_logs(query_request)

        return ApiResponse.success_response(data=result, message="获取日志列表成功")
        
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日志列表失败"
        )


@router.post("/details", response_model=ApiResponse[LogResponse], summary="获取日志详情")
async def get_log_detail(
    request: LogIdRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取日志详情

    Args:
        request: 日志ID请求（请求体传参）
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        日志详情
    """
    try:
        log_service = LogService(db)
        log_detail = log_service.get_log_by_id(request.log_id)
        
        if not log_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="日志不存在"
            )
        
        return ApiResponse.success_response(data=log_detail, message="获取日志详情成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting log detail {log_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日志详情失败"
        )


@router.get("/statistics", response_model=ApiResponse[LogStatsResponse], summary="获取日志统计")
async def get_log_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取日志统计信息
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        日志统计信息
    """
    try:
        log_service = LogService(db)
        stats = log_service.get_log_stats()
        
        return ApiResponse.success_response(data=stats, message="获取日志统计成功")
        
    except Exception as e:
        logger.error(f"Error getting log stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日志统计失败"
        )


@router.delete("", response_model=ApiResponse[dict], summary="清空日志")
async def clear_logs(
    request: LogClearRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    清空日志

    Args:
        request: 清空日志请求（请求体传参）
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        清空结果
    """
    try:
        log_service = LogService(db)
        deleted_count = log_service.clear_logs(request.before_date)
        
        # 记录操作日志
        log_service.create_log(
            level="INFO",
            module="log_management",
            message=f"管理员清空了 {deleted_count} 条日志",
            user=current_user.username,
            user_id=current_user.id,
            details=f"清空条件: before_date={before_date}"
        )
        
        return ApiResponse.success_response(
            data={"deleted_count": deleted_count},
            message=f"成功清空 {deleted_count} 条日志"
        )
        
    except Exception as e:
        logger.error(f"Error clearing logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清空日志失败"
        )
