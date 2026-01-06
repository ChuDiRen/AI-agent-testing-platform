"""
核心数据模型 - API自动化测试平台

本模块定义了平台的所有核心数据模型，包括：
- API端点模型
- 测试用例模型
- 测试步骤模型
- 测试结果模型
- 断言模型
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


# ==================== 枚举类型 ====================

class HttpMethod(str, Enum):
    """HTTP请求方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class TestPriority(str, Enum):
    """测试优先级"""
    CRITICAL = "critical"  # 关键
    HIGH = "high"          # 高
    MEDIUM = "medium"      # 中
    LOW = "low"            # 低


class TestType(str, Enum):
    """测试类型"""
    FUNCTIONAL = "functional"      # 功能测试
    SECURITY = "security"          # 安全测试
    PERFORMANCE = "performance"    # 性能测试
    INTEGRATION = "integration"    # 集成测试
    BOUNDARY = "boundary"          # 边界测试
    NEGATIVE = "negative"          # 负面测试


class TestStatus(str, Enum):
    """测试状态"""
    PENDING = "pending"      # 待执行
    RUNNING = "running"      # 执行中
    PASSED = "passed"        # 通过
    FAILED = "failed"        # 失败
    SKIPPED = "skipped"      # 跳过
    ERROR = "error"          # 错误


class AssertionType(str, Enum):
    """断言类型"""
    STATUS_CODE = "status_code"              # 状态码断言
    RESPONSE_TIME = "response_time"          # 响应时间断言
    JSON_PATH = "json_path"                  # JSON路径断言
    JSON_SCHEMA = "json_schema"              # JSON Schema断言
    HEADER = "header"                        # 响应头断言
    BODY_CONTAINS = "body_contains"          # 响应体包含断言
    BODY_EQUALS = "body_equals"              # 响应体相等断言
    REGEX = "regex"                          # 正则表达式断言


class APISchemaType(str, Enum):
    """API文档类型"""
    OPENAPI_3_0 = "openapi_3.0"
    OPENAPI_3_1 = "openapi_3.1"
    SWAGGER_2_0 = "swagger_2.0"
    GRAPHQL = "graphql"
    POSTMAN = "postman"
    CUSTOM = "custom"


# ==================== API相关模型 ====================

class APIParameter(BaseModel):
    """API参数模型"""
    name: str = Field(..., description="参数名称")
    param_in: str = Field(..., description="参数位置: query/path/header/body")
    param_type: str = Field(default="string", description="参数类型")
    required: bool = Field(default=False, description="是否必需")
    description: Optional[str] = Field(default=None, description="参数描述")
    default_value: Optional[Any] = Field(default=None, description="默认值")
    example: Optional[Any] = Field(default=None, description="示例值")
    schema: Optional[Dict[str, Any]] = Field(default=None, description="参数Schema")


class APIEndpoint(BaseModel):
    """API端点模型"""
    endpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="端点ID")
    path: str = Field(..., description="API路径")
    method: HttpMethod = Field(..., description="HTTP方法")
    summary: str = Field(default="", description="API摘要")
    description: str = Field(default="", description="详细描述")
    tags: List[str] = Field(default_factory=list, description="API标签")
    parameters: List[APIParameter] = Field(default_factory=list, description="请求参数")
    request_body: Optional[Dict[str, Any]] = Field(default=None, description="请求体Schema")
    responses: Dict[str, Any] = Field(default_factory=dict, description="响应定义")
    security: List[Dict[str, Any]] = Field(default_factory=list, description="安全要求")
    deprecated: bool = Field(default=False, description="是否已废弃")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class APIDocument(BaseModel):
    """API文档模型"""
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="文档ID")
    title: str = Field(..., description="文档标题")
    version: str = Field(default="1.0.0", description="API版本")
    schema_type: APISchemaType = Field(..., description="文档类型")
    base_url: Optional[str] = Field(default=None, description="基础URL")
    endpoints: List[APIEndpoint] = Field(default_factory=list, description="API端点列表")
    security_schemes: Dict[str, Any] = Field(default_factory=dict, description="安全方案")
    servers: List[Dict[str, Any]] = Field(default_factory=list, description="服务器列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


# ==================== 测试用例模型 ====================

class TestAssertion(BaseModel):
    """测试断言模型"""
    assertion_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="断言ID")
    assertion_type: AssertionType = Field(..., description="断言类型")
    target: str = Field(..., description="断言目标（如JSON路径、响应头名称等）")
    operator: str = Field(..., description="比较操作符: equals/contains/gt/lt/regex等")
    expected_value: Any = Field(..., description="期望值")
    description: Optional[str] = Field(default=None, description="断言描述")


