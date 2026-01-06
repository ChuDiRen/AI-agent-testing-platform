from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class WebExecution(SQLModel, table=True):
    """Web测试执行记录表"""
    __tablename__ = "t_web_execution"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='执行记录ID')
    execution_id: str = Field(max_length=64, description='执行ID')
    project_id: int = Field(description='项目ID')
    execution_name: str = Field(max_length=200, description='执行名称')
    execution_type: str = Field(max_length=20, description='执行类型：single/batch/schedule')
    trigger_type: str = Field(max_length=20, description='触发类型：manual/api/schedule')
    trigger_by: Optional[int] = Field(default=None, description='触发人ID')
    case_ids: Optional[str] = Field(default=None, description='用例ID列表JSON')
    total_cases: int = Field(default=0, description='总用例数')
    passed_cases: int = Field(default=0, description='通过用例数')
    failed_cases: int = Field(default=0, description='失败用例数')
    skipped_cases: int = Field(default=0, description='跳过用例数')
    error_cases: int = Field(default=0, description='错误用例数')
    status: str = Field(max_length=20, description='执行状态：pending/running/completed/failed/stopped')
    start_time: Optional[datetime] = Field(default=None, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')
    duration: Optional[int] = Field(default=None, description='执行时长(秒)')
    browser_type: str = Field(default='chrome', max_length=20, description='浏览器类型')
    environment: Optional[str] = Field(default=None, max_length=100, description='执行环境')
    report_path: Optional[str] = Field(default=None, max_length=500, description='报告路径')
    log_path: Optional[str] = Field(default=None, max_length=500, description='日志路径')
    error_message: Optional[str] = Field(default=None, max_length=2000, description='错误信息')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')


class WebExecutionResult(SQLModel, table=True):
    """Web测试执行结果表"""
    __tablename__ = "t_web_execution_result"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='结果记录ID')
    execution_id: str = Field(max_length=64, description='执行ID')
    case_id: int = Field(description='用例ID')
    case_name: str = Field(max_length=200, description='用例名称')
    status: str = Field(max_length=20, description='执行状态：passed/failed/skipped/error')
    start_time: Optional[datetime] = Field(default=None, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')
    duration: Optional[int] = Field(default=None, description='执行时长(毫秒)')
    error_message: Optional[str] = Field(default=None, max_length=2000, description='错误信息')
    error_type: Optional[str] = Field(default=None, max_length=100, description='错误类型')
    screenshot_path: Optional[str] = Field(default=None, max_length=500, description='截图路径')
    step_results: Optional[str] = Field(default=None, description='步骤执行结果JSON')
    assertions: Optional[str] = Field(default=None, description='断言结果JSON')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
