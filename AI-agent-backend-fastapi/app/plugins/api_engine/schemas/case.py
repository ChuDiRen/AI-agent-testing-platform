# Copyright (c) 2025 左岚. All rights reserved.
"""
测试用例Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class CaseBase(BaseModel):
    """用例基础Schema"""
    suite_id: int = Field(..., description="所属套件ID")
    name: str = Field(..., min_length=1, max_length=200, description="用例名称")
    description: Optional[str] = Field(None, description="用例描述")
    config_type: str = Field("form", pattern="^(form|yaml)$", description="配置类型:form/yaml")
    config_data: Optional[Dict[str, Any]] = Field(None, description="表单配置数据")
    yaml_content: Optional[str] = Field(None, description="YAML内容")
    sort_order: int = Field(0, description="排序序号")
    status: str = Field("draft", description="状态:draft/active/disabled")
    tags: Optional[str] = Field(None, max_length=200, description="标签,逗号分隔")


class CaseCreate(CaseBase):
    """创建用例Schema"""
    pass


class CaseUpdate(BaseModel):
    """更新用例Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="用例名称")
    description: Optional[str] = Field(None, description="用例描述")
    config_type: Optional[str] = Field(None, pattern="^(form|yaml)$", description="配置类型")
    config_data: Optional[Dict[str, Any]] = Field(None, description="表单配置数据")
    yaml_content: Optional[str] = Field(None, description="YAML内容")
    sort_order: Optional[int] = Field(None, description="排序序号")
    status: Optional[str] = Field(None, description="状态")
    tags: Optional[str] = Field(None, description="标签")


class CaseResponse(CaseBase):
    """用例响应Schema"""
    case_id: int = Field(..., description="用例ID")
    created_by: int = Field(..., description="创建人ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class CaseListResponse(BaseModel):
    """用例列表响应Schema"""
    total: int = Field(..., description="总数")
    items: List[CaseResponse] = Field(..., description="用例列表")


class CaseExecuteRequest(BaseModel):
    """执行用例请求Schema"""
    context: Optional[Dict[str, Any]] = Field(None, description="执行上下文(额外的变量)")
    timeout: Optional[int] = Field(300, ge=1, le=3600, description="超时时间(秒)")

