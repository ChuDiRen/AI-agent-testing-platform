"""
AI代理管理DTO
定义AI代理相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field, validator

from .base import BaseRequest, BaseResponse, PaginationRequest, SearchRequest


class AgentTypeEnum(str, Enum):
    """代理类型枚举"""
    CHAT = "chat"
    TASK = "task"
    ANALYSIS = "analysis"
    TESTING = "testing"
    CUSTOM = "custom"


class AgentStatusEnum(str, Enum):
    """代理状态枚举"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"


# 请求DTO
class AgentCreateRequest(BaseRequest):
    """创建代理请求DTO"""
    name: str = Field(..., min_length=1, max_length=100, description="代理名称")
    type: AgentTypeEnum = Field(default=AgentTypeEnum.CHAT, description="代理类型")
    description: Optional[str] = Field(None, max_length=500, description="代理描述")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="代理配置")
    version: Optional[str] = Field(default="1.0.0", max_length=20, description="代理版本")

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('代理名称不能为空')
        return v

    @validator('config')
    def validate_config(cls, v):
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError('代理配置必须是字典格式')
        return v


class AgentUpdateRequest(BaseRequest):
    """更新代理请求DTO"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="代理名称")
    type: Optional[AgentTypeEnum] = Field(None, description="代理类型")
    description: Optional[str] = Field(None, max_length=500, description="代理描述")
    config: Optional[Dict[str, Any]] = Field(None, description="代理配置")
    version: Optional[str] = Field(None, max_length=20, description="代理版本")

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('代理名称不能为空')
        return v


class AgentSearchRequest(SearchRequest):
    """代理搜索请求DTO"""
    type: Optional[AgentTypeEnum] = Field(None, description="代理类型筛选")
    status: Optional[AgentStatusEnum] = Field(None, description="代理状态筛选")
    created_by_id: Optional[int] = Field(None, description="创建者ID筛选")
    start_date: Optional[datetime] = Field(None, description="创建时间开始")
    end_date: Optional[datetime] = Field(None, description="创建时间结束")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError('结束时间必须大于开始时间')
        return v


class AgentStatusUpdateRequest(BaseRequest):
    """代理状态更新请求DTO"""
    status: AgentStatusEnum = Field(..., description="目标状态")


class AgentConfigUpdateRequest(BaseRequest):
    """代理配置更新请求DTO"""
    config: Dict[str, Any] = Field(..., description="配置信息")

    @validator('config')
    def validate_config(cls, v):
        if not isinstance(v, dict):
            raise ValueError('配置信息必须是字典格式')
        return v


class AgentBatchOperationRequest(BaseRequest):
    """代理批量操作请求DTO"""
    agent_ids: List[int] = Field(..., min_items=1, max_items=100, description="代理ID列表")
    operation: str = Field(..., description="操作类型: activate, deactivate, delete")

    @validator('agent_ids')
    def validate_agent_ids(cls, v):
        return sorted(list(set(v)))  # 去重并排序

    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['activate', 'deactivate', 'delete', 'start', 'stop']
        if v not in allowed_operations:
            raise ValueError(f'不支持的操作类型: {v}')
        return v


# 响应DTO
class AgentResponse(BaseResponse):
    """代理响应DTO"""
    id: int = Field(description="代理ID")
    name: str = Field(description="代理名称")
    type: str = Field(description="代理类型")
    description: Optional[str] = Field(description="代理描述")
    status: str = Field(description="代理状态")
    config: Dict[str, Any] = Field(description="代理配置")
    version: str = Field(description="代理版本")
    created_by_id: int = Field(description="创建者ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(description="更新时间")
    last_run_time: Optional[datetime] = Field(description="最后运行时间")
    run_count: int = Field(description="运行次数")
    success_count: int = Field(description="成功次数")
    error_count: int = Field(description="错误次数")
    success_rate: float = Field(description="成功率")
    error_rate: float = Field(description="错误率")


class AgentListResponse(BaseResponse):
    """代理列表响应DTO"""
    agents: List[AgentResponse] = Field(description="代理列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页")
    page_size: int = Field(description="页大小")
    total_pages: int = Field(description="总页数")


class AgentStatisticsResponse(BaseResponse):
    """代理统计响应DTO"""
    total_agents: int = Field(description="代理总数")
    active_agents: int = Field(description="激活代理数")
    running_agents: int = Field(description="运行中代理数")
    error_agents: int = Field(description="错误状态代理数")
    total_runs: int = Field(description="总运行次数")
    total_success: int = Field(description="总成功次数")
    total_errors: int = Field(description="总错误次数")
    overall_success_rate: float = Field(description="整体成功率")
    
    agents_by_type: Dict[str, int] = Field(description="按类型统计")
    agents_by_status: Dict[str, int] = Field(description="按状态统计")
    recent_activity: List[Dict[str, Any]] = Field(description="最近活动")


class AgentConfigItemResponse(BaseResponse):
    """代理配置项响应DTO"""
    id: int = Field(description="配置项ID")
    agent_id: int = Field(description="代理ID")
    config_key: str = Field(description="配置键")
    config_value: Optional[str] = Field(description="配置值")
    config_type: str = Field(description="配置类型")
    description: Optional[str] = Field(description="配置描述")
    is_required: bool = Field(description="是否必填")
    is_enabled: bool = Field(description="是否启用")
    default_value: Optional[str] = Field(description="默认值")
    display_order: int = Field(description="显示顺序")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(description="更新时间")


class AgentConfigListResponse(BaseResponse):
    """代理配置列表响应DTO"""
    configs: List[AgentConfigItemResponse] = Field(description="配置列表")
    agent_id: int = Field(description="代理ID")


# 代理配置相关DTO
class ConfigTypeEnum(str, Enum):
    """配置类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    SECRET = "secret"


