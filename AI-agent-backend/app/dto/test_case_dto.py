"""
测试用例DTO
定义测试用例相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field, validator

from .base import BaseRequest, BaseResponse, PaginationRequest, SearchRequest


class TestCaseStatusEnum(str, Enum):
    """测试用例状态枚举"""
    DRAFT = "draft"
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class TestCasePriorityEnum(str, Enum):
    """测试用例优先级枚举"""
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"


class TestCaseTypeEnum(str, Enum):
    """测试用例类型枚举"""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UI = "ui"
    API = "api"
    INTEGRATION = "integration"
    UNIT = "unit"


# 请求DTO
class TestCaseCreateRequest(BaseRequest):
    """创建测试用例请求DTO"""
    name: str = Field(..., min_length=1, max_length=200, description="用例名称")
    module: Optional[str] = Field(None, max_length=100, description="所属模块")
    description: Optional[str] = Field(None, description="用例描述")
    preconditions: Optional[str] = Field(None, description="前置条件")
    test_steps: Optional[str] = Field(None, description="测试步骤")
    expected_result: Optional[str] = Field(None, description="预期结果")
    priority: TestCasePriorityEnum = Field(default=TestCasePriorityEnum.P3, description="用例优先级")
    test_type: TestCaseTypeEnum = Field(default=TestCaseTypeEnum.FUNCTIONAL, description="用例类型")
    tags: Optional[str] = Field(None, max_length=200, description="标签")
    agent_id: Optional[int] = Field(None, description="关联的代理ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="附加数据")

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('用例名称不能为空')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class TestCaseUpdateRequest(BaseRequest):
    """更新测试用例请求DTO"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="用例名称")
    module: Optional[str] = Field(None, max_length=100, description="所属模块")
    description: Optional[str] = Field(None, description="用例描述")
    preconditions: Optional[str] = Field(None, description="前置条件")
    test_steps: Optional[str] = Field(None, description="测试步骤")
    expected_result: Optional[str] = Field(None, description="预期结果")
    priority: Optional[TestCasePriorityEnum] = Field(None, description="用例优先级")
    test_type: Optional[TestCaseTypeEnum] = Field(None, description="用例类型")
    tags: Optional[str] = Field(None, max_length=200, description="标签")

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('用例名称不能为空')
        return v


class TestCaseSearchRequest(SearchRequest):
    """测试用例搜索请求DTO"""
    module: Optional[str] = Field(None, description="模块筛选")
    status: Optional[TestCaseStatusEnum] = Field(None, description="状态筛选")
    priority: Optional[TestCasePriorityEnum] = Field(None, description="优先级筛选")
    test_type: Optional[TestCaseTypeEnum] = Field(None, description="类型筛选")
    agent_id: Optional[int] = Field(None, description="代理ID筛选")
    created_by_id: Optional[int] = Field(None, description="创建者ID筛选")
    executor_id: Optional[int] = Field(None, description="执行者ID筛选")
    tags: Optional[str] = Field(None, description="标签筛选")
    start_date: Optional[datetime] = Field(None, description="创建时间开始")
    end_date: Optional[datetime] = Field(None, description="创建时间结束")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError('结束时间必须大于开始时间')
        return v


class TestCaseExecutionRequest(BaseRequest):
    """测试用例执行请求DTO"""
    executor_id: Optional[int] = Field(None, description="执行者ID")
    actual_result: Optional[str] = Field(None, description="实际结果")
    remarks: Optional[str] = Field(None, description="备注")


class TestCaseBatchOperationRequest(BaseRequest):
    """测试用例批量操作请求DTO"""
    test_case_ids: List[int] = Field(..., min_items=1, max_items=100, description="测试用例ID列表")
    operation: str = Field(..., description="操作类型")
    operation_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="操作数据")

    @validator('test_case_ids')
    def validate_test_case_ids(cls, v):
        return sorted(list(set(v)))  # 去重并排序

    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['set_pending', 'set_running', 'set_passed', 'set_failed', 
                             'set_skipped', 'set_blocked', 'delete', 'update_priority', 
                             'update_type', 'add_tag', 'remove_tag']
        if v not in allowed_operations:
            raise ValueError(f'不支持的操作类型: {v}')
        return v


# AI测试用例生成相关DTO
class TestCaseGenerationRequest(BaseRequest):
    """AI测试用例生成请求DTO"""
    requirements_document: str = Field(..., min_length=10, description="需求文档内容")
    agent_id: Optional[int] = Field(None, description="指定使用的AI代理")
    generation_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="生成配置")
    target_module: Optional[str] = Field(None, description="目标模块")
    test_types: Optional[List[TestCaseTypeEnum]] = Field(None, description="指定测试类型")
    priority_levels: Optional[List[TestCasePriorityEnum]] = Field(None, description="指定优先级")
    max_cases: int = Field(default=50, ge=1, le=200, description="最大生成用例数")
    include_edge_cases: bool = Field(default=True, description="是否包含边界用例")
    include_negative_cases: bool = Field(default=True, description="是否包含负面用例")

    @validator('requirements_document')
    def validate_requirements_document(cls, v):
        v = v.strip()
        if len(v) < 10:
            raise ValueError('需求文档内容太短，至少需要10个字符')
        return v


