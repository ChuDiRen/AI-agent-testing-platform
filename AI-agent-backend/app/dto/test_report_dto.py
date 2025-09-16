# Copyright (c) 2025 左岚. All rights reserved.
"""
测试报告DTO
定义测试报告相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field, validator

from .base import BaseRequest, BaseResponse, PaginationRequest, SearchRequest


class ReportStatusEnum(str, Enum):
    """报告状态枚举"""
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ReportTypeEnum(str, Enum):
    """报告类型枚举"""
    EXECUTION = "execution"
    SUMMARY = "summary"
    DETAILED = "detailed"
    CUSTOM = "custom"


# 请求DTO
class TestReportCreateRequest(BaseRequest):
    """创建测试报告请求DTO"""
    name: str = Field(..., min_length=1, max_length=200, description="报告名称")
    description: Optional[str] = Field(None, description="报告描述")
    report_type: ReportTypeEnum = Field(default=ReportTypeEnum.EXECUTION, description="报告类型")
    test_case_id: Optional[int] = Field(None, description="关联的测试用例ID")
    agent_id: Optional[int] = Field(None, description="关联的代理ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="附加数据")

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('报告名称不能为空')
        return v


class TestReportUpdateRequest(BaseRequest):
    """更新测试报告请求DTO"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="报告名称")
    description: Optional[str] = Field(None, description="报告描述")
    report_type: Optional[ReportTypeEnum] = Field(None, description="报告类型")
    summary: Optional[str] = Field(None, description="报告摘要")

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('报告名称不能为空')
        return v


class TestReportSearchRequest(SearchRequest):
    """测试报告搜索请求DTO"""
    report_type: Optional[ReportTypeEnum] = Field(None, description="报告类型筛选")
    status: Optional[ReportStatusEnum] = Field(None, description="报告状态筛选")
    test_case_id: Optional[int] = Field(None, description="测试用例ID筛选")
    agent_id: Optional[int] = Field(None, description="代理ID筛选")
    created_by_id: Optional[int] = Field(None, description="创建者ID筛选")
    start_date: Optional[datetime] = Field(None, description="创建时间开始")
    end_date: Optional[datetime] = Field(None, description="创建时间结束")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError('结束时间必须大于开始时间')
        return v


class TestReportGenerationRequest(BaseRequest):
    """测试报告生成请求DTO"""
    name: str = Field(..., min_length=1, max_length=200, description="报告名称")
    report_type: ReportTypeEnum = Field(default=ReportTypeEnum.EXECUTION, description="报告类型")
    test_case_ids: Optional[List[int]] = Field(None, description="测试用例ID列表")
    agent_id: Optional[int] = Field(None, description="代理ID")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="时间范围")
    include_charts: bool = Field(default=True, description="是否包含图表")
    include_details: bool = Field(default=True, description="是否包含详细信息")
    format: str = Field(default="pdf", description="报告格式: pdf, html, excel")

    @validator('format')
    def validate_format(cls, v):
        allowed_formats = ['pdf', 'html', 'excel', 'json']
        if v not in allowed_formats:
            raise ValueError(f'不支持的报告格式: {v}')
        return v


class TestReportStatisticsUpdateRequest(BaseRequest):
    """测试报告统计更新请求DTO"""
    total_cases: Optional[int] = Field(None, ge=0, description="总用例数")
    passed_cases: Optional[int] = Field(None, ge=0, description="通过用例数")
    failed_cases: Optional[int] = Field(None, ge=0, description="失败用例数")
    skipped_cases: Optional[int] = Field(None, ge=0, description="跳过用例数")
    blocked_cases: Optional[int] = Field(None, ge=0, description="阻塞用例数")


class TestReportIssueAddRequest(BaseRequest):
    """测试报告问题添加请求DTO"""
    issue_type: str = Field(..., description="问题类型")
    description: str = Field(..., min_length=1, description="问题描述")
    severity: str = Field(default="medium", description="严重级别: low, medium, high, critical")

    @validator('severity')
    def validate_severity(cls, v):
        allowed_severities = ['low', 'medium', 'high', 'critical']
        if v not in allowed_severities:
            raise ValueError(f'不支持的严重级别: {v}')
        return v


