"""
API 数据库基础配置 Schema
从 Flask 迁移到 FastAPI
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApiDbBaseBase(BaseModel):
    """API 数据库基础配置基础 Schema"""
    project_id: Optional[int] = Field(None, description='项目ID')
    name: str = Field(..., description='连接名')
    ref_name: Optional[str] = Field(None, description='引用变量')
    db_type: Optional[str] = Field(None, description='数据库类型')
    db_info: Optional[str] = Field(None, description='数据库连接信息')
    is_enabled: Optional[str] = Field(None, description='是否启用')


class ApiDbBaseCreate(ApiDbBaseBase):
    """创建 API 数据库基础配置 Schema"""
    pass


class ApiDbBaseUpdate(BaseModel):
    """更新 API 数据库基础配置 Schema"""
    project_id: Optional[int] = None
    name: Optional[str] = None
    ref_name: Optional[str] = None
    db_type: Optional[str] = None
    db_info: Optional[str] = None
    is_enabled: Optional[str] = None


class ApiDbBaseResponse(ApiDbBaseBase):
    """API 数据库基础配置响应 Schema"""
    id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
