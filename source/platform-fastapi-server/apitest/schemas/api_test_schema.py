from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# 测试历史查询Schema
class ApiTestHistoryQuery(BaseModel):
    page: int = 1
    pageSize: int = 10
    api_info_id: Optional[int] = None
    project_id: Optional[int] = None
    test_status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

# 测试执行请求Schema
class ApiTestExecuteRequest(BaseModel):
    api_info_id: int
    test_name: Optional[str] = None
    context_vars: Optional[Dict[str, Any]] = {}  # 上下文变量
    pre_script: Optional[List[str]] = []         # 前置脚本列表
    post_script: Optional[List[str]] = []        # 后置脚本列表
    assertions: Optional[List[Dict]] = []        # 断言配置列表
    
# 断言配置Schema
class AssertionConfig(BaseModel):
    type: str  # assert_text_comparators, assert_json_path等
    extract_path: Optional[str] = None  # JSONPath提取路径
    expected_value: str  # 期望值
    operator: str = "=="  # 比较操作符
    description: Optional[str] = None  # 断言描述

# 变量提取配置Schema
class VariableExtract(BaseModel):
    var_name: str  # 变量名
    extract_path: str  # JSONPath提取路径
    index: int = 0  # 提取索引
    description: Optional[str] = None

# 测试结果Schema
class ApiTestResult(BaseModel):
    test_id: int
    test_status: str
    response_time: Optional[int] = None
    status_code: Optional[int] = None
    response_data: Optional[Dict] = None
    error_message: Optional[str] = None
    allure_report_url: Optional[str] = None

# 测试历史响应Schema
class ApiTestHistoryResponse(BaseModel):
    id: int
    api_info_id: int
    project_id: int
    test_name: str
    test_status: str
    request_data: Optional[str] = None
    response_data: Optional[str] = None
    response_time: Optional[int] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    allure_report_path: Optional[str] = None
    yaml_content: Optional[str] = None
    execution_log: Optional[str] = None
    create_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None

# YAML用例生成配置Schema
class YamlGenerateConfig(BaseModel):
    api_info_id: int
    test_name: str
    context_vars: Optional[Dict[str, Any]] = {}
    pre_script: Optional[List[str]] = []
    post_script: Optional[List[str]] = []
    variable_extracts: Optional[List[VariableExtract]] = []
    assertions: Optional[List[AssertionConfig]] = []
