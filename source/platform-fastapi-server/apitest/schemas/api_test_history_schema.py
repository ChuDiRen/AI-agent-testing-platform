from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApiTestHistoryQuery(BaseModel): # 查询测试历史的请求模型
    page: int = 1  # 当前页码
    pageSize: int = 10  # 每页数量
    api_info_id: Optional[int] = None  # 接口ID筛选
    project_id: Optional[int] = None  # 项目ID筛选
    test_status: Optional[str] = None  # 测试状态筛选

class ApiTestHistoryCreate(BaseModel): # 创建测试历史的请求模型
    api_info_id: int
    project_id: int
    test_name: str
    test_status: str
    request_data: Optional[str] = None
    response_data: Optional[str] = None
    response_time: Optional[int] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None

class ExecuteTestRequest(BaseModel): # 执行测试的请求模型
    api_info_id: Optional[int] = None
    project_id: Optional[int] = None
    request_method: str
    request_url: str
    request_headers: Optional[str] = None
    request_params: Optional[str] = None
    request_body: Optional[str] = None

