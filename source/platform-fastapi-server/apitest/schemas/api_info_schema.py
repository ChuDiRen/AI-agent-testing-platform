from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
    create_time: Optional[datetime] = None
