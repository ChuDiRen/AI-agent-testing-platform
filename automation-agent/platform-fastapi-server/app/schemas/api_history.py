"""
API 历史记录信息 Schema
从 Flask 迁移到 FastAPI
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApiHistoryBase(BaseModel):
    """API 历史记录基础 Schema"""
    collection_info_id: int = Field(..., description='关联t_app_collection_info表主键id')
    history_desc: Optional[str] = Field(None, description='运行记录简述')
    history_detail: Optional[str] = Field(None, description='运行详细记录')


class ApiHistoryCreate(ApiHistoryBase):
    """创建 API 历史记录 Schema"""
    pass


class ApiHistoryUpdate(BaseModel):
    """更新 API 历史记录 Schema"""
    collection_info_id: Optional[int] = None
    history_desc: Optional[str] = None
    history_detail: Optional[str] = None


class ApiHistoryResponse(ApiHistoryBase):
    """API 历史记录响应 Schema"""
    id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
