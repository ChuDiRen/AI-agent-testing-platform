"""
仪表板Service
处理仪表板相关的业务逻辑
"""

from typing import List, Optional, Dict, Any

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.dto.dashboard_dto import (
    DashboardStatsResponse,
    SystemInfoResponse,
    RecentActivityResponse,
    DashboardOverviewResponse,
    QuickActionResponse
)
from app.entity.department import Department
from app.entity.menu import Menu
from app.entity.role import Role
from app.entity.user import User
from app.entity.agent import Agent, AgentStatus # 新增Agent相关导入
from app.entity.test_case import TestCase # 新增TestCase导入
from app.entity.test_report import TestReport # 新增TestReport导入
from app.entity.ai_model import AIModel # 新增AIModel导入

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

            # 获取AI代理统计 # 新增AI代理统计
            agent_count = self.db.query(func.count(Agent.id)).filter(Agent.is_deleted == 0).scalar() or 0
            active_agent_count = self.db.query(func.count(Agent.id)).filter(
                and_(Agent.status == AgentStatus.ACTIVE.value, Agent.is_deleted == 0)
            ).scalar() or 0
            running_agent_count = self.db.query(func.count(Agent.id)).filter(
                and_(Agent.status == AgentStatus.RUNNING.value, Agent.is_deleted == 0)
            ).scalar() or 0

            # 获取测试相关统计 # 新增测试统计
            test_case_count = self.db.query(func.count(TestCase.id)).filter(TestCase.is_deleted == 0).scalar() or 0
            test_report_count = self.db.query(func.count(TestReport.id)).filter(TestReport.is_deleted == 0).scalar() or 0

            # 获取AI模型统计 # 新增AI模型统计
            ai_model_count = self.db.query(func.count(AIModel.id)).filter(AIModel.is_deleted == 0).scalar() or 0

            logger.info(f"Dashboard stats: users={user_count}, roles={role_count}, menus={menu_count}, departments={department_count}, agents={agent_count}, test_cases={test_case_count}")

            return DashboardStatsResponse(
                user_count=user_count,
                role_count=role_count,
                menu_count=menu_count,
                department_count=department_count,
                agent_count=agent_count,
                active_agent_count=active_agent_count,
                running_agent_count=running_agent_count,
                test_case_count=test_case_count,
                test_report_count=test_report_count,
                ai_model_count=ai_model_count
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

    def get_quick_actions(self) -> List[QuickActionResponse]:
        """
        获取快捷操作列表

        Returns:
            快捷操作列表
        """
        quick_actions = [
            QuickActionResponse(
                name="创建AI代理",
                icon="Monitor",
                path="/agent/create",
                description="快速创建新的AI代理",
                permission="agent:create"
            ),
            QuickActionResponse(
                name="用户管理",
                icon="User",
                path="/system/user",
                description="管理系统用户",
                permission="user:view"
            ),
            QuickActionResponse(
                name="角色管理",
                icon="UserFilled",
                path="/system/role",
                description="管理用户角色",
                permission="role:view"
            ),
            QuickActionResponse(
                name="测试用例",
                icon="Document",
                path="/test/cases",
                description="查看测试用例",
                permission="test_case:view"
            ),
            QuickActionResponse(
                name="AI模型配置",
                icon="Setting",
                path="/model/config",
                description="配置AI模型",
                permission="model:view"
            ),
            QuickActionResponse(
                name="系统日志",
                icon="Operation",
                path="/logs",
                description="查看系统日志",
                permission="log:view"
            )
        ]
        return quick_actions

    def get_agent_status_chart(self) -> Dict[str, Any]:
        """
        获取代理状态图表数据

        Returns:
            代理状态图表数据
        """
        try:
            # 统计各状态的代理数量
            status_counts = {}
            for status in AgentStatus:
                count = self.db.query(func.count(Agent.id)).filter(
                    and_(Agent.status == status.value, Agent.is_deleted == 0)
                ).scalar() or 0
                status_counts[status.value] = count

            # 构造图表数据
            chart_data = {
                "labels": ["激活", "运行中", "停止", "错误", "维护中"],
                "data": [
                    status_counts.get(AgentStatus.ACTIVE.value, 0),
                    status_counts.get(AgentStatus.RUNNING.value, 0),
                    status_counts.get(AgentStatus.STOPPED.value, 0),
                    status_counts.get(AgentStatus.ERROR.value, 0),
                    status_counts.get(AgentStatus.MAINTENANCE.value, 0)
                ],
                "colors": ["#67C23A", "#409EFF", "#909399", "#F56C6C", "#E6A23C"]
            }

            return chart_data

        except Exception as e:
            logger.error(f"Error getting agent status chart: {str(e)}")
            return {"labels": [], "data": [], "colors": []}

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

            # 获取快捷操作 # 新增快捷操作
            quick_actions = self.get_quick_actions()

            # 获取代理状态图表数据 # 新增图表数据
            agent_status_chart = self.get_agent_status_chart()

            return DashboardOverviewResponse(
                stats=stats,
                system_info=system_info,
                recent_activities=recent_activities,
                quick_actions=quick_actions,
                agent_status_chart=agent_status_chart
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {str(e)}")
            raise Exception("获取仪表板数据失败")
