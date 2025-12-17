"""
Mock服务模型
支持Mock规则管理和智能Mock
"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiMock(SQLModel, table=True):
    """Mock规则表"""
    __tablename__ = "t_api_mock"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='Mock ID')
    project_id: int = Field(description='所属项目ID')
    api_id: Optional[int] = Field(default=None, description='关联接口ID')
    mock_name: str = Field(max_length=255, description='Mock名称')
    mock_desc: Optional[str] = Field(default=None, max_length=500, description='Mock描述')
    mock_path: str = Field(max_length=500, description='Mock路径')
    mock_method: str = Field(max_length=20, default='GET', description='请求方法')
    
    # 请求匹配条件
    match_headers: Optional[str] = Field(default=None, description='匹配请求头JSON')
    match_params: Optional[str] = Field(default=None, description='匹配请求参数JSON')
    match_body: Optional[str] = Field(default=None, description='匹配请求体JSON')
    
    # 响应配置
    response_status: int = Field(default=200, description='响应状态码')
    response_headers: Optional[str] = Field(default=None, description='响应头JSON')
    response_body: Optional[str] = Field(default=None, description='响应体')
    response_body_type: str = Field(default='json', max_length=50, description='响应体类型(json/xml/text/html)')
    
    # 高级配置
    delay_ms: int = Field(default=0, description='延迟响应(毫秒)')
    is_enabled: int = Field(default=1, description='是否启用(1是/0否)')
    priority: int = Field(default=0, description='优先级，数字越大优先级越高')
    
    # Mock脚本（高级）
    mock_script: Optional[str] = Field(default=None, description='Mock脚本(Python)')
    use_script: int = Field(default=0, description='是否使用脚本(1是/0否)')
    
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')


class ApiMockLog(SQLModel, table=True):
    """Mock请求日志表"""
    __tablename__ = "t_api_mock_log"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='日志ID')
    mock_id: int = Field(description='Mock规则ID')
    project_id: int = Field(description='项目ID')
    request_method: str = Field(max_length=20, description='请求方法')
    request_path: str = Field(max_length=500, description='请求路径')
    request_headers: Optional[str] = Field(default=None, description='请求头JSON')
    request_body: Optional[str] = Field(default=None, description='请求体')
    response_status: int = Field(description='响应状态码')
    response_body: Optional[str] = Field(default=None, description='响应体')
    response_time: int = Field(default=0, description='响应时间(ms)')
    client_ip: Optional[str] = Field(default=None, max_length=50, description='客户端IP')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
