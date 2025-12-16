"""
测试计划与机器人关联模型
"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiPlanRobot(SQLModel, table=True):
    """测试计划与机器人关联表"""
    __tablename__ = "t_api_plan_robot"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='关联ID')
    plan_id: int = Field(description='测试计划ID')
    robot_id: int = Field(description='机器人ID')
    is_enabled: bool = Field(default=True, description='是否启用通知')
    notify_on_success: bool = Field(default=True, description='成功时是否通知')
    notify_on_failure: bool = Field(default=True, description='失败时是否通知')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
