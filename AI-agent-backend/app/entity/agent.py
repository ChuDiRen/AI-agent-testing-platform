"""
AI代理实体
定义AI代理的基本信息和行为
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import BaseEntity


class AgentType(str, Enum):
    """代理类型枚举"""
    CHAT = "chat"  # 聊天代理
    TASK = "task"  # 任务代理
    ANALYSIS = "analysis"  # 分析代理
    TESTING = "testing"  # 测试代理
    CUSTOM = "custom"  # 自定义代理


class AgentStatus(str, Enum):
    """代理状态枚举"""
    INACTIVE = "inactive"  # 未激活
    ACTIVE = "active"  # 激活
    RUNNING = "running"  # 运行中
    STOPPED = "stopped"  # 已停止
    ERROR = "error"  # 错误状态
    MAINTENANCE = "maintenance"  # 维护中


class Agent(BaseEntity):
    """
    AI代理实体类
    定义AI代理的基本信息和行为
    """
    __tablename__ = "agent"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 代理名称 - 必填，最大100个字符，唯一
    name = Column(String(100), nullable=False, unique=True, index=True, comment="代理名称")

    # 代理类型 - 必填，使用枚举值
    type = Column(String(20), nullable=False, default=AgentType.CHAT.value, comment="代理类型")

    # 代理描述 - 可选，最大500个字符
    description = Column(String(500), nullable=True, comment="代理描述")

    # 代理状态 - 必填，使用枚举值
    status = Column(String(20), nullable=False, default=AgentStatus.INACTIVE.value, comment="代理状态")

    # 代理配置 - JSON格式存储
    config = Column(JSON, nullable=True, comment="代理配置信息")

    # 代理版本 - 可选
    version = Column(String(20), nullable=True, default="1.0.0", comment="代理版本")

    # 创建者ID - 外键关联用户表
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment="创建者ID")

    # 最后运行时间
    last_run_time = Column(DateTime, nullable=True, comment="最后运行时间")

    # 运行统计信息
    run_count = Column(Integer, default=0, comment="运行次数")
    
    # 成功运行次数
    success_count = Column(Integer, default=0, comment="成功运行次数")
    
    # 失败运行次数
    error_count = Column(Integer, default=0, comment="失败运行次数")

    # 关联关系
    # 代理-用户关联（一个用户可以创建多个代理）
    creator = relationship("User", back_populates="created_agents", foreign_keys=[created_by_id])

    # 代理-配置关联（一个代理可以有多个配置项）
    agent_configs = relationship("AgentConfig", back_populates="agent", cascade="all, delete-orphan")

    # 代理-测试用例关联（一个代理可以有多个测试用例）
    test_cases = relationship("TestCase", back_populates="agent")

    # 代理-测试报告关联（一个代理可以有多个测试报告）
    test_reports = relationship("TestReport", back_populates="agent")

    def __init__(self, name: str, type: str = AgentType.CHAT.value, description: str = None,
                 created_by_id: int = None, config: Dict[str, Any] = None, version: str = "1.0.0"):
        """
        初始化AI代理

        Args:
            name: 代理名称
            type: 代理类型
            description: 代理描述
            created_by_id: 创建者ID
            config: 代理配置
            version: 代理版本
        """
        self.name = name
        self.type = type
        self.description = description
        self.status = AgentStatus.INACTIVE.value
        self.created_by_id = created_by_id
        self.config = config or {}
        self.version = version
        self.run_count = 0
        self.success_count = 0
        self.error_count = 0

    def is_active(self) -> bool:
        """
        判断代理是否处于激活状态

        Returns:
            True表示激活，False表示未激活
        """
        return self.status == AgentStatus.ACTIVE.value

    def is_running(self) -> bool:
        """
        判断代理是否正在运行

        Returns:
            True表示运行中，False表示未运行
        """
        return self.status == AgentStatus.RUNNING.value

    def is_stopped(self) -> bool:
        """
        判断代理是否已停止

        Returns:
            True表示已停止，False表示未停止
        """
        return self.status == AgentStatus.STOPPED.value

    def is_error(self) -> bool:
        """
        判断代理是否处于错误状态

        Returns:
            True表示错误状态，False表示正常
        """
        return self.status == AgentStatus.ERROR.value

    def activate(self):
        """
        激活代理
        """
        if self.status == AgentStatus.INACTIVE.value:
            self.status = AgentStatus.ACTIVE.value
            self.updated_at = datetime.utcnow()

    def deactivate(self):
        """
        停用代理
        """
        if self.status != AgentStatus.INACTIVE.value:
            self.status = AgentStatus.INACTIVE.value
            self.updated_at = datetime.utcnow()

    def start(self):
        """
        启动代理
        """
        if self.status == AgentStatus.ACTIVE.value:
            self.status = AgentStatus.RUNNING.value
            self.last_run_time = datetime.utcnow()
            self.updated_at = datetime.utcnow()

    def stop(self):
        """
        停止代理
        """
        if self.status == AgentStatus.RUNNING.value:
            self.status = AgentStatus.STOPPED.value
            self.updated_at = datetime.utcnow()

    def set_error(self, error_message: str = None):
        """
        设置代理为错误状态

        Args:
            error_message: 错误消息
        """
        self.status = AgentStatus.ERROR.value
        if error_message and self.config:
            self.config["last_error"] = error_message
        self.error_count += 1
        self.updated_at = datetime.utcnow()

    def record_success_run(self):
        """
        记录成功运行
        """
        self.run_count += 1
        self.success_count += 1
        self.last_run_time = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def record_error_run(self, error_message: str = None):
        """
        记录失败运行

        Args:
            error_message: 错误消息
        """
        self.run_count += 1
        self.error_count += 1
        self.set_error(error_message)

    def update_config(self, config: Dict[str, Any]):
        """
        更新代理配置

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

    def get_success_rate(self) -> float:
        """
        获取成功率

        Returns:
            成功率（0.0-1.0）
        """
        if self.run_count == 0:
            return 0.0
        return self.success_count / self.run_count

    def get_error_rate(self) -> float:
        """
        获取错误率

        Returns:
            错误率（0.0-1.0）
        """
        if self.run_count == 0:
            return 0.0
        return self.error_count / self.run_count

    def update_info(self, name: str = None, description: str = None, 
                   type: str = None, version: str = None):
        """
        更新代理基本信息

        Args:
            name: 代理名称
            description: 代理描述
            type: 代理类型
            version: 代理版本
        """
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if type is not None:
            self.type = type
        if version is not None:
            self.version = version
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            代理信息字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "status": self.status,
            "config": self.config,
            "version": self.version,
            "created_by_id": self.created_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "run_count": self.run_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.get_success_rate(),
            "error_rate": self.get_error_rate()
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.type}', status='{self.status}')>"
