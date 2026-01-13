"""
API 元数据管理 Schema
从 Flask 迁移到 FastAPI
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApiMetaBase(BaseModel):
    """API 元数据管理基础 Schema"""
    project_id: Optional[int] = Field(None, description='项目ID')
    module_id: Optional[int] = Field(None, description='模块ID')
    api_name: str = Field(..., description='接口名称')
    request_method: Optional[str] = Field(None, description='请求方法')
    request_url: Optional[str] = Field(None, description='请求地址')
    request_params: Optional[str] = Field(None, description='URL参数')
    request_headers: Optional[str] = Field(None, description='请求头')
    debug_vars: Optional[str] = Field(None, description='调试参数')
    request_form_datas: Optional[str] = Field(None, description='form-data')
    request_www_form_datas: Optional[str] = Field(None, description='www-form-data')
    requests_json_data: Optional[str] = Field(None, description='json数据')
    request_files: Optional[str] = Field(None, description='文件列表')


class ApiMetaCreate(ApiMetaBase):
    """创建 API 元数据管理 Schema"""
    pass


class ApiMetaUpdate(BaseModel):
    """更新 API 元数据管理 Schema"""
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    api_name: Optional[str] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    request_params: Optional[str] = None
    request_headers: Optional[str] = None
    debug_vars: Optional[str] = None
    request_form_datas: Optional[str] = None
    request_www_form_datas: Optional[str] = None
    requests_json_data: Optional[str] = None
    request_files: Optional[str] = None


class ApiMetaResponse(ApiMetaBase):
    """API 元数据管理响应 Schema"""
    id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