class TestStep(BaseModel):
    """测试步骤模型"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="步骤ID")
    name: str = Field(..., description="步骤名称")
    description: str = Field(default="", description="步骤描述")
    endpoint: str = Field(..., description="API端点路径")
    method: HttpMethod = Field(..., description="HTTP方法")
    headers: Dict[str, str] = Field(default_factory=dict, description="请求头")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="查询参数")
    path_params: Dict[str, Any] = Field(default_factory=dict, description="路径参数")
    request_body: Optional[Any] = Field(default=None, description="请求体")
    assertions: List[TestAssertion] = Field(default_factory=list, description="断言列表")
    extract_variables: Dict[str, str] = Field(default_factory=dict, description="提取变量（变量名: JSONPath）")
    depends_on: List[str] = Field(default_factory=list, description="依赖的步骤ID列表")
    timeout: int = Field(default=30000, description="超时时间（毫秒）")
    retry_count: int = Field(default=0, description="重试次数")


class TestCase(BaseModel):
    """测试用例模型"""
    case_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="用例ID")
    name: str = Field(..., description="用例名称")
    description: str = Field(default="", description="用例描述")
    priority: TestPriority = Field(default=TestPriority.MEDIUM, description="优先级")
    test_type: TestType = Field(default=TestType.FUNCTIONAL, description="测试类型")
    tags: List[str] = Field(default_factory=list, description="标签")
    preconditions: List[str] = Field(default_factory=list, description="前置条件")
    steps: List[TestStep] = Field(default_factory=list, description="测试步骤")
    setup_steps: List[TestStep] = Field(default_factory=list, description="Setup步骤")
    teardown_steps: List[TestStep] = Field(default_factory=list, description="Teardown步骤")
    expected_result: str = Field(default="", description="预期结果")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class TestSuite(BaseModel):
    """测试套件模型"""
    suite_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="套件ID")
    name: str = Field(..., description="套件名称")
    description: str = Field(default="", description="套件描述")
    test_cases: List[TestCase] = Field(default_factory=list, description="测试用例列表")
    tags: List[str] = Field(default_factory=list, description="标签")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


# ==================== 测试结果模型 ====================

class AssertionResult(BaseModel):
    """断言结果模型"""
    assertion_id: str = Field(..., description="断言ID")
    assertion_type: AssertionType = Field(..., description="断言类型")
    target: str = Field(..., description="断言目标")
    expected_value: Any = Field(..., description="期望值")
    actual_value: Any = Field(..., description="实际值")
    passed: bool = Field(..., description="是否通过")
    error_message: Optional[str] = Field(default=None, description="错误信息")


class StepResult(BaseModel):
    """测试步骤结果模型"""
    step_id: str = Field(..., description="步骤ID")
    step_name: str = Field(..., description="步骤名称")
    status: TestStatus = Field(..., description="执行状态")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    duration_ms: float = Field(..., description="执行耗时（毫秒）")
    request: Dict[str, Any] = Field(default_factory=dict, description="请求详情")
    response: Dict[str, Any] = Field(default_factory=dict, description="响应详情")
    assertion_results: List[AssertionResult] = Field(default_factory=list, description="断言结果")
    extracted_variables: Dict[str, Any] = Field(default_factory=dict, description="提取的变量")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    error_stack: Optional[str] = Field(default=None, description="错误堆栈")


class CaseResult(BaseModel):
    """测试用例结果模型"""
    case_id: str = Field(..., description="用例ID")
    case_name: str = Field(..., description="用例名称")
    status: TestStatus = Field(..., description="执行状态")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    duration_ms: float = Field(..., description="执行耗时（毫秒）")
    step_results: List[StepResult] = Field(default_factory=list, description="步骤结果")
    total_steps: int = Field(default=0, description="总步骤数")
    passed_steps: int = Field(default=0, description="通过步骤数")
    failed_steps: int = Field(default=0, description="失败步骤数")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    screenshots: List[str] = Field(default_factory=list, description="截图路径列表")
    logs: List[str] = Field(default_factory=list, description="日志列表")


class SuiteResult(BaseModel):
    """测试套件结果模型"""
    suite_id: str = Field(..., description="套件ID")
    suite_name: str = Field(..., description="套件名称")
    status: TestStatus = Field(..., description="执行状态")
    total_cases: int = Field(default=0, description="总用例数")
    passed_cases: int = Field(default=0, description="通过用例数")
    failed_cases: int = Field(default=0, description="失败用例数")
    skipped_cases: int = Field(default=0, description="跳过用例数")
    duration_ms: float = Field(default=0.0, description="执行耗时（毫秒）")
    case_results: List[CaseResult] = Field(default_factory=list, description="用例结果")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    environment: Dict[str, Any] = Field(default_factory=dict, description="执行环境信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


# ==================== 测试计划模型 ====================

class TestPlan(BaseModel):
    """测试计划模型"""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="计划ID")
    name: str = Field(..., description="计划名称")
    description: str = Field(default="", description="计划描述")
    api_document_id: str = Field(..., description="关联的API文档ID")
    test_suites: List[TestSuite] = Field(default_factory=list, description="测试套件列表")
    test_categories: List[TestType] = Field(default_factory=list, description="测试类别")
    coverage_summary: Dict[str, Any] = Field(default_factory=dict, description="覆盖率摘要")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


# ==================== 代码生成模型 ====================

class GeneratedTestFile(BaseModel):
    """生成的测试文件模型"""
    file_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="文件ID")
    file_name: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件路径")
    framework: str = Field(..., description="测试框架: playwright/jest/postman")
    language: str = Field(..., description="编程语言: typescript/javascript/python")
    content: str = Field(..., description="文件内容")
    test_case_ids: List[str] = Field(default_factory=list, description="包含的测试用例ID列表")
    dependencies: List[str] = Field(default_factory=list, description="依赖的包列表")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")


class CodeGenerationResult(BaseModel):
    """代码生成结果模型"""
    generation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="生成ID")
    test_plan_id: str = Field(..., description="测试计划ID")
    framework: str = Field(..., description="测试框架")
    language: str = Field(..., description="编程语言")
    generated_files: List[GeneratedTestFile] = Field(default_factory=list, description="生成的文件列表")
    config_files: List[GeneratedTestFile] = Field(default_factory=list, description="配置文件列表")
    total_files: int = Field(default=0, description="总文件数")
    total_lines: int = Field(default=0, description="总代码行数")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


# ==================== 会话和任务模型 ====================

class SessionStatus(str, Enum):
    """会话状态"""
    ACTIVE = "active"        # 活跃
    COMPLETED = "completed"  # 完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 取消


class TestSession(BaseModel):
    """测试会话模型"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="会话ID")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    test_plan_id: Optional[str] = Field(default=None, description="测试计划ID")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE, description="会话状态")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    variables: Dict[str, Any] = Field(default_factory=dict, description="会话变量")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"      # 待处理
    RUNNING = "running"      # 运行中
    COMPLETED = "completed"  # 完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 取消


