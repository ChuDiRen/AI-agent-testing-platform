"""
Mock服务Schema
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ApiMockQuery(BaseModel):
    """Mock查询参数"""
    page: int = 1
    pageSize: int = 10
    project_id: Optional[int] = None
    api_id: Optional[int] = None
    mock_name: Optional[str] = None
    mock_method: Optional[str] = None
    is_enabled: Optional[int] = None


class ApiMockCreate(BaseModel):
    """创建Mock规则"""
    project_id: int
    api_id: Optional[int] = None
    mock_name: str
    mock_desc: Optional[str] = None
    mock_path: str
    mock_method: str = "GET"
    match_headers: Optional[str] = None
    match_params: Optional[str] = None
    match_body: Optional[str] = None
    response_status: int = 200
    response_headers: Optional[str] = None
    response_body: Optional[str] = None
    response_body_type: str = "json"
    delay_ms: int = 0
    is_enabled: int = 1
    priority: int = 0
    mock_script: Optional[str] = None
    use_script: int = 0


class ApiMockUpdate(BaseModel):
    """更新Mock规则"""
    id: int
    mock_name: Optional[str] = None
    mock_desc: Optional[str] = None
    mock_path: Optional[str] = None
    mock_method: Optional[str] = None
    match_headers: Optional[str] = None
    match_params: Optional[str] = None
    match_body: Optional[str] = None
    response_status: Optional[int] = None
    response_headers: Optional[str] = None
    response_body: Optional[str] = None
    response_body_type: Optional[str] = None
    delay_ms: Optional[int] = None
    is_enabled: Optional[int] = None
    priority: Optional[int] = None
    mock_script: Optional[str] = None
    use_script: Optional[int] = None


class ApiMockLogQuery(BaseModel):
    """Mock日志查询参数"""
    page: int = 1
    pageSize: int = 20
    mock_id: Optional[int] = None
    project_id: Optional[int] = None
    request_method: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ApiMockGenerate(BaseModel):
    """智能生成Mock"""
    project_id: int
    api_id: int
    mock_name: Optional[str] = None
    generate_type: str = "success"  # success/error/random


class ApiMockFromApi(BaseModel):
    """从接口生成Mock"""
    api_id: int
    mock_name: Optional[str] = None
    response_template: Optional[str] = None
