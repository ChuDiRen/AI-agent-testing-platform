"""
测试执行相关的数据模型
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class QuickApiTestRequest(BaseModel):
    """快速 API 测试请求"""
    url: str = Field(..., description="请求 URL")
    method: str = Field(default="GET", description="HTTP 方法")
    headers: Optional[Dict[str, str]] = Field(default=None, description="请求头")
    params: Optional[Dict[str, Any]] = Field(default=None, description="URL 参数")
    data: Optional[Dict[str, Any]] = Field(default=None, description="表单数据")
    json_body: Optional[Dict[str, Any]] = Field(default=None, description="JSON 请求体")
    expected_status: int = Field(default=200, description="期望状态码")
    expected_contains: Optional[str] = Field(default=None, description="期望响应包含的文本")
    expected_json: Optional[Dict[str, Any]] = Field(default=None, description="期望的 JSON 字段值，如 {'$.code': 0}")
    max_response_time_ms: Optional[int] = Field(default=None, description="最大响应时间（毫秒）")


class RunCaseRequest(BaseModel):
    """运行测试用例请求"""
    engine_type: str = Field(..., description="引擎类型: api/web/mobile/perf")
    case_content: Dict[str, Any] = Field(..., description="用例内容（YAML 解析后的字典）")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文变量")


class RunCaseFileRequest(BaseModel):
    """运行用例文件请求"""
    case_file_path: str = Field(..., description="用例文件路径")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文变量")


class RunDirectoryRequest(BaseModel):
    """运行目录测试请求"""
    cases_dir: str = Field(..., description="用例目录路径")
    engine_type: Optional[str] = Field(default=None, description="引擎类型（可选，会自动检测）")
    case_type: str = Field(default="yaml", description="用例格式: yaml/pytest")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文变量")


class RunBatchRequest(BaseModel):
    """批量运行测试请求"""
    engine_type: str = Field(..., description="引擎类型: api/web/mobile/perf")
    cases: List[Dict[str, Any]] = Field(..., description="用例列表")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文变量")