class AgentTask(BaseModel):
    """智能体任务模型"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="任务ID")
    task_type: str = Field(..., description="任务类型: rag_retrieval/test_planning/test_generation等")
    user_request: str = Field(..., description="用户请求")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    progress: float = Field(default=0.0, description="进度百分比 0-100")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="输入数据")
    output_data: Optional[Dict[str, Any]] = Field(default=None, description="输出数据")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


# ==================== RAG检索模型 ====================

class RAGEntity(BaseModel):
    """RAG实体模型"""
    entity_id: str = Field(..., description="实体ID")
    entity_name: str = Field(..., description="实体名称")
    entity_type: str = Field(..., description="实体类型: API_ENDPOINT/PARAMETER/SCHEMA等")
    description: str = Field(default="", description="实体描述")
    properties: Dict[str, Any] = Field(default_factory=dict, description="实体属性")
    confidence: float = Field(default=1.0, description="置信度 0-1")


class RAGRelationship(BaseModel):
    """RAG关系模型"""
    relationship_id: str = Field(..., description="关系ID")
    source_id: str = Field(..., description="源实体ID")
    target_id: str = Field(..., description="目标实体ID")
    relationship_type: str = Field(..., description="关系类型: DEPENDS_ON/RETURNS/REQUIRES等")
    description: str = Field(default="", description="关系描述")
    properties: Dict[str, Any] = Field(default_factory=dict, description="关系属性")


class RAGChunk(BaseModel):
    """RAG文本块模型"""
    chunk_id: str = Field(..., description="文本块ID")
    content: str = Field(..., description="文本内容")
    source: str = Field(..., description="来源文档")
    chunk_type: str = Field(default="text", description="块类型: text/code/table等")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    score: float = Field(default=0.0, description="相关性分数")


class RAGCitation(BaseModel):
    """RAG引用模型"""
    citation_id: str = Field(..., description="引用ID")
    source_document: str = Field(..., description="源文档")
    page_number: Optional[int] = Field(default=None, description="页码")
    section: Optional[str] = Field(default=None, description="章节")
    content_snippet: str = Field(..., description="内容片段")


class RAGQueryResult(BaseModel):
    """RAG查询结果模型"""
    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="查询ID")
    query: str = Field(..., description="查询文本")
    mode: str = Field(..., description="检索模式: local/global/hybrid/naive/mix/bypass")
    entities: List[RAGEntity] = Field(default_factory=list, description="实体列表")
    relationships: List[RAGRelationship] = Field(default_factory=list, description="关系列表")
    chunks: List[RAGChunk] = Field(default_factory=list, description="文本块列表")
    citations: List[RAGCitation] = Field(default_factory=list, description="引用列表")
    confidence: float = Field(default=0.0, description="整体置信度")
    processing_time_ms: float = Field(default=0.0, description="处理时间（毫秒）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


# ==================== 工具函数 ====================

def generate_id(prefix: str = "") -> str:
    """生成唯一ID"""
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id


def calculate_duration_ms(start_time: datetime, end_time: datetime) -> float:
    """计算时间差（毫秒）"""
    delta = end_time - start_time
    return delta.total_seconds() * 1000


# ==================== 模型导出 ====================

__all__ = [
    # 枚举类型
    "HttpMethod",
    "TestPriority",
    "TestType",
    "TestStatus",
    "AssertionType",
    "APISchemaType",
    "SessionStatus",
    "TaskStatus",

    # API模型
    "APIParameter",
    "APIEndpoint",
    "APIDocument",

    # 测试用例模型
    "TestAssertion",
    "TestStep",
    "TestCase",
    "TestSuite",
    "TestPlan",

    # 测试结果模型
    "AssertionResult",
    "StepResult",
    "CaseResult",
    "SuiteResult",

    # 代码生成模型
    "GeneratedTestFile",
    "CodeGenerationResult",

    # 会话和任务模型
    "TestSession",
    "AgentTask",

    # RAG模型
    "RAGEntity",
    "RAGRelationship",
    "RAGChunk",
    "RAGCitation",
    "RAGQueryResult",

    # 工具函数
    "generate_id",
    "calculate_duration_ms",
]
