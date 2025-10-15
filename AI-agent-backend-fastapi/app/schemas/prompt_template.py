# Copyright (c) 2025 左岚. All rights reserved.
"""提示词模板Schema"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PromptTemplateBase(BaseModel):
    """提示词模板基础模型"""
    name: str = Field(..., description="模板名称")
    template_type: str = Field("testcase_generation", description="模板类型")
    test_type: Optional[str] = Field(None, description="测试类型: API/Web/App/通用")
    content: str = Field(..., description="提示词内容")
    variables: Optional[str] = Field(None, description="变量说明(JSON格式)")
    description: Optional[str] = Field(None, description="模板描述")
    is_active: bool = Field(True, description="是否启用")


class PromptTemplateCreate(PromptTemplateBase):
    """创建提示词模板"""
    pass


class PromptTemplateUpdate(BaseModel):
    """更新提示词模板"""
    name: Optional[str] = None
    template_type: Optional[str] = None
    test_type: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PromptTemplateResponse(PromptTemplateBase):
    """提示词模板响应"""
    template_id: int
    is_default: bool
    created_by: Optional[int] = None
    create_time: datetime
    modify_time: Optional[datetime] = None

    class Config:
        from_attributes = True

