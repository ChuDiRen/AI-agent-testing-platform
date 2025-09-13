# Copyright (c) 2025 左岚. All rights reserved.
"""
仪表板Controller
处理仪表板相关的HTTP请求
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.db.session import get_db
from app.dto.base import ApiResponse, Success, Fail
from app.dto.dashboard_dto import (
    DashboardStatsResponse,
    SystemInfoResponse,
    DashboardOverviewResponse,
    DashboardStatsRequest,
    SystemInfoRequest,
    DashboardOverviewRequest
)
from app.entity.user import User
from app.middleware.auth import get_current_user_with_audit, get_current_user
from app.service.dashboard_service import DashboardService
from app.utils.log_decorators import log_operation, log_user_action

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/dashboard", tags=["仪表板"])


@router.post("/get-statistics-data", response_model=ApiResponse[DashboardStatsResponse], summary="获取仪表板统计数据")
@log_operation(
    operation_type="VIEW",
    resource_type="DASHBOARD",
    operation_desc="获取仪表板统计数据"
)
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

        # 转换为字典格式
        stats_dict = {
            "user_count": stats.user_count,
            "role_count": stats.role_count,
            "menu_count": stats.menu_count,
            "department_count": stats.department_count
        }

        return Success(code=200, msg="获取统计数据成功", data=stats_dict)
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计数据失败"
        )


@router.post("/get-system-info", response_model=ApiResponse[SystemInfoResponse], summary="获取系统信息")
@log_operation(
    operation_type="VIEW",
    resource_type="SYSTEM",
    operation_desc="获取系统信息"
)
async def get_system_info(
    request: SystemInfoRequest = None,
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
        # 添加调试信息
        logger.info("System info request received")

        dashboard_service = DashboardService(db)
        system_info = dashboard_service.get_system_info(1)  # 使用默认用户ID

        # 转换为字典格式
        system_info_dict = {
            "version": system_info.system_version,
            "server_info": system_info.server_info,
            "database_info": system_info.database_info,
            "last_login_time": system_info.last_login_time.isoformat() if system_info.last_login_time else None
        }

        return Success(code=200, msg="获取系统信息成功", data=system_info_dict)
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统信息失败"
        )


@router.post("/get-overview-data", response_model=ApiResponse[DashboardOverviewResponse], summary="获取仪表板概览")
@log_operation(
    operation_type="VIEW",
    resource_type="DASHBOARD",
    operation_desc="获取仪表板概览数据"
)
async def get_overview_data(
    request: DashboardOverviewRequest = None,
    current_user: User = Depends(get_current_user_with_audit),
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

        # 转换为字典格式
        overview_dict = {
            "stats": {
                "user_count": overview.stats.user_count,
                "role_count": overview.stats.role_count,
                "menu_count": overview.stats.menu_count,
                "department_count": overview.stats.department_count
            },
            "system_info": {
                "version": overview.system_info.system_version,
                "server_info": overview.system_info.server_info,
                "database_info": overview.system_info.database_info,
                "last_login_time": overview.system_info.last_login_time.isoformat() if overview.system_info.last_login_time else None
            }
        }

        return Success(code=200, msg="获取仪表板概览成功", data=overview_dict)
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取仪表板概览失败"
        )
