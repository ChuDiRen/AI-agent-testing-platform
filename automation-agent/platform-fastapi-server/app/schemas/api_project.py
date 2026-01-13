"""
API 项目管理 Schema
从 Flask 迁移到 FastAPI
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApiProjectBase(BaseModel):
    """API 项目管理基础 Schema"""
    project_name: str = Field(..., description='项目名称')
    project_desc: Optional[str] = Field(None, description='项目描述')


class ApiProjectCreate(ApiProjectBase):
    """创建 API 项目管理 Schema"""
    pass


class ApiProjectUpdate(BaseModel):
    """更新 API 项目管理 Schema"""
    project_name: Optional[str] = None
    project_desc: Optional[str] = None


class ApiProjectResponse(ApiProjectBase):
    """API 项目管理响应 Schema"""
    id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
