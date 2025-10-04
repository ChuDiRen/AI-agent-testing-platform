# Copyright (c) 2025 左岚. All rights reserved.
"""测试报告Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TestReportBase(BaseModel):
    """测试报告基础模型"""
    name: str = Field(..., description="报告名称")
    description: Optional[str] = Field(None, description="报告描述")
    report_type: str = Field("execution", description="报告类型: execution/summary/detailed/custom")
    test_case_id: Optional[int] = Field(None, description="关联测试用例ID")
    agent_id: Optional[int] = Field(None, description="关联AI代理ID")


class TestReportCreate(TestReportBase):
    """创建测试报告"""
    pass


class TestReportUpdate(BaseModel):
    """更新测试报告"""
    name: Optional[str] = None
    description: Optional[str] = None
    report_type: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    issues: Optional[List[Dict[str, Any]]] = None


class TestReportResponse(TestReportBase):
    """测试报告响应"""
    report_id: int
    status: str
    created_by_id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    total_cases: int
    passed_cases: int
    failed_cases: int
    skipped_cases: int
    blocked_cases: int
    executed_cases: int
    remaining_cases: int
    pass_rate: float
    execution_rate: float
    file_path: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TestReportDetail(TestReportResponse):
    """测试报告详情"""
    content: Optional[Dict[str, Any]] = None
    issues: Optional[List[Dict[str, Any]]] = None
    extra_data: Optional[Dict[str, Any]] = None


class TestReportStatistics(BaseModel):
    """测试报告统计"""
    total_reports: int = Field(..., description="总报告数")
    generating_reports: int = Field(..., description="生成中的报告数")
    completed_reports: int = Field(..., description="已完成的报告数")
    failed_reports: int = Field(..., description="失败的报告数")
    average_pass_rate: float = Field(..., description="平均通过率")
    total_test_cases: int = Field(..., description="总测试用例数")
    passed_test_cases: int = Field(..., description="通过的测试用例数")
    failed_test_cases: int = Field(..., description="失败的测试用例数")


class TestExecutionBase(BaseModel):
    """测试执行基础模型"""
    testcase_id: int = Field(..., description="测试用例ID")
    environment: Optional[str] = Field(None, description="执行环境")
    executor: Optional[str] = Field(None, description="执行器")


class TestExecutionCreate(TestExecutionBase):
    """创建测试执行"""
    report_id: int = Field(..., description="关联报告ID")


class TestExecutionUpdate(BaseModel):
    """更新测试执行"""
    status: Optional[str] = None
    actual_result: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    logs: Optional[str] = None


class TestExecutionResponse(TestExecutionBase):
    """测试执行响应"""
    execution_id: int
    report_id: int
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    actual_result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportGenerateRequest(BaseModel):
    """报告生成请求"""
    name: str = Field(..., description="报告名称")
    description: Optional[str] = Field(None, description="报告描述")
    report_type: str = Field("execution", description="报告类型")
    testcase_ids: List[int] = Field(..., description="测试用例ID列表")
    environment: Optional[str] = Field("default", description="执行环境")
    config: Optional[Dict[str, Any]] = Field(None, description="执行配置")


class ReportExportRequest(BaseModel):
    """报告导出请求"""
    report_id: int = Field(..., description="报告ID")
    format: str = Field("excel", description="导出格式: excel/pdf")
    include_details: bool = Field(True, description="是否包含详细信息")