# 响应DTO
class TestReportResponse(BaseResponse):
    """测试报告响应DTO"""
    id: int = Field(description="报告ID")
    name: str = Field(description="报告名称")
    description: Optional[str] = Field(description="报告描述")
    report_type: str = Field(description="报告类型")
    status: str = Field(description="报告状态")
    test_case_id: Optional[int] = Field(description="关联的测试用例ID")
    agent_id: Optional[int] = Field(description="关联的代理ID")
    created_by_id: int = Field(description="创建者ID")
    start_time: Optional[datetime] = Field(description="执行开始时间")
    end_time: Optional[datetime] = Field(description="执行结束时间")
    duration: Optional[float] = Field(description="执行耗时")
    total_cases: int = Field(description="总测试用例数")
    passed_cases: int = Field(description="通过用例数")
    failed_cases: int = Field(description="失败用例数")
    skipped_cases: int = Field(description="跳过用例数")
    blocked_cases: int = Field(description="阻塞用例数")
    executed_cases: int = Field(description="已执行用例数")
    remaining_cases: int = Field(description="剩余用例数")
    pass_rate: float = Field(description="通过率")
    execution_rate: float = Field(description="执行率")
    content: Optional[Dict[str, Any]] = Field(description="报告内容")
    file_path: Optional[str] = Field(description="报告文件路径")
    summary: Optional[str] = Field(description="报告摘要")
    issues: Optional[List[Dict[str, Any]]] = Field(description="问题统计")
    metadata: Dict[str, Any] = Field(description="附加数据")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(description="更新时间")


class TestReportListResponse(BaseResponse):
    """测试报告列表响应DTO"""
    reports: List[TestReportResponse] = Field(description="测试报告列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页")
    page_size: int = Field(description="页大小")
    total_pages: int = Field(description="总页数")


class TestReportStatisticsResponse(BaseResponse):
    """测试报告统计响应DTO"""
    total_reports: int = Field(description="报告总数")
    generating_reports: int = Field(description="生成中报告数")
    completed_reports: int = Field(description="已完成报告数")
    failed_reports: int = Field(description="失败报告数")
    archived_reports: int = Field(description="已归档报告数")
    
    reports_by_type: Dict[str, int] = Field(description="按类型统计")
    reports_by_status: Dict[str, int] = Field(description="按状态统计")
    
    avg_generation_time: float = Field(description="平均生成时间")
    total_test_cases_covered: int = Field(description="总覆盖测试用例数")
    overall_pass_rate: float = Field(description="整体通过率")
    
    recent_reports: List[Dict[str, Any]] = Field(description="最近报告")


class TestReportGenerationResponse(BaseResponse):
    """测试报告生成响应DTO"""
    generation_id: str = Field(description="生成任务ID")
    report_id: Optional[int] = Field(description="报告ID")
    status: str = Field(description="生成状态")
    progress: float = Field(description="生成进度(0-100)")
    estimated_time: Optional[float] = Field(description="预计剩余时间(秒)")
    file_path: Optional[str] = Field(description="生成的文件路径")
    file_url: Optional[str] = Field(description="文件下载链接")
    errors: List[str] = Field(default_factory=list, description="错误信息")


class TestReportSummaryResponse(BaseResponse):
    """测试报告摘要响应DTO"""
    report_id: int = Field(description="报告ID")
    name: str = Field(description="报告名称")
    overall_status: str = Field(description="整体状态")
    test_summary: Dict[str, Any] = Field(description="测试摘要")
    key_metrics: Dict[str, Any] = Field(description="关键指标")
    top_issues: List[Dict[str, Any]] = Field(description="主要问题")
    recommendations: List[str] = Field(description="建议")
    charts_data: Optional[Dict[str, Any]] = Field(description="图表数据")


class TestReportContentResponse(BaseResponse):
    """测试报告内容响应DTO"""
    report_id: int = Field(description="报告ID")
    content_type: str = Field(description="内容类型")
    content: Dict[str, Any] = Field(description="报告内容")
    metadata: Dict[str, Any] = Field(description="元数据")


# 导出所有DTO类
__all__ = [
    # 枚举
    "ReportStatusEnum",
    "ReportTypeEnum",
    
    # 请求DTO
    "TestReportCreateRequest",
    "TestReportUpdateRequest",
    "TestReportSearchRequest",
    "TestReportGenerationRequest",
    "TestReportStatisticsUpdateRequest",
    "TestReportIssueAddRequest",
    
    # 响应DTO
    "TestReportResponse",
    "TestReportListResponse",
    "TestReportStatisticsResponse",
    "TestReportGenerationResponse",
    "TestReportSummaryResponse",
    "TestReportContentResponse",
]