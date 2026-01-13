"""
API 测试用例信息 Schema
从 Flask 迁移到 FastAPI
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApiInfoCaseBase(BaseModel):
    """API 测试用例基础 Schema"""
    project_id: Optional[int] = Field(None, description='项目ID')
    module_id: Optional[int] = Field(None, description='模块ID')
    case_name: str = Field(..., description='用例名称')
    case_desc: Optional[str] = Field(None, description='用例描述')
    param_data: Optional[str] = Field(None, description='调试变量')
    pre_request: Optional[str] = Field(None, description='执行前事件')
    post_request: Optional[str] = Field(None, description='执行后事件')
    debug_info: Optional[str] = Field(None, description='调试信息')


class ApiInfoCaseCreate(ApiInfoCaseBase):
    """创建 API 测试用例 Schema"""
    pass


class ApiInfoCaseUpdate(BaseModel):
    """更新 API 测试用例 Schema"""
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    case_name: Optional[str] = None
    case_desc: Optional[str] = None
    param_data: Optional[str] = None
    pre_request: Optional[str] = None
    post_request: Optional[str] = None
    debug_info: Optional[str] = None


class ApiInfoCaseResponse(ApiInfoCaseBase):
    """API 测试用例响应 Schema"""
    id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
