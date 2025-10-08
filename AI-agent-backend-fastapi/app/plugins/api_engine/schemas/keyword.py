# Copyright (c) 2025 左岚. All rights reserved.
"""
关键字Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class KeywordParamSchema(BaseModel):
    """关键字参数Schema"""
    name: str = Field(..., description="参数名称")
    type: str = Field(..., description="参数类型")
    required: bool = Field(False, description="是否必填")
    description: Optional[str] = Field(None, description="参数描述")
    default: Optional[Any] = Field(None, description="默认值")


class KeywordBase(BaseModel):
    """关键字基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="关键字名称")
    description: Optional[str] = Field(None, description="关键字描述")
    params_schema: Optional[List[KeywordParamSchema]] = Field(None, description="参数定义")
    code: str = Field(..., min_length=1, description="关键字实现代码")


class KeywordCreate(KeywordBase):
    """创建关键字Schema"""
    pass


class KeywordUpdate(BaseModel):
    """更新关键字Schema"""
    description: Optional[str] = Field(None, description="关键字描述")
    params_schema: Optional[List[KeywordParamSchema]] = Field(None, description="参数定义")
    code: Optional[str] = Field(None, description="关键字实现代码")


class KeywordResponse(KeywordBase):
    """关键字响应Schema"""
    keyword_id: int = Field(..., description="关键字ID")
    is_builtin: bool = Field(..., description="是否内置关键字")
    created_by: Optional[int] = Field(None, description="创建人ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class KeywordListResponse(BaseModel):
    """关键字列表响应Schema"""
    total: int = Field(..., description="总数")
    items: List[KeywordResponse] = Field(..., description="关键字列表")

