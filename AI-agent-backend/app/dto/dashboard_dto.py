"""
仪表板DTO
定义仪表板相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class DashboardStatsRequest(BaseModel):
    """
    仪表板统计数据请求DTO
    """
    date_range: Optional[str] = Field(None, description="日期范围筛选")
    department_id: Optional[int] = Field(None, description="部门ID筛选")

    class Config:
        json_schema_extra = {
            "example": {
                "date_range": "7d",  # 7天、30天、90天等
                "department_id": 1
            }
        }


class SystemInfoRequest(BaseModel):
    """
    系统信息请求DTO
    """
    include_performance: Optional[bool] = Field(False, description="是否包含性能信息")

    class Config:
        json_schema_extra = {
            "example": {
                "include_performance": True
            }
        }


class DashboardOverviewRequest(BaseModel):
    """
    仪表板概览请求DTO
    """
    activity_limit: Optional[int] = Field(10, ge=1, le=50, description="最近活动数量限制")
    date_range: Optional[str] = Field(None, description="日期范围筛选")

    class Config:
        json_schema_extra = {
            "example": {
                "activity_limit": 10,
                "date_range": "7d"
            }
        }


class DashboardStatsResponse(BaseModel):
    """
    仪表板统计数据响应DTO
    """
    user_count: int = Field(..., description="用户总数")
    role_count: int = Field(..., description="角色数量")
    menu_count: int = Field(..., description="菜单数量")
    department_count: int = Field(..., description="部门数量")

    # AI代理相关统计 # 新增AI代理统计数据
    agent_count: int = Field(0, description="AI代理总数")
    active_agent_count: int = Field(0, description="激活代理数量")
    running_agent_count: int = Field(0, description="运行中代理数量")

    # 测试相关统计 # 新增测试统计数据
    test_case_count: int = Field(0, description="测试用例总数")
    test_report_count: int = Field(0, description="测试报告总数")

    # AI模型相关统计 # 新增AI模型统计数据
    ai_model_count: int = Field(0, description="AI模型总数")

    class Config:
        json_schema_extra = {
            "example": {
                "user_count": 5,
                "role_count": 3,
                "menu_count": 15,
                "department_count": 4,
                "agent_count": 8,
                "active_agent_count": 6,
                "running_agent_count": 2,
                "test_case_count": 25,
                "test_report_count": 12,
                "ai_model_count": 4
            }
        }


class SystemInfoResponse(BaseModel):
    """
    系统信息响应DTO
    """
    system_version: str = Field(..., description="系统版本")
    server_info: str = Field(..., description="服务器信息")
    database_info: str = Field(..., description="数据库信息")
    last_login_time: Optional[datetime] = Field(None, description="最后登录时间")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "system_version": "v1.0.0",
                "server_info": "FastAPI + Vue 3",
                "database_info": "SQLite",
                "last_login_time": "2025-08-24T14:43:51.727092"
            }
        }


class RecentActivityResponse(BaseModel):
    """
    最近活动响应DTO
    """
    activity_type: str = Field(..., description="活动类型")
    description: str = Field(..., description="活动描述")
    user_name: str = Field(..., description="用户名")
    create_time: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "activity_type": "LOGIN",
                "description": "用户登录系统",
                "user_name": "admin",
                "create_time": "2025-08-24T14:43:51.727092"
            }
        }


class QuickActionResponse(BaseModel):
    """
    快捷操作响应DTO
    """
    name: str = Field(..., description="操作名称")
    icon: str = Field(..., description="操作图标")
    path: str = Field(..., description="操作路径")
    description: str = Field(..., description="操作描述")
    permission: Optional[str] = Field(None, description="所需权限")


class DashboardOverviewResponse(BaseModel):
    """
    仪表板概览响应DTO
    """
    stats: DashboardStatsResponse = Field(..., description="统计数据")
    system_info: SystemInfoResponse = Field(..., description="系统信息")
    recent_activities: List[RecentActivityResponse] = Field(default=[], description="最近活动")
    quick_actions: List[QuickActionResponse] = Field(default=[], description="快捷操作") # 新增快捷操作
    agent_status_chart: Dict[str, Any] = Field(default={}, description="代理状态图表数据") # 新增图表数据

    class Config:
        json_schema_extra = {
            "example": {
                "stats": {
                    "user_count": 5,
                    "role_count": 3,
                    "menu_count": 15,
                    "department_count": 4,
                    "agent_count": 8,
                    "active_agent_count": 6,
                    "running_agent_count": 2,
                    "test_case_count": 25,
                    "test_report_count": 12,
                    "ai_model_count": 4
                },
                "system_info": {
                    "system_version": "v1.0.0",
                    "server_info": "FastAPI + Vue 3",
                    "database_info": "SQLite",
                    "last_login_time": "2025-08-24T14:43:51.727092"
                },
                "recent_activities": [],
                "quick_actions": [
                    {
                        "name": "创建代理",
                        "icon": "Robot",
                        "path": "/agent/create",
                        "description": "快速创建AI代理",
                        "permission": "agent:create"
                    }
                ],
                "agent_status_chart": {
                    "labels": ["激活", "运行中", "停止", "错误"],
                    "data": [6, 2, 3, 1]
                }
            }
        }
