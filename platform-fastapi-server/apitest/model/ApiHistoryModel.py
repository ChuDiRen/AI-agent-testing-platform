from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ApiHistory(SQLModel, table=True): # API测试历史记录表
    __tablename__ = "t_api_history"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='记录编号')
    api_info_id: int = Field(description='接口信息ID')
    project_id: int = Field(description='项目ID')
    plan_id: Optional[int] = Field(default=None, description='测试计划ID')
    case_info_id: Optional[int] = Field(default=None, description='用例ID')
    execution_uuid: Optional[str] = Field(default=None, max_length=64, description='批量执行UUID')
    test_name: str = Field(max_length=255, description='测试名称')
    test_status: str = Field(max_length=20, description='测试状态：running, success, failed')
    request_url: Optional[str] = Field(default=None, max_length=500, description='请求URL')
    request_method: Optional[str] = Field(default=None, max_length=20, description='请求方法')
    request_headers: Optional[str] = Field(default=None, description='请求头JSON')
    request_params: Optional[str] = Field(default=None, description='请求参数JSON')
    request_body: Optional[str] = Field(default=None, description='请求体')
    request_data: Optional[str] = Field(default=None, description='请求数据JSON')
    response_data: Optional[str] = Field(default=None, description='响应数据JSON')
    response_time: Optional[int] = Field(default=None, description='响应时间(ms)')
    status_code: Optional[int] = Field(default=None, description='HTTP状态码')
    response_headers: Optional[str] = Field(default=None, description='响应头JSON')
    response_body: Optional[str] = Field(default=None, description='响应体')
    error_message: Optional[str] = Field(default=None, description='错误信息')
    allure_report_path: Optional[str] = Field(default=None, max_length=500, description='allure报告路径')
    yaml_content: Optional[str] = Field(default=None, description='生成的YAML用例内容')
    execution_log: Optional[str] = Field(default=None, description='执行日志')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    modify_time: Optional[datetime] = Field(default_factory=datetime.now, description='修改时间')
    finish_time: Optional[datetime] = Field(default=None, description='完成时间')
