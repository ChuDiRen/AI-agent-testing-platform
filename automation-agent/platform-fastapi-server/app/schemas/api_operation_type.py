"""
API 操作类型管理 Schema
从 Flask 迁移到 FastAPI
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApiOperationTypeBase(BaseModel):
    """API 操作类型管理基础 Schema"""
    operation_type_name: str = Field(..., description='操作类型名称')
    operation_type_desc: Optional[str] = Field(None, description='操作类型描述')
    operation_type_fun_name: Optional[str] = Field(None, description='方法名')
    operation_type_value: Optional[str] = Field(None, description='方法体')
    is_enabled: Optional[str] = Field(None, description='是否启用')


class ApiOperationTypeCreate(ApiOperationTypeBase):
    """创建 API 操作类型管理 Schema"""
    pass


class ApiOperationTypeUpdate(BaseModel):
    """更新 API 操作类型管理 Schema"""
    operation_type_name: Optional[str] = None
    operation_type_desc: Optional[str] = None
    operation_type_fun_name: Optional[str] = None
    operation_type_value: Optional[str] = None
    is_enabled: Optional[str] = None


class ApiOperationTypeResponse(ApiOperationTypeBase):
    """API 操作类型管理响应 Schema"""
    id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