class AgentConfigCreateRequest(BaseRequest):
    """创建代理配置请求DTO"""
    config_key: str = Field(..., min_length=1, max_length=100, description="配置键")
    config_value: Optional[str] = Field(None, description="配置值")
    config_type: ConfigTypeEnum = Field(default=ConfigTypeEnum.STRING, description="配置类型")
    description: Optional[str] = Field(None, max_length=500, description="配置描述")
    is_required: bool = Field(default=False, description="是否必填")
    is_enabled: bool = Field(default=True, description="是否启用")
    default_value: Optional[str] = Field(None, description="默认值")
    validation_rules: Optional[str] = Field(None, description="验证规则")
    display_order: int = Field(default=0, description="显示顺序")

    @validator('config_key')
    def validate_config_key(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('配置键不能为空')
        return v


class AgentConfigUpdateRequest(BaseRequest):
    """更新代理配置请求DTO"""
    config_value: Optional[str] = Field(None, description="配置值")
    description: Optional[str] = Field(None, max_length=500, description="配置描述")
    is_required: Optional[bool] = Field(None, description="是否必填")
    is_enabled: Optional[bool] = Field(None, description="是否启用")
    default_value: Optional[str] = Field(None, description="默认值")
    validation_rules: Optional[str] = Field(None, description="验证规则")
    display_order: Optional[int] = Field(None, description="显示顺序")


class AgentConfigSearchRequest(PaginationRequest):
    """代理配置搜索请求DTO"""
    agent_id: int = Field(..., description="代理ID")
    config_type: Optional[ConfigTypeEnum] = Field(None, description="配置类型筛选")
    is_required: Optional[bool] = Field(None, description="是否必填筛选")
    is_enabled: Optional[bool] = Field(None, description="是否启用筛选")
    keyword: Optional[str] = Field(None, description="关键词搜索")


# 批量操作响应
class AgentBatchOperationResponse(BaseResponse):
    """代理批量操作响应DTO"""
    total: int = Field(description="总操作数")
    success_count: int = Field(description="成功数")
    failed_count: int = Field(description="失败数")
    failed_ids: List[int] = Field(description="失败的代理ID列表")
    errors: List[str] = Field(description="错误信息列表")
    success_rate: float = Field(description="成功率")


# 导出所有DTO类
__all__ = [
    # 枚举
    "AgentTypeEnum",
    "AgentStatusEnum",
    "ConfigTypeEnum",
    
    # 请求DTO
    "AgentCreateRequest",
    "AgentUpdateRequest",
    "AgentSearchRequest",
    "AgentStatusUpdateRequest",
    "AgentConfigUpdateRequest",
    "AgentBatchOperationRequest",
    "AgentConfigCreateRequest",
    "AgentConfigUpdateRequest",
    "AgentConfigSearchRequest",
    
    # 响应DTO
    "AgentResponse",
    "AgentListResponse",
    "AgentStatisticsResponse",
    "AgentConfigItemResponse",
    "AgentConfigListResponse",
    "AgentBatchOperationResponse",
]
