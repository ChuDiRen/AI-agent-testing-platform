from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


# 变量提取配置Schema
class VariableExtract(BaseModel):
    var_name: str  # 变量名
    extract_path: str  # JSONPath提取路径
    index: int = 0  # 提取索引
    description: Optional[str] = None

# 断言配置Schema
class AssertionConfig(BaseModel):
    type: str  # assert_text_comparators, assert_json_path等
    extract_path: Optional[str] = None  # JSONPath提取路径
    expected_value: str  # 期望值
    operator: str = "=="  # 比较操作符
    description: Optional[str] = None  # 断言描述

# API测试执行请求Schema
class ApiTestExecuteRequest(BaseModel):
    api_info_id: int
    test_name: Optional[str] = None
    context_vars: Optional[Dict[str, Any]] = {}  # 上下文变量
    pre_script: Optional[List[str]] = []         # 前置脚本列表
    post_script: Optional[List[str]] = []        # 后置脚本列表
    variable_extracts: Optional[List[VariableExtract]] = []  # 变量提取配置列表
    assertions: Optional[List[Dict]] = []        # 断言配置列表

# 测试状态查询Schema
class ApiTestStatusRequest(BaseModel):
    test_id: int

# 测试结果Schema
class ApiTestResult(BaseModel):
    test_id: int
    test_status: str
    response_time: Optional[int] = None
    status_code: Optional[int] = None
    response_data: Optional[Dict] = None
    error_message: Optional[str] = None
    allure_report_url: Optional[str] = None

# 引擎健康检查响应Schema
class EngineHealthResponse(BaseModel):
    status: str
    message: Optional[str] = None
    version: Optional[str] = None
