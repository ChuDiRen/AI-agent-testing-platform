from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ApiTestHistory(SQLModel, table=True): # API测试历史记录表
    __tablename__ = "t_api_test_history"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='记录编号')
    api_info_id: int = Field(description='接口信息ID')
    project_id: int = Field(description='项目ID')
    test_name: str = Field(max_length=255, description='测试名称')
    test_status: str = Field(max_length=20, description='测试状态：running, success, failed')
    request_data: Optional[str] = Field(default=None, description='请求数据JSON')
    response_data: Optional[str] = Field(default=None, description='响应数据JSON')
    response_time: Optional[int] = Field(default=None, description='响应时间(ms)')
    status_code: Optional[int] = Field(default=None, description='HTTP状态码')
    error_message: Optional[str] = Field(default=None, description='错误信息')
    allure_report_path: Optional[str] = Field(default=None, max_length=500, description='allure报告路径')
    yaml_content: Optional[str] = Field(default=None, description='生成的YAML用例内容')
    execution_log: Optional[str] = Field(default=None, description='执行日志')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    finish_time: Optional[datetime] = Field(default=None, description='完成时间')
