"""
Copyright (c) 2025 左岚. All rights reserved.
测试数据Schema
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TestDataBase(BaseModel):
    """测试数据基础Schema"""

    name: str = Field(..., description="数据名称", min_length=1, max_length=200)
    data_type: str = Field(default="json", description="数据类型: json, csv, text, sql")
    description: Optional[str] = Field(None, description="描述")
    content: str = Field(..., description="数据内容")


class TestDataCreate(TestDataBase):
    """创建测试数据Schema"""

    pass


class TestDataUpdate(BaseModel):
    """更新测试数据Schema"""

    name: Optional[str] = Field(None, description="数据名称", min_length=1, max_length=200)
    data_type: Optional[str] = Field(None, description="数据类型")
    description: Optional[str] = Field(None, description="描述")
    content: Optional[str] = Field(None, description="数据内容")


class TestDataResponse(TestDataBase):
    """测试数据响应Schema"""

    id: int = Field(..., description="数据ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class TestDataListResponse(BaseModel):
    """测试数据列表响应"""

    total: int = Field(..., description="总数")
    items: list[TestDataResponse] = Field(..., description="数据列表")

