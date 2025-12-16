from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# 查询Schema
class ApiInfoQuery(BaseModel):
    page: int = 1
    pageSize: int = 10
    project_id: Optional[int] = None
    group_id: Optional[int] = None
    api_name: Optional[str] = None
    request_method: Optional[str] = None

# 创建Schema
class ApiInfoCreate(BaseModel):
    project_id: Optional[int] = None
    api_name: Optional[str] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    request_params: Optional[str] = None
    request_headers: Optional[str] = None
    debug_vars: Optional[str] = None
    request_form_datas: Optional[str] = None
    request_www_form_datas: Optional[str] = None
    requests_json_data: Optional[str] = None
    request_files: Optional[str] = None
    executor_code: Optional[str] = None  # 执行器插件代码

# 更新Schema
class ApiInfoUpdate(BaseModel):
    id: int
    project_id: Optional[int] = None
    api_name: Optional[str] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    request_params: Optional[str] = None
    request_headers: Optional[str] = None
    debug_vars: Optional[str] = None
    request_form_datas: Optional[str] = None
    request_www_form_datas: Optional[str] = None
    requests_json_data: Optional[str] = None
    request_files: Optional[str] = None
    executor_code: Optional[str] = None  # 执行器插件代码

# 测试执行Schema
class ApiTestExecute(BaseModel):
    api_info_id: int
    test_name: Optional[str] = None
    context_vars: Optional[dict] = None  # 上下文变量
    pre_script: Optional[str] = None     # 前置脚本
    post_script: Optional[str] = None    # 后置脚本
    assertions: Optional[list] = None    # 断言配置

# 响应Schema
class ApiInfoResponse(BaseModel):
    id: int
    project_id: Optional[int] = None
    api_name: Optional[str] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    request_params: Optional[str] = None
    request_headers: Optional[str] = None
    debug_vars: Optional[str] = None
    request_form_datas: Optional[str] = None
    request_www_form_datas: Optional[str] = None
    requests_json_data: Optional[str] = None
    request_files: Optional[str] = None
    executor_code: Optional[str] = None  # 执行器插件代码
    create_time: Optional[datetime] = None

# 接口调试请求Schema
class ApiDebugRequest(BaseModel):
    """接口调试请求"""
    request_method: str  # 请求方法
    request_url: str  # 请求URL
    request_params: Optional[list] = None  # URL参数 [{"key": "name", "value": "test"}]
    request_headers: Optional[list] = None  # 请求头 [{"key": "Content-Type", "value": "application/json"}]
    request_form_datas: Optional[list] = None  # form-data参数
    request_www_form_datas: Optional[list] = None  # x-www-form-urlencoded参数
    requests_json_data: Optional[str] = None  # JSON请求体
    request_files: Optional[list] = None  # 文件上传参数
    debug_vars: Optional[list] = None  # 调试变量 [{"key": "base_url", "value": "http://localhost"}]
    timeout: Optional[int] = 30  # 超时时间（秒）

# 接口调试响应Schema
class ApiDebugResponse(BaseModel):
    """接口调试响应"""
    success: bool
    status_code: Optional[int] = None
    response_time: Optional[float] = None  # 响应时间（毫秒）
    response_headers: Optional[dict] = None
    response_body: Optional[str] = None
    request_url: Optional[str] = None  # 实际请求URL
    request_method: Optional[str] = None
    request_headers: Optional[dict] = None  # 实际请求头
    request_body: Optional[str] = None  # 实际请求体
    error_message: Optional[str] = None
