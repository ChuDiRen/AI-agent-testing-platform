"""
环境管理模型
支持多环境配置（开发/测试/生产），环境变量管理
"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiEnvironment(SQLModel, table=True):
    """环境配置表"""
    __tablename__ = "t_api_environment"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='环境ID')
    project_id: int = Field(description='所属项目ID')
    env_name: str = Field(max_length=100, description='环境名称')
    env_code: str = Field(max_length=50, description='环境代码(dev/test/prod)')
    base_url: Optional[str] = Field(default=None, max_length=500, description='基础URL')
    env_variables: Optional[str] = Field(default=None, description='环境变量JSON')
    env_headers: Optional[str] = Field(default=None, description='全局请求头JSON')
    is_default: int = Field(default=0, description='是否默认环境(1是/0否)')
    is_enabled: int = Field(default=1, description='是否启用(1是/0否)')
    sort_order: int = Field(default=0, description='排序顺序')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
