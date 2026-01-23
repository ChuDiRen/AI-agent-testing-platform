"""
API 测试用例步骤信息 Schema
从 Flask 迁移到 FastAPI
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApiInfoCaseStepBase(BaseModel):
    """API 测试用例步骤信息基础 Schema"""
    api_case_info_id: int = Field(..., description='用例的ID')
    key_word_id: int = Field(..., description='关键字方法ID')
    step_desc: Optional[str] = Field(None, description='步骤描述')
    ref_variable: Optional[str] = Field(None, description='引用变量')
    run_order: int = Field(..., description='步骤的顺序')


class ApiInfoCaseStepCreate(ApiInfoCaseStepBase):
    """创建 API 测试用例步骤信息 Schema"""
    pass


class ApiInfoCaseStepUpdate(BaseModel):
    """更新 API 测试用例步骤信息 Schema"""
    api_case_info_id: Optional[int] = None
    key_word_id: Optional[int] = None
    step_desc: Optional[str] = None
    ref_variable: Optional[str] = None
    run_order: Optional[int] = None


class ApiInfoCaseStepResponse(ApiInfoCaseStepBase):
    """API 测试用例步骤信息响应 Schema"""
    id: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
