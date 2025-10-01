"""
AI代理配置实体
定义AI代理的配置参数信息
"""

from datetime import datetime
from typing import Optional, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseEntity


class ConfigType(str, Enum):
    """配置类型枚举"""
    STRING = "string"  # 字符串类型
    INTEGER = "integer"  # 整数类型
    FLOAT = "float"  # 浮点数类型
    BOOLEAN = "boolean"  # 布尔类型
    JSON = "json"  # JSON对象类型
    SECRET = "secret"  # 密钥类型（需要加密存储）


class AgentConfig(BaseEntity):
    """
    AI代理配置实体类
    定义AI代理的配置参数信息
    """
    __tablename__ = "agent_config"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 代理ID - 外键关联代理表
    agent_id = Column(Integer, ForeignKey('agent.id'), nullable=False, comment="代理ID")

    # 配置键 - 必填，最大100个字符
    config_key = Column(String(100), nullable=False, comment="配置键")

    # 配置值 - 可选，文本类型
    config_value = Column(Text, nullable=True, comment="配置值")

    # 配置类型 - 必填，使用枚举值
    config_type = Column(String(20), nullable=False, default=ConfigType.STRING.value, comment="配置类型")

    # 配置描述 - 可选，最大500个字符
    description = Column(String(500), nullable=True, comment="配置描述")

    # 是否必填 - 默认False
    is_required = Column(Integer, default=0, comment="是否必填(0:否,1:是)")

    # 是否启用 - 默认True
    is_enabled = Column(Integer, default=1, comment="是否启用(0:禁用,1:启用)")

    # 默认值 - 可选
    default_value = Column(Text, nullable=True, comment="默认值")

    # 验证规则 - 可选，JSON格式
    validation_rules = Column(Text, nullable=True, comment="验证规则")

    # 显示顺序
    display_order = Column(Integer, default=0, comment="显示顺序")

    # 关联关系
    # 配置-代理关联（多个配置属于一个代理）
    agent = relationship("Agent", back_populates="agent_configs")

    def __init__(self, agent_id: int, config_key: str, config_value: str = None,
                 config_type: str = ConfigType.STRING.value, description: str = None,
                 is_required: bool = False, is_enabled: bool = True, 
                 default_value: str = None, validation_rules: str = None,
                 display_order: int = 0):
        """
        初始化代理配置

        Args:
            agent_id: 代理ID
            config_key: 配置键
            config_value: 配置值
            config_type: 配置类型
            description: 配置描述
            is_required: 是否必填
            is_enabled: 是否启用
            default_value: 默认值
            validation_rules: 验证规则
            display_order: 显示顺序
        """
        self.agent_id = agent_id
        self.config_key = config_key
        self.config_value = config_value
        self.config_type = config_type
        self.description = description
        self.is_required = 1 if is_required else 0
        self.is_enabled = 1 if is_enabled else 0
        self.default_value = default_value
        self.validation_rules = validation_rules
        self.display_order = display_order

    def is_required_config(self) -> bool:
        """
        判断是否为必填配置

        Returns:
            True表示必填，False表示可选
        """
        return self.is_required == 1

    def is_enabled_config(self) -> bool:
        """
        判断配置是否启用

        Returns:
            True表示启用，False表示禁用
        """
        return self.is_enabled == 1

    def is_secret_config(self) -> bool:
        """
        判断是否为密钥配置

        Returns:
            True表示密钥配置，False表示普通配置
        """
        return self.config_type == ConfigType.SECRET.value

    def enable(self):
        """
        启用配置
        """
        self.is_enabled = 1
        self.updated_at = datetime.utcnow()

    def disable(self):
        """
        禁用配置
        """
        self.is_enabled = 0
        self.updated_at = datetime.utcnow()

    def set_required(self, required: bool = True):
        """
        设置是否必填

        Args:
            required: 是否必填
        """
        self.is_required = 1 if required else 0
        self.updated_at = datetime.utcnow()

    def update_value(self, value: str):
        """
        更新配置值

        Args:
            value: 新的配置值
        """
        self.config_value = value
        self.updated_at = datetime.utcnow()

    def get_typed_value(self) -> Any:
        """
        根据配置类型返回对应类型的值

        Returns:
            转换后的配置值
        """
        if self.config_value is None:
            return self.get_typed_default_value()

        try:
            if self.config_type == ConfigType.INTEGER.value:
                return int(self.config_value)
            elif self.config_type == ConfigType.FLOAT.value:
                return float(self.config_value)
            elif self.config_type == ConfigType.BOOLEAN.value:
                return self.config_value.lower() in ('true', '1', 'yes', 'on')
            elif self.config_type == ConfigType.JSON.value:
                import json
                return json.loads(self.config_value)
            else:  # STRING or SECRET
                return self.config_value
        except (ValueError, TypeError, Exception):
            return self.get_typed_default_value()

    def get_typed_default_value(self) -> Any:
        """
        根据配置类型返回默认值

        Returns:
            转换后的默认值
        """
        if self.default_value is None:
            if self.config_type == ConfigType.INTEGER.value:
                return 0
            elif self.config_type == ConfigType.FLOAT.value:
                return 0.0
            elif self.config_type == ConfigType.BOOLEAN.value:
                return False
            elif self.config_type == ConfigType.JSON.value:
                return {}
            else:  # STRING or SECRET
                return ""

        try:
            if self.config_type == ConfigType.INTEGER.value:
                return int(self.default_value)
            elif self.config_type == ConfigType.FLOAT.value:
                return float(self.default_value)
            elif self.config_type == ConfigType.BOOLEAN.value:
                return self.default_value.lower() in ('true', '1', 'yes', 'on')
            elif self.config_type == ConfigType.JSON.value:
                import json
                return json.loads(self.default_value)
            else:  # STRING or SECRET
                return self.default_value
        except (ValueError, TypeError, Exception):
            return self.default_value

    def update_info(self, config_value: str = None, description: str = None,
                   is_required: bool = None, is_enabled: bool = None,
                   default_value: str = None, validation_rules: str = None,
                   display_order: int = None):
        """
        更新配置信息

        Args:
            config_value: 配置值
            description: 配置描述
            is_required: 是否必填
            is_enabled: 是否启用
            default_value: 默认值
            validation_rules: 验证规则
            display_order: 显示顺序
        """
        if config_value is not None:
            self.config_value = config_value
        if description is not None:
            self.description = description
        if is_required is not None:
            self.is_required = 1 if is_required else 0
        if is_enabled is not None:
            self.is_enabled = 1 if is_enabled else 0
        if default_value is not None:
            self.default_value = default_value
        if validation_rules is not None:
            self.validation_rules = validation_rules
        if display_order is not None:
            self.display_order = display_order
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            配置信息字典
        """
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "config_key": self.config_key,
            "config_value": self.config_value if not self.is_secret_config() else "***",  # 密钥类型隐藏值
            "config_type": self.config_type,
            "description": self.description,
            "is_required": self.is_required,
            "is_enabled": self.is_enabled,
            "default_value": self.default_value,
            "validation_rules": self.validation_rules,
            "display_order": self.display_order,
            "typed_value": self.get_typed_value() if not self.is_secret_config() else "***",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<AgentConfig(id={self.id}, agent_id={self.agent_id}, key='{self.config_key}', type='{self.config_type}')>"
