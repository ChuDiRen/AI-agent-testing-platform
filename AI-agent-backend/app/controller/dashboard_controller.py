# Copyright (c) 2025 左岚. All rights reserved.
"""
仪表板Controller
处理仪表板相关的HTTP请求
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.db.session import get_db
from app.dto.base import ApiResponse
from app.dto.dashboard_dto import (
    DashboardStatsResponse,
    SystemInfoResponse,
    DashboardOverviewResponse,
    DashboardStatsRequest,
    SystemInfoRequest,
    DashboardOverviewRequest
)
from app.entity.user import User
from app.middleware.auth import get_current_user
from app.service.dashboard_service import DashboardService

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/dashboard", tags=["仪表板"])


@router.post("/get-statistics-data", response_model=ApiResponse[DashboardStatsResponse], summary="获取仪表板统计数据")
async def get_statistics_data(
    request: DashboardStatsRequest = None,
    db: Session = Depends(get_db)
):
    """
    获取仪表板统计数据

    Args:
        request: 统计数据请求参数（可选）
        db: 数据库会话

    Returns:
        仪表板统计数据，包括用户总数、角色数量、菜单数量、部门数量
    """
    try:
        dashboard_service = DashboardService(db)
        stats = dashboard_service.get_dashboard_stats()
        
        return ApiResponse.success_response(data=stats, message="获取统计数据成功")
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计数据失败"
        )


@router.post("/get-system-info", response_model=ApiResponse[SystemInfoResponse], summary="获取系统信息")
async def get_system_info(
    request: SystemInfoRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取系统信息

    Args:
        request: 系统信息请求参数（可选）
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        系统信息，包括版本、服务器信息、数据库信息、最后登录时间
    """
    try:
        dashboard_service = DashboardService(db)
        system_info = dashboard_service.get_system_info(current_user.id)
        
        return ApiResponse.success_response(data=system_info, message="获取系统信息成功")
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统信息失败"
        )


@router.post("/get-overview-data", response_model=ApiResponse[DashboardOverviewResponse], summary="获取仪表板概览")
async def get_overview_data(
    request: DashboardOverviewRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取仪表板概览数据

    Args:
        request: 概览数据请求参数（可选）
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        仪表板概览数据，包括统计数据、系统信息、最近活动
    """
    try:
        dashboard_service = DashboardService(db)
        overview = dashboard_service.get_dashboard_overview(current_user.id)
        
        return ApiResponse.success_response(data=overview, message="获取仪表板概览成功")
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取仪表板概览失败"
        )