class TestCaseGenerationResponse(BaseResponse):
    """AI测试用例生成响应DTO"""
    generation_id: str = Field(description="生成任务ID")
    status: str = Field(description="生成状态")
    total_generated: int = Field(description="总生成数量")
    generated_cases: List[Dict[str, Any]] = Field(description="生成的测试用例")


# 生成历史相关DTO
class GenerationHistoryStatusEnum(str, Enum):
    """生成历史状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TestCaseGenerationHistoryRequest(PaginationRequest):
    """测试用例生成历史请求DTO"""
    user_id: Optional[int] = Field(None, description="用户ID")
    status: Optional[GenerationHistoryStatusEnum] = Field(None, description="生成状态")
    test_type: Optional[TestCaseTypeEnum] = Field(None, description="测试类型")


class TestCaseGenerationHistoryItem(BaseModel):
    """测试用例生成历史项DTO"""
    id: int = Field(description="历史记录ID")
    task_id: str = Field(description="生成任务ID")
    requirement_text: str = Field(description="需求描述")
    requirement_summary: str = Field(description="需求摘要")
    test_type: str = Field(description="测试类型")
    priority: str = Field(description="优先级")
    generated_count: int = Field(description="生成数量")
    status: str = Field(description="生成状态")
    created_at: str = Field(description="创建时间")
    updated_at: str = Field(description="更新时间")


class TestCaseGenerationHistoryResponse(BaseResponse):
    """测试用例生成历史响应DTO"""
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    history: List[TestCaseGenerationHistoryItem] = Field(description="历史记录列表")
    generation_time: float = Field(description="生成耗时(秒)")
    agent_used: Optional[str] = Field(description="使用的AI代理")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
    errors: List[str] = Field(default_factory=list, description="错误信息")


# 响应DTO
class TestCaseResponse(BaseResponse):
    """测试用例响应DTO"""
    id: int = Field(description="用例ID")
    name: str = Field(description="用例名称")
    module: Optional[str] = Field(description="所属模块")
    description: Optional[str] = Field(description="用例描述")
    preconditions: Optional[str] = Field(description="前置条件")
    test_steps: Optional[str] = Field(description="测试步骤")
    expected_result: Optional[str] = Field(description="预期结果")
    actual_result: Optional[str] = Field(description="实际结果")
    status: str = Field(description="用例状态")
    priority: str = Field(description="用例优先级")
    test_type: str = Field(description="用例类型")
    tags: Optional[str] = Field(description="标签")
    tags_list: List[str] = Field(description="标签列表")
    agent_id: Optional[int] = Field(description="关联的代理ID")
    created_by_id: int = Field(description="创建者ID")
    executor_id: Optional[int] = Field(description="执行者ID")
    executed_at: Optional[datetime] = Field(description="执行时间")
    execution_time: Optional[float] = Field(description="执行耗时")
    remarks: Optional[str] = Field(description="备注")
    metadata: Dict[str, Any] = Field(description="附加数据")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(description="更新时间")


class TestCaseListResponse(BaseResponse):
    """测试用例列表响应DTO"""
    test_cases: List[TestCaseResponse] = Field(description="测试用例列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页")
    page_size: int = Field(description="页大小")
    total_pages: int = Field(description="总页数")


class TestCaseStatisticsResponse(BaseResponse):
    """测试用例统计响应DTO"""
    total_cases: int = Field(description="用例总数")
    draft_cases: int = Field(description="草稿用例数")
    pending_cases: int = Field(description="待执行用例数")
    running_cases: int = Field(description="执行中用例数")
    passed_cases: int = Field(description="通过用例数")
    failed_cases: int = Field(description="失败用例数")
    skipped_cases: int = Field(description="跳过用例数")
    blocked_cases: int = Field(description="阻塞用例数")
    
    cases_by_priority: Dict[str, int] = Field(description="按优先级统计")
    cases_by_type: Dict[str, int] = Field(description="按类型统计")
    cases_by_module: Dict[str, int] = Field(description="按模块统计")
    
    execution_rate: float = Field(description="执行率")
    pass_rate: float = Field(description="通过率")
    avg_execution_time: float = Field(description="平均执行时间")


class TestCaseBatchOperationResponse(BaseResponse):
    """测试用例批量操作响应DTO"""
    total: int = Field(description="总操作数")
    success_count: int = Field(description="成功数")
    failed_count: int = Field(description="失败数")
    failed_ids: List[int] = Field(description="失败的用例ID列表")
    errors: List[str] = Field(description="错误信息列表")
    success_rate: float = Field(description="成功率")


# 导出所有DTO类
__all__ = [
    # 枚举
    "TestCaseStatusEnum",
    "TestCasePriorityEnum",
    "TestCaseTypeEnum",
    
    # 请求DTO
    "TestCaseCreateRequest",
    "TestCaseUpdateRequest",
    "TestCaseSearchRequest",
    "TestCaseExecutionRequest",
    "TestCaseBatchOperationRequest",
    "TestCaseGenerationRequest",
    
    # 响应DTO
    "TestCaseResponse",
    "TestCaseListResponse",
    "TestCaseStatisticsResponse",
    "TestCaseBatchOperationResponse",
    "TestCaseGenerationResponse",

    # 生成历史相关DTO
    "GenerationHistoryStatusEnum",
    "TestCaseGenerationHistoryRequest",
    "TestCaseGenerationHistoryItem",
    "TestCaseGenerationHistoryResponse",
]
