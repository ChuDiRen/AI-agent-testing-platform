from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlmodel import SQLModel, Field


class WebExecutionStatus(str, Enum):
    """Web执行状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    CANCELLED = "cancelled"


class WebEnvironment(str, Enum):
    """Web环境枚举"""
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class WebHistory(SQLModel, table=True):
    """Web测试执行历史表"""
    __tablename__ = "t_web_history"
    
    id: Optional[str] = Field(default=None, primary_key=True, description='执行ID')
    project_id: int = Field(description='项目ID')
    project_name: str = Field(max_length=200, description='项目名称')
    env: WebEnvironment = Field(description='执行环境')
    status: WebExecutionStatus = Field(description='执行状态')
    total: int = Field(default=0, description='总用例数')
    passed: int = Field(default=0, description='通过用例数')
    failed: int = Field(default=0, description='失败用例数')
    pass_rate: float = Field(default=0.0, description='通过率')
    duration: int = Field(default=0, description='执行耗时(秒)')
    executor: str = Field(max_length=100, description='执行人')
    start_time: datetime = Field(default_factory=datetime.now, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')
    browsers: Optional[str] = Field(default=None, description='浏览器列表JSON')
    threads: int = Field(default=1, description='并发线程数')
    case_ids: Optional[str] = Field(default=None, description='执行的用例ID列表JSON')
    report_path: Optional[str] = Field(default=None, description='报告文件路径')
    allure_path: Optional[str] = Field(default=None, description='Allure报告路径')
    error_summary: Optional[str] = Field(default=None, max_length=2000, description='错误摘要')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
    
    class Config:
        """模型配置"""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "exec_20260106_001",
                "project_id": 1,
                "project_name": "商城系统 Web 测试",
                "env": "test",
                "status": "success",
                "total": 15,
                "passed": 15,
                "failed": 0,
                "pass_rate": 100.0,
                "duration": 180,
                "executor": "admin",
                "start_time": "2026-01-06T10:00:00",
                "browsers": '["chromium"]',
                "threads": 2
            }
        }


class WebHistoryCase(SQLModel, table=True):
    """Web测试执行历史用例详情表"""
    __tablename__ = "t_web_history_case"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='记录ID')
    execution_id: str = Field(description='执行ID')
    case_id: int = Field(description='用例ID')
    case_name: str = Field(max_length=200, description='用例名称')
    status: WebExecutionStatus = Field(description='执行状态')
    duration: int = Field(default=0, description='执行耗时(秒)')
    error_message: Optional[str] = Field(default=None, max_length=1000, description='错误信息')
    start_time: Optional[datetime] = Field(default=None, description='开始时间')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')
    screenshot_path: Optional[str] = Field(default=None, description='截图路径')
    step_results: Optional[str] = Field(default=None, description='步骤结果JSON')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    
    class Config:
        """模型配置"""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "execution_id": "exec_20260106_001",
                "case_id": 1,
                "case_name": "登录页面测试.yaml",
                "status": "success",
                "duration": 25,
                "error_message": None
            }
        }
