# Copyright (c) 2025 左岚. All rights reserved.
"""
AI模型配置实体
定义AI模型相关的配置信息
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship

from .base import BaseEntity


class ModelProvider(str, Enum):
    """模型提供商枚举"""
    OPENAI = "openai"  # OpenAI
    ANTHROPIC = "anthropic"  # Anthropic Claude
    DEEPSEEK = "deepseek"  # DeepSeek
    QIANWEN = "qianwen"  # 通义千问
    BAIDU = "baidu"  # 百度文心
    GOOGLE = "google"  # Google
    CUSTOM = "custom"  # 自定义


class ModelType(str, Enum):
    """模型类型枚举"""
    CHAT = "chat"  # 聊天模型
    COMPLETION = "completion"  # 补全模型
    EMBEDDING = "embedding"  # 嵌入模型
    IMAGE = "image"  # 图像模型
    AUDIO = "audio"  # 音频模型
    MULTIMODAL = "multimodal"  # 多模态模型


class ModelStatus(str, Enum):
    """模型状态枚举"""
    ACTIVE = "active"  # 激活
    INACTIVE = "inactive"  # 未激活
    DEPRECATED = "deprecated"  # 已废弃
    MAINTENANCE = "maintenance"  # 维护中


class AIModel(BaseEntity):
    """
    AI模型实体类
    定义AI模型的基本信息
    """
    __tablename__ = "ai_model"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 模型名称 - 必填，最大100个字符，唯一
    name = Column(String(100), nullable=False, unique=True, index=True, comment="模型名称")

    # 模型显示名称 - 可选，最大100个字符
    display_name = Column(String(100), nullable=True, comment="模型显示名称")

    # 模型提供商 - 必填，使用枚举值
    provider = Column(String(20), nullable=False, comment="模型提供商")

    # 模型类型 - 必填，使用枚举值
    model_type = Column(String(20), nullable=False, default=ModelType.CHAT.value, comment="模型类型")

    # 模型状态 - 必填，使用枚举值
    status = Column(String(20), nullable=False, default=ModelStatus.ACTIVE.value, comment="模型状态")

    # 模型版本 - 可选
    version = Column(String(20), nullable=True, comment="模型版本")

    # 模型描述 - 可选，文本类型
    description = Column(Text, nullable=True, comment="模型描述")

    # API端点 - 可选
    api_endpoint = Column(String(500), nullable=True, comment="API端点")

    # API密钥 - 可选，加密存储
    api_key = Column(String(500), nullable=True, comment="API密钥")

    # 最大令牌数
    max_tokens = Column(Integer, default=4096, comment="最大令牌数")

    # 温度参数
    temperature = Column(Float, default=0.7, comment="温度参数")

    # 费用信息 - JSON格式存储
    pricing = Column(JSON, nullable=True, comment="费用信息")

    # 模型配置 - JSON格式存储
    config = Column(JSON, nullable=True, comment="模型配置")

    # 使用次数
    usage_count = Column(Integer, default=0, comment="使用次数")

    # 总令牌消耗
    total_tokens = Column(Integer, default=0, comment="总令牌消耗")

    # 总费用
    total_cost = Column(Float, default=0.0, comment="总费用")

    # 创建者ID - 外键关联用户表
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment="创建者ID")

    # 最后使用时间
    last_used_at = Column(DateTime, nullable=True, comment="最后使用时间")

    # 关联关系
    # 模型-创建者关联
    creator = relationship("User", foreign_keys=[created_by_id])

    def __init__(self, name: str, provider: str, model_type: str = ModelType.CHAT.value,
                 display_name: str = None, version: str = None, description: str = None,
                 api_endpoint: str = None, api_key: str = None, max_tokens: int = 4096,
                 temperature: float = 0.7, pricing: Dict[str, Any] = None,
                 config: Dict[str, Any] = None, created_by_id: int = None):
        """
        初始化AI模型

        Args:
            name: 模型名称
            provider: 模型提供商
            model_type: 模型类型
            display_name: 模型显示名称
            version: 模型版本
            description: 模型描述
            api_endpoint: API端点
            api_key: API密钥
            max_tokens: 最大令牌数
            temperature: 温度参数
            pricing: 费用信息
            config: 模型配置
            created_by_id: 创建者ID
        """
        self.name = name
        self.provider = provider
        self.model_type = model_type
        self.display_name = display_name or name
        self.status = ModelStatus.ACTIVE.value
        self.version = version
        self.description = description
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.pricing = pricing or {}
        self.config = config or {}
        self.usage_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.created_by_id = created_by_id

    def is_active(self) -> bool:
        """判断模型是否激活"""
        return self.status == ModelStatus.ACTIVE.value

    def is_deprecated(self) -> bool:
        """判断模型是否已废弃"""
        return self.status == ModelStatus.DEPRECATED.value

    def is_chat_model(self) -> bool:
        """判断是否为聊天模型"""
        return self.model_type == ModelType.CHAT.value

    def is_completion_model(self) -> bool:
        """判断是否为补全模型"""
        return self.model_type == ModelType.COMPLETION.value

    def is_embedding_model(self) -> bool:
        """判断是否为嵌入模型"""
        return self.model_type == ModelType.EMBEDDING.value

    def activate(self):
        """激活模型"""
        self.status = ModelStatus.ACTIVE.value
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """停用模型"""
        self.status = ModelStatus.INACTIVE.value
        self.updated_at = datetime.utcnow()

    def deprecate(self):
        """废弃模型"""
        self.status = ModelStatus.DEPRECATED.value
        self.updated_at = datetime.utcnow()

    def set_maintenance(self):
        """设置为维护状态"""
        self.status = ModelStatus.MAINTENANCE.value
        self.updated_at = datetime.utcnow()

    def update_api_config(self, api_endpoint: str = None, api_key: str = None):
        """
        更新API配置
        
        Args:
            api_endpoint: API端点
            api_key: API密钥
        """
        if api_endpoint is not None:
            self.api_endpoint = api_endpoint
        if api_key is not None:
            self.api_key = api_key
        self.updated_at = datetime.utcnow()

    def update_parameters(self, max_tokens: int = None, temperature: float = None):
        """
        更新模型参数
        
        Args:
            max_tokens: 最大令牌数
            temperature: 温度参数
        """
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if temperature is not None:
            self.temperature = temperature
        self.updated_at = datetime.utcnow()

    def update_config(self, config: Dict[str, Any]):
        """
        更新模型配置
        
        Args:
            config: 新的配置信息
        """
        if self.config is None:
            self.config = {}
        self.config.update(config)
        self.updated_at = datetime.utcnow()

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        if self.config is None:
            return default
        return self.config.get(key, default)

    def record_usage(self, tokens_used: int = 0, cost: float = 0.0):
        """
        记录使用情况
        
        Args:
            tokens_used: 使用的令牌数
            cost: 产生的费用
        """
        self.usage_count += 1
        self.total_tokens += tokens_used
        self.total_cost += cost
        self.last_used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def get_average_tokens_per_use(self) -> float:
        """获取平均每次使用令牌数"""
        if self.usage_count == 0:
            return 0.0
        return self.total_tokens / self.usage_count

    def get_average_cost_per_use(self) -> float:
        """获取平均每次使用费用"""
        if self.usage_count == 0:
            return 0.0
        return self.total_cost / self.usage_count

    def get_cost_per_token(self) -> float:
        """获取每令牌费用"""
        if self.total_tokens == 0:
            return 0.0
        return self.total_cost / self.total_tokens

    def update_pricing(self, pricing: Dict[str, Any]):
        """
        更新费用信息
        
        Args:
            pricing: 费用信息
        """
        if self.pricing is None:
            self.pricing = {}
        self.pricing.update(pricing)
        self.updated_at = datetime.utcnow()

    def get_pricing_info(self, key: str, default: Any = None) -> Any:
        """
        获取费用信息
        
        Args:
            key: 费用信息键
            default: 默认值
            
        Returns:
            费用信息值
        """
        if self.pricing is None:
            return default
        return self.pricing.get(key, default)

    def update_info(self, display_name: str = None, description: str = None,
                   version: str = None, max_tokens: int = None, temperature: float = None):
        """
        更新模型基本信息

        Args:
            display_name: 模型显示名称
            description: 模型描述
            version: 模型版本
            max_tokens: 最大令牌数
            temperature: 温度参数
        """
        if display_name is not None:
            self.display_name = display_name
        if description is not None:
            self.description = description
        if version is not None:
            self.version = version
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if temperature is not None:
            self.temperature = temperature
        self.updated_at = datetime.utcnow()

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        转换为字典格式

        Args:
            include_sensitive: 是否包含敏感信息（如API密钥）

        Returns:
            模型信息字典
        """
        result = {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "provider": self.provider,
            "model_type": self.model_type,
            "status": self.status,
            "version": self.version,
            "description": self.description,
            "api_endpoint": self.api_endpoint,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "pricing": self.pricing,
            "config": self.config,
            "usage_count": self.usage_count,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "average_tokens_per_use": self.get_average_tokens_per_use(),
            "average_cost_per_use": self.get_average_cost_per_use(),
            "cost_per_token": self.get_cost_per_token(),
            "created_by_id": self.created_by_id,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            result["api_key"] = self.api_key
        else:
            result["api_key"] = "***" if self.api_key else None
        
        return result

    def __repr__(self):
        """
        字符串表示
        """
        return f"<AIModel(id={self.id}, name='{self.name}', provider='{self.provider}', status='{self.status}')>"