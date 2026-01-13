"""
API 集合信息 Schema
从 Flask 迁移到 FastAPI
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApiCollectionInfoBase(BaseModel):
    """API 集合信息基础 Schema"""
    project_id: Optional[int] = Field(None, description='项目ID')
    collection_name: Optional[str] = Field(None, description='测试集合名称')
    collection_desc: Optional[str] = Field(None, description='测试集合描述')
    collection_env: Optional[str] = Field(None, description='测试集合全局变量')


class ApiCollectionInfoCreate(ApiCollectionInfoBase):
    """创建 API 集合信息 Schema"""
    pass


class ApiCollectionInfoUpdate(BaseModel):
    """更新 API 集合信息 Schema"""
    project_id: Optional[int] = None
    collection_name: Optional[str] = None
    collection_desc: Optional[str] = None
    collection_env: Optional[str] = None


class ApiCollectionInfoResponse(ApiCollectionInfoBase):
    """API 集合信息响应 Schema"""
    id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
