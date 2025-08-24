# Copyright (c) 2025 左岚. All rights reserved.
"""
仪表板Service
处理仪表板相关的业务逻辑
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.logger import get_logger
from app.entity.user import User
from app.entity.role import Role
from app.entity.menu import Menu
from app.entity.department import Department
from app.dto.dashboard_dto import (
    DashboardStatsResponse,
    SystemInfoResponse,
    RecentActivityResponse,
    DashboardOverviewResponse
)

logger = get_logger(__name__)


class DashboardService:
    """
    仪表板服务类
    提供仪表板相关的业务逻辑
    """

    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_stats(self) -> DashboardStatsResponse:
        """
        获取仪表板统计数据
        
        Returns:
            仪表板统计数据
        """
        try:
            # 获取用户总数
            user_count = self.db.query(func.count(User.id)).scalar() or 0
            
            # 获取角色数量
            role_count = self.db.query(func.count(Role.id)).scalar() or 0
            
            # 获取菜单数量
            menu_count = self.db.query(func.count(Menu.id)).scalar() or 0
            
            # 获取部门数量
            department_count = self.db.query(func.count(Department.id)).scalar() or 0
            
            logger.info(f"Dashboard stats: users={user_count}, roles={role_count}, menus={menu_count}, departments={department_count}")
            
            return DashboardStatsResponse(
                user_count=user_count,
                role_count=role_count,
                menu_count=menu_count,
                department_count=department_count
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            # 返回默认值
            return DashboardStatsResponse(
                user_count=0,
                role_count=0,
                menu_count=0,
                department_count=0
            )

    def get_system_info(self, user_id: Optional[int] = None) -> SystemInfoResponse:
        """
        获取系统信息
        
        Args:
            user_id: 用户ID，用于获取最后登录时间
            
        Returns:
            系统信息
        """
        try:
            # 获取用户最后登录时间
            last_login_time = None
            if user_id:
                user = self.db.query(User).filter(User.id == user_id).first()
                if user and user.last_login_time:
                    last_login_time = user.last_login_time
            
            return SystemInfoResponse(
                system_version="v1.0.0",
                server_info="FastAPI + Vue 3",
                database_info="SQLite",
                last_login_time=last_login_time
            )
            
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return SystemInfoResponse(
                system_version="v1.0.0",
                server_info="FastAPI + Vue 3",
                database_info="SQLite",
                last_login_time=None
            )

    def get_recent_activities(self, limit: int = 10) -> List[RecentActivityResponse]:
        """
        获取最近活动
        
        Args:
            limit: 限制返回数量
            
        Returns:
            最近活动列表
        """
        try:
            # 这里可以从审计日志表获取最近活动
            # 目前返回空列表，后续可以扩展
            activities = []
            
            # 示例：获取最近创建的用户
            recent_users = self.db.query(User).order_by(User.create_time.desc()).limit(limit).all()
            
            for user in recent_users:
                activities.append(RecentActivityResponse(
                    activity_type="USER_CREATED",
                    description=f"新用户 {user.username} 注册",
                    user_name="system",
                    create_time=user.create_time
                ))
            
            return activities
            
        except Exception as e:
            logger.error(f"Error getting recent activities: {str(e)}")
            return []

    def get_dashboard_overview(self, user_id: Optional[int] = None) -> DashboardOverviewResponse:
        """
        获取仪表板概览数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            仪表板概览数据
        """
        try:
            # 获取统计数据
            stats = self.get_dashboard_stats()
            
            # 获取系统信息
            system_info = self.get_system_info(user_id)
            
            # 获取最近活动
            recent_activities = self.get_recent_activities()
            
            return DashboardOverviewResponse(
                stats=stats,
                system_info=system_info,
                recent_activities=recent_activities
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {str(e)}")
            raise Exception("获取仪表板数据失败")
