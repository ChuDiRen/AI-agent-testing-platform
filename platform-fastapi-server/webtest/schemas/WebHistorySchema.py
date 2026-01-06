from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

from ..model.WebHistoryModel import WebExecutionStatus, WebEnvironment


class WebHistoryQuery(BaseModel):
    """Web历史查询参数"""
    page: int = Field(default=1, ge=1, description='页码')
    pageSize: int = Field(default=10, ge=1, le=100, description='每页数量')
    project_id: Optional[int] = Field(default=None, description='项目ID')
    status: Optional[str] = Field(default=None, description='执行状态')
    env: Optional[str] = Field(default=None, description='执行环境')
    executor: Optional[str] = Field(default=None, description='执行人')
    start_date: Optional[datetime] = Field(default=None, description='开始日期')
    end_date: Optional[datetime] = Field(default=None, description='结束日期')
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None and v not in [status.value for status in WebExecutionStatus]:
            raise ValueError('执行状态无效')
        return v
    
    @validator('env')
    def validate_env(cls, v):
        if v is not None and v not in [env.value for env in WebEnvironment]:
            raise ValueError('执行环境无效')
        return v
    
    class Config:
        """Schema配置"""
        schema_extra = {
            "example": {
                "page": 1,
                "pageSize": 10,
                "project_id": 1,
                "status": "success",
                "env": "test",
                "executor": "admin"
            }
        }


class WebHistoryCreate(BaseModel):
    """创建Web历史记录"""
    project_id: int = Field(..., description='项目ID')
    project_name: str = Field(..., max_length=200, description='项目名称')
    env: WebEnvironment = Field(..., description='执行环境')
    status: WebExecutionStatus = Field(default=WebExecutionStatus.RUNNING, description='执行状态')
    total: int = Field(default=0, description='总用例数')
    passed: int = Field(default=0, description='通过用例数')
    failed: int = Field(default=0, description='失败用例数')
    pass_rate: float = Field(default=0.0, description='通过率')
    duration: int = Field(default=0, description='执行耗时(秒)')
    executor: str = Field(..., max_length=100, description='执行人')
    browsers: Optional[List[str]] = Field(default=None, description='浏览器列表')
    threads: int = Field(default=1, description='并发线程数')
    case_ids: Optional[List[int]] = Field(default=None, description='执行的用例ID列表')
    error_summary: Optional[str] = Field(default=None, max_length=2000, description='错误摘要')
    
    class Config:
        """Schema配置"""
        use_enum_values = True
        schema_extra = {
            "example": {
                "project_id": 1,
                "project_name": "商城系统 Web 测试",
                "env": "test",
                "executor": "admin",
                "browsers": ["chromium"],
                "threads": 2
            }
        }


class WebHistoryUpdate(BaseModel):
    """更新Web历史记录"""
    id: str = Field(..., description='执行ID')
    status: Optional[WebExecutionStatus] = Field(default=None, description='执行状态')
    total: Optional[int] = Field(default=None, description='总用例数')
    passed: Optional[int] = Field(default=None, description='通过用例数')
    failed: Optional[int] = Field(default=None, description='失败用例数')
    pass_rate: Optional[float] = Field(default=None, description='通过率')
    duration: Optional[int] = Field(default=None, description='执行耗时(秒)')
    end_time: Optional[datetime] = Field(default=None, description='结束时间')
    browsers: Optional[List[str]] = Field(default=None, description='浏览器列表')
    report_path: Optional[str] = Field(default=None, description='报告文件路径')
    allure_path: Optional[str] = Field(default=None, description='Allure报告路径')
    error_summary: Optional[str] = Field(default=None, max_length=2000, description='错误摘要')
    
    class Config:
        """Schema配置"""
        use_enum_values = True
        schema_extra = {
            "example": {
                "id": "exec_20260106_001",
                "status": "success",
                "total": 15,
                "passed": 15,
                "failed": 0,
                "pass_rate": 100.0,
                "duration": 180
            }
        }


class WebHistoryResponse(BaseModel):
    """Web历史响应数据"""
    id: str
    project_id: int
    project_name: str
    env: str
    status: str
    total: int
    passed: int
    failed: int
    pass_rate: float
    duration: int
    executor: str
    start_time: datetime
    end_time: Optional[datetime] = None
    browsers: Optional[List[str]] = None
    threads: int
    case_ids: Optional[List[int]] = None
    report_path: Optional[str] = None
    allure_path: Optional[str] = None
    error_summary: Optional[str] = None
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True


class WebHistoryCaseResponse(BaseModel):
    """Web历史用例详情响应"""
    id: int
    execution_id: str
    case_id: int
    case_name: str
    status: str
    duration: int
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    screenshot_path: Optional[str] = None
    step_results: Optional[dict] = None
    create_time: datetime
    
    class Config:
        from_attributes = True


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[str] = Field(..., description='执行ID列表')
