# Copyright (c) 2025 左岚. All rights reserved.
"""
AI模型DTO
定义AI模型相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field, validator

from .base import BaseRequest, BaseResponse, PaginationRequest, SearchRequest


class ModelProviderEnum(str, Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    QIANWEN = "qianwen"
    BAIDU = "baidu"
    GOOGLE = "google"
    CUSTOM = "custom"


class ModelTypeEnum(str, Enum):
    """模型类型枚举"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE = "image"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"


class ModelStatusEnum(str, Enum):
    """模型状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"


# 请求DTO
class AIModelCreateRequest(BaseRequest):
    """创建AI模型请求DTO"""
    model_config = {"protected_namespaces": ()}  # 禁用保护命名空间警告

    name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    display_name: Optional[str] = Field(None, max_length=100, description="模型显示名称")
    provider: ModelProviderEnum = Field(..., description="模型提供商")
    model_type: ModelTypeEnum = Field(default=ModelTypeEnum.CHAT, description="模型类型")
    version: Optional[str] = Field(None, max_length=20, description="模型版本")
    description: Optional[str] = Field(None, description="模型描述")
    api_endpoint: Optional[str] = Field(None, max_length=500, description="API端点")
    api_key: Optional[str] = Field(None, max_length=500, description="API密钥")
    max_tokens: int = Field(default=4096, ge=1, le=1000000, description="最大令牌数")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    pricing: Optional[Dict[str, Any]] = Field(default_factory=dict, description="费用信息")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="模型配置")

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('模型名称不能为空')
        return v

    @validator('api_endpoint')
    def validate_api_endpoint(cls, v):
        if v is not None:
            v = v.strip()
            if v and not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('API端点必须以http://或https://开头')
        return v


class AIModelUpdateRequest(BaseRequest):
    """更新AI模型请求DTO"""
    display_name: Optional[str] = Field(None, max_length=100, description="模型显示名称")
    description: Optional[str] = Field(None, description="模型描述")
    version: Optional[str] = Field(None, max_length=20, description="模型版本")
    api_endpoint: Optional[str] = Field(None, max_length=500, description="API端点")
    api_key: Optional[str] = Field(None, max_length=500, description="API密钥")
    max_tokens: Optional[int] = Field(None, ge=1, le=1000000, description="最大令牌数")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="温度参数")
    pricing: Optional[Dict[str, Any]] = Field(None, description="费用信息")
    config: Optional[Dict[str, Any]] = Field(None, description="模型配置")

    @validator('api_endpoint')
    def validate_api_endpoint(cls, v):
        if v is not None:
            v = v.strip()
            if v and not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('API端点必须以http://或https://开头')
        return v


class AIModelSearchRequest(SearchRequest):
    """AI模型搜索请求DTO"""
    model_config = {"protected_namespaces": ()}  # 禁用保护命名空间警告

    provider: Optional[ModelProviderEnum] = Field(None, description="提供商筛选")
    model_type: Optional[ModelTypeEnum] = Field(None, description="类型筛选")
    status: Optional[ModelStatusEnum] = Field(None, description="状态筛选")
    created_by_id: Optional[int] = Field(None, description="创建者ID筛选")
    start_date: Optional[datetime] = Field(None, description="创建时间开始")
    end_date: Optional[datetime] = Field(None, description="创建时间结束")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError('结束时间必须大于开始时间')
        return v


class AIModelStatusUpdateRequest(BaseRequest):
    """AI模型状态更新请求DTO"""
    status: ModelStatusEnum = Field(..., description="目标状态")


class AIModelUsageRecordRequest(BaseRequest):
    """AI模型使用记录请求DTO"""
    tokens_used: int = Field(default=0, ge=0, description="使用的令牌数")
    cost: float = Field(default=0.0, ge=0.0, description="产生的费用")
    operation_type: str = Field(default="completion", description="操作类型")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="附加数据")


class AIModelTestRequest(BaseRequest):
    """AI模型测试请求DTO"""
    test_prompt: str = Field(..., min_length=1, description="测试提示词")
    test_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="测试配置")


class AIModelBatchOperationRequest(BaseRequest):
    """AI模型批量操作请求DTO"""
    model_config = {"protected_namespaces": ()}  # 禁用保护命名空间警告

    model_ids: List[int] = Field(..., min_items=1, max_items=50, description="模型ID列表")
    operation: str = Field(..., description="操作类型")
    operation_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="操作数据")

    @validator('model_ids')
    def validate_model_ids(cls, v):
        return sorted(list(set(v)))  # 去重并排序

    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['activate', 'deactivate', 'deprecate', 'set_maintenance', 'delete']
        if v not in allowed_operations:
            raise ValueError(f'不支持的操作类型: {v}')
        return v


# 响应DTO
class AIModelResponse(BaseResponse):
    """AI模型响应DTO"""
    model_config = {"protected_namespaces": ()}  # 禁用保护命名空间警告

    id: int = Field(description="模型ID")
    name: str = Field(description="模型名称")
    display_name: str = Field(description="模型显示名称")
    provider: str = Field(description="模型提供商")
    model_type: str = Field(description="模型类型")
    status: str = Field(description="模型状态")
    version: Optional[str] = Field(description="模型版本")
    description: Optional[str] = Field(description="模型描述")
    api_endpoint: Optional[str] = Field(description="API端点")
    api_key: Optional[str] = Field(description="API密钥(隐藏)")
    max_tokens: int = Field(description="最大令牌数")
    temperature: float = Field(description="温度参数")
    pricing: Dict[str, Any] = Field(description="费用信息")
    config: Dict[str, Any] = Field(description="模型配置")
    usage_count: int = Field(description="使用次数")
    total_tokens: int = Field(description="总令牌消耗")
    total_cost: float = Field(description="总费用")
    average_tokens_per_use: float = Field(description="平均每次使用令牌数")
    average_cost_per_use: float = Field(description="平均每次使用费用")
    cost_per_token: float = Field(description="每令牌费用")
    created_by_id: int = Field(description="创建者ID")
    last_used_at: Optional[datetime] = Field(description="最后使用时间")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(description="更新时间")


class AIModelListResponse(BaseResponse):
    """AI模型列表响应DTO"""
    models: List[AIModelResponse] = Field(description="模型列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页")
    page_size: int = Field(description="页大小")
    total_pages: int = Field(description="总页数")


class AIModelStatisticsResponse(BaseResponse):
    """AI模型统计响应DTO"""
    total_models: int = Field(description="模型总数")
    active_models: int = Field(description="激活模型数")
    deprecated_models: int = Field(description="废弃模型数")
    maintenance_models: int = Field(description="维护中模型数")
    
    models_by_provider: Dict[str, int] = Field(description="按提供商统计")
    models_by_type: Dict[str, int] = Field(description="按类型统计")
    models_by_status: Dict[str, int] = Field(description="按状态统计")
    
    total_usage_count: int = Field(description="总使用次数")
    total_tokens_consumed: int = Field(description="总令牌消耗")
    total_cost: float = Field(description="总费用")
    
    avg_cost_per_model: float = Field(description="每模型平均费用")
    avg_tokens_per_model: float = Field(description="每模型平均令牌数")
    
    most_used_models: List[Dict[str, Any]] = Field(description="最常用模型")
    cost_breakdown: Dict[str, float] = Field(description="费用明细")


class AIModelTestResponse(BaseResponse):
    """AI模型测试响应DTO"""
    model_config = {"protected_namespaces": ()}  # 禁用保护命名空间警告

    test_id: str = Field(description="测试ID")
    model_id: int = Field(description="模型ID")
    test_prompt: str = Field(description="测试提示词")
    response_text: Optional[str] = Field(description="响应文本")
    tokens_used: int = Field(description="使用令牌数")
    response_time: float = Field(description="响应时间(秒)")
    cost: float = Field(description="费用")
    success: bool = Field(description="测试是否成功")
    error_message: Optional[str] = Field(description="错误信息")
    metadata: Dict[str, Any] = Field(description="测试元数据")
    tested_at: datetime = Field(description="测试时间")


class AIModelUsageResponse(BaseResponse):
    """AI模型使用情况响应DTO"""
    model_config = {"protected_namespaces": ()}  # 禁用保护命名空间警告

    model_id: int = Field(description="模型ID")
    usage_history: List[Dict[str, Any]] = Field(description="使用历史")
    daily_stats: Dict[str, Any] = Field(description="日统计")
    weekly_stats: Dict[str, Any] = Field(description="周统计")
    monthly_stats: Dict[str, Any] = Field(description="月统计")
    cost_trends: List[Dict[str, Any]] = Field(description="费用趋势")
    token_trends: List[Dict[str, Any]] = Field(description="令牌趋势")


class AIModelBatchOperationResponse(BaseResponse):
    """AI模型批量操作响应DTO"""
    total: int = Field(description="总操作数")
    success_count: int = Field(description="成功数")
    failed_count: int = Field(description="失败数")
    failed_ids: List[int] = Field(description="失败的模型ID列表")
    errors: List[str] = Field(description="错误信息列表")
    success_rate: float = Field(description="成功率")


# 导出所有DTO类
__all__ = [
    # 枚举
    "ModelProviderEnum",
    "ModelTypeEnum",
    "ModelStatusEnum",
    
    # 请求DTO
    "AIModelCreateRequest",
    "AIModelUpdateRequest",
    "AIModelSearchRequest",
    "AIModelStatusUpdateRequest",
    "AIModelUsageRecordRequest",
    "AIModelTestRequest",
    "AIModelBatchOperationRequest",
    
    # 响应DTO
    "AIModelResponse",
    "AIModelListResponse",
    "AIModelStatisticsResponse",
    "AIModelTestResponse",
    "AIModelUsageResponse",
    "AIModelBatchOperationResponse",
]