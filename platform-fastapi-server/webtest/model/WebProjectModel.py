from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class WebProject(SQLModel, table=True):
    """Web项目表"""
    __tablename__ = "t_web_project"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='项目ID')
    name: str = Field(max_length=100, description='项目名称')
    description: Optional[str] = Field(default=None, max_length=500, description='项目描述')
    base_url: str = Field(max_length=255, description='基础URL')
    browser_type: str = Field(default='chrome', max_length=20, description='浏览器类型')
    timeout: int = Field(default=30, description='超时时间(秒)')
    page_load_timeout: int = Field(default=60, description='页面加载超时(秒)')
    implicit_wait: int = Field(default=10, description='隐式等待(秒)')
    screenshot_path: Optional[str] = Field(default=None, max_length=255, description='截图保存路径')
    report_path: Optional[str] = Field(default=None, max_length=255, description='报告保存路径')
    status: str = Field(default='active', max_length=20, description='状态：active/inactive')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
    create_by: Optional[int] = Field(default=None, description='创建人ID')
    update_by: Optional[int] = Field(default=None, description='更新人ID')
