from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WebProjectBase(BaseModel):
    """Web项目基础Schema"""
    name: str = Field(..., max_length=100, description='项目名称')
    description: Optional[str] = Field(None, max_length=500, description='项目描述')
    base_url: str = Field(..., max_length=255, description='基础URL')
    browser_type: str = Field(default='chrome', max_length=20, description='浏览器类型')
    timeout: int = Field(default=30, description='超时时间(秒)')
    page_load_timeout: int = Field(default=60, description='页面加载超时(秒)')
    implicit_wait: int = Field(default=10, description='隐式等待(秒)')
    screenshot_path: Optional[str] = Field(None, max_length=255, description='截图保存路径')
    report_path: Optional[str] = Field(None, max_length=255, description='报告保存路径')
    status: str = Field(default='active', max_length=20, description='状态：active/inactive')


class WebProjectCreate(WebProjectBase):
    """创建Web项目Schema"""
    pass


class WebProjectUpdate(BaseModel):
    """更新Web项目Schema"""
    name: Optional[str] = Field(None, max_length=100, description='项目名称')
    description: Optional[str] = Field(None, max_length=500, description='项目描述')
    base_url: Optional[str] = Field(None, max_length=255, description='基础URL')
    browser_type: Optional[str] = Field(None, max_length=20, description='浏览器类型')
    timeout: Optional[int] = Field(None, description='超时时间(秒)')
    page_load_timeout: Optional[int] = Field(None, description='页面加载超时(秒)')
    implicit_wait: Optional[int] = Field(None, description='隐式等待(秒)')
    screenshot_path: Optional[str] = Field(None, max_length=255, description='截图保存路径')
    report_path: Optional[str] = Field(None, max_length=255, description='报告保存路径')
    status: Optional[str] = Field(None, max_length=20, description='状态：active/inactive')


class WebProjectQuery(BaseModel):
    """查询Web项目Schema"""
    page: int = Field(default=1, description='页码')
    pageSize: int = Field(default=10, description='每页数量')
    name: Optional[str] = Field(None, description='项目名称')
    status: Optional[str] = Field(None, description='状态')


class WebProjectResponse(WebProjectBase):
    """Web项目响应Schema"""
    id: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_by: Optional[int] = None
    update_by: Optional[int] = None

    class Config:
        from_attributes = True


class BatchDeleteRequest(BaseModel):
    """批量删除请求Schema"""
    ids: list[int] = Field(..., description='ID列表')
