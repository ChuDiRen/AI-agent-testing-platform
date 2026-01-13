"""
API 关键字管理 Schema
从 Flask 迁移到 FastAPI
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApiKeyWordBase(BaseModel):
    """API 关键字管理基础 Schema"""
    name: str = Field(..., description='关键字名称')
    keyword_desc: Optional[str] = Field(None, description='关键字描述')
    operation_type_id: Optional[int] = Field(None, description='操作类型ID')
    keyword_fun_name: Optional[str] = Field(None, description='方法名')
    keyword_value: Optional[str] = Field(None, description='方法体')
    is_enabled: Optional[str] = Field(None, description='是否启用')
    page_id: Optional[int] = Field(None, description='页面ID')


class ApiKeyWordCreate(ApiKeyWordBase):
    """创建 API 关键字管理 Schema"""
    pass


class ApiKeyWordUpdate(BaseModel):
    """更新 API 关键字管理 Schema"""
    name: Optional[str] = None
    keyword_desc: Optional[str] = None
    operation_type_id: Optional[int] = None
    keyword_fun_name: Optional[str] = None
    keyword_value: Optional[str] = None
    is_enabled: Optional[str] = None
    page_id: Optional[int] = None


class ApiKeyWordResponse(ApiKeyWordBase):
    """API 关键字管理响应 Schema"""
    id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
