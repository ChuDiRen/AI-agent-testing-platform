# Copyright (c) 2025 左岚. All rights reserved.
"""测试用例Schema"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TestCaseBase(BaseModel):
    """测试用例基础模型"""
    name: str = Field(..., description="用例名称")
    test_type: str = Field(..., description="测试类型: API/WEB/APP")
    module: Optional[str] = Field(None, description="所属模块")
    description: Optional[str] = Field(None, description="用例描述")
    preconditions: Optional[str] = Field(None, description="前置条件")
    test_steps: Optional[str] = Field(None, description="测试步骤")
    expected_result: Optional[str] = Field(None, description="预期结果")
    priority: str = Field("P2", description="优先级: P0/P1/P2/P3")
    status: str = Field("draft", description="状态: draft/active/deprecated")
    tags: Optional[str] = Field(None, description="标签,逗号分隔")


class TestCaseCreate(TestCaseBase):
    """创建测试用例"""
    pass


class TestCaseUpdate(BaseModel):
    """更新测试用例"""
    name: Optional[str] = None
    test_type: Optional[str] = None
    module: Optional[str] = None
    description: Optional[str] = None
    preconditions: Optional[str] = None
    test_steps: Optional[str] = None
    expected_result: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[str] = None


class TestCaseResponse(TestCaseBase):
    """测试用例响应"""
    testcase_id: int
    created_by: int
    create_time: datetime
    modify_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class TestCaseExecute(BaseModel):
    """执行测试用例"""
    environment: Optional[str] = Field(None, description="测试环境")
    config: Optional[dict] = Field(None, description="执行配置")

