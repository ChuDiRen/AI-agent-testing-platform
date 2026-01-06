from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class WebExecutionRequest(BaseModel):
    """Web测试执行请求Schema"""
    project_id: int = Field(..., description='项目ID')
    execution_name: str = Field(..., max_length=200, description='执行名称')
    execution_type: Literal['single', 'batch', 'schedule'] = Field(default='batch', description='执行类型')
    case_ids: List[int] = Field(..., description='要执行的用例ID列表')
    browser_type: str = Field(default='chrome', description='浏览器类型')
    environment: Optional[str] = Field(None, max_length=100, description='执行环境')
    parallel_count: int = Field(default=1, description='并发数')
    retry_count: int = Field(default=0, description='重试次数')
    timeout: int = Field(default=30, description='超时时间(分钟)')
    generate_report: bool = Field(default=True, description='是否生成报告')
    take_screenshot: bool = Field(default=True, description='是否截图')


class WebExecutionStopRequest(BaseModel):
    """Web测试停止请求Schema"""
    execution_id: str = Field(..., description='执行ID')
    force_stop: bool = Field(default=False, description='是否强制停止')


class WebExecutionStatus(BaseModel):
    """Web测试执行状态Schema"""
    execution_id: str
    project_id: int
    execution_name: str
    status: Literal['pending', 'running', 'completed', 'failed', 'stopped']
    progress: float = Field(default=0.0, description='执行进度(0-100)')
    total_cases: int
    passed_cases: int = 0
    failed_cases: int = 0
    skipped_cases: int = 0
    error_cases: int = 0
    running_cases: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # 秒
    current_case: Optional[str] = None
    error_message: Optional[str] = None
    browser_type: str
    environment: Optional[str] = None


class WebExecutionQuery(BaseModel):
    """Web执行历史查询Schema"""
    page: int = Field(default=1, description='页码')
    pageSize: int = Field(default=10, description='每页数量')
    project_id: Optional[int] = Field(None, description='项目ID')
    execution_name: Optional[str] = Field(None, description='执行名称')
    status: Optional[str] = Field(None, description='执行状态')
    execution_type: Optional[str] = Field(None, description='执行类型')
    trigger_type: Optional[str] = Field(None, description='触发类型')
    start_date: Optional[str] = Field(None, description='开始日期')
    end_date: Optional[str] = Field(None, description='结束日期')
    trigger_by: Optional[int] = Field(None, description='触发人ID')


class WebExecutionResponse(BaseModel):
    """Web执行记录响应Schema"""
    id: int
    execution_id: str
    project_id: int
    execution_name: str
    execution_type: str
    trigger_type: str
    trigger_by: Optional[int] = None
    total_cases: int
    passed_cases: int
    failed_cases: int
    skipped_cases: int
    error_cases: int
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    browser_type: str
    environment: Optional[str] = None
    report_path: Optional[str] = None
    log_path: Optional[str] = None
    error_message: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class WebExecutionResultResponse(BaseModel):
    """Web执行结果响应Schema"""
    id: int
    execution_id: str
    case_id: int
    case_name: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    screenshot_path: Optional[str] = None
    step_results: Optional[Dict[str, Any]] = None
    assertions: Optional[Dict[str, Any]] = None
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class WebExecutionDetail(BaseModel):
    """Web执行详情Schema"""
    execution_info: WebExecutionResponse
    case_results: List[WebExecutionResultResponse]
    statistics: Dict[str, Any]


class WebReportInfo(BaseModel):
    """Web报告信息Schema"""
    execution_id: str
    report_url: str
    report_format: str = Field(default='html', description='报告格式')
    is_available: bool = Field(default=False, description='报告是否可用')
    generate_time: Optional[datetime] = None
    file_size: Optional[int] = None  # 字节


class WebExecutionStep(BaseModel):
    """Web执行步骤Schema"""
    step_no: int
    action: str
    element_name: Optional[str] = None
    locator_type: Optional[str] = None
    locator_value: Optional[str] = None
    input_value: Optional[str] = None
    status: Literal['passed', 'failed', 'skipped']
    duration: Optional[int] = None
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
