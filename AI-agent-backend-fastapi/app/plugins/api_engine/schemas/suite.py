# Copyright (c) 2025 左岚. All rights reserved.
"""
测试套件Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class SuiteBase(BaseModel):
    """套件基础Schema"""
    name: str = Field(..., min_length=1, max_length=200, description="套件名称")
    description: Optional[str] = Field(None, description="套件描述")
    global_context: Optional[Dict[str, Any]] = Field(None, description="全局变量配置")


class SuiteCreate(SuiteBase):
    """创建套件Schema"""
    pass


class SuiteUpdate(BaseModel):
    """更新套件Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="套件名称")
    description: Optional[str] = Field(None, description="套件描述")
    global_context: Optional[Dict[str, Any]] = Field(None, description="全局变量配置")


class SuiteResponse(SuiteBase):
    """套件响应Schema"""
    suite_id: int = Field(..., description="套件ID")
    created_by: int = Field(..., description="创建人ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    case_count: Optional[int] = Field(0, description="用例数量")
    
    class Config:
        from_attributes = True


class SuiteListResponse(BaseModel):
    """套件列表响应Schema"""
    total: int = Field(..., description="总数")
    items: List[SuiteResponse] = Field(..., description="套件列表")

