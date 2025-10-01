"""
测试用例生成历史实体
定义AI智能测试用例生成历史记录的实体模型
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import BaseEntity


class GenerationStatus(str, Enum):
    """生成状态枚举"""
    PENDING = "pending"  # 等待中
    RUNNING = "running"  # 生成中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class TestCaseGenerationHistory(BaseEntity):
    """
    测试用例生成历史实体类
    记录AI智能生成测试用例的历史记录
    """
    __tablename__ = "test_case_generation_history"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 生成任务ID - 必填，最大100个字符，唯一标识
    task_id = Column(String(100), nullable=False, unique=True, comment="生成任务ID")

    # 需求描述 - 必填，文本类型
    requirement_text = Column(Text, nullable=False, comment="需求描述")

    # 测试类型 - 必填，最大20个字符
    test_type = Column(String(20), nullable=False, comment="测试类型")

    # 优先级 - 必填，最大10个字符
    priority = Column(String(10), nullable=False, comment="优先级")

    # 生成数量 - 必填，整数类型
    generated_count = Column(Integer, nullable=False, default=0, comment="生成数量")

    # 生成状态 - 必填，使用枚举值
    status = Column(String(20), nullable=False, default=GenerationStatus.PENDING.value, comment="生成状态")

    # 创建者ID - 外键关联用户表
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment="创建者ID")

    # 关联的代理ID - 外键关联代理表
    agent_id = Column(Integer, ForeignKey('agent.id'), nullable=True, comment="关联的代理ID")

    # 生成配置 - JSON格式存储
    generation_config = Column(JSON, nullable=True, comment="生成配置")

    # 生成结果 - JSON格式存储
    generation_result = Column(JSON, nullable=True, comment="生成结果")

    # 错误信息 - 可选，文本类型
    error_message = Column(Text, nullable=True, comment="错误信息")

    # 开始时间
    started_at = Column(DateTime, nullable=True, comment="开始时间")

    # 完成时间
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    # 关联关系
    # 生成历史-创建者关联
    creator = relationship("User", foreign_keys=[created_by_id])

    # 生成历史-代理关联
    agent = relationship("Agent", foreign_keys=[agent_id])

    def __init__(self, task_id: str, requirement_text: str, test_type: str,
                 priority: str, created_by_id: int, agent_id: int = None,
                 generation_config: Dict[str, Any] = None):
        """
        初始化测试用例生成历史

        Args:
            task_id: 生成任务ID
            requirement_text: 需求描述
            test_type: 测试类型
            priority: 优先级
            created_by_id: 创建者ID
            agent_id: 关联的代理ID
            generation_config: 生成配置
        """
        self.task_id = task_id
        self.requirement_text = requirement_text
        self.test_type = test_type
        self.priority = priority
        self.created_by_id = created_by_id
        self.agent_id = agent_id
        self.generation_config = generation_config or {}
        self.status = GenerationStatus.PENDING.value
        self.generated_count = 0

    def is_pending(self) -> bool:
        """判断是否为等待中状态"""
        return self.status == GenerationStatus.PENDING.value

    def is_running(self) -> bool:
        """判断是否为生成中状态"""
        return self.status == GenerationStatus.RUNNING.value

    def is_completed(self) -> bool:
        """判断是否为已完成状态"""
        return self.status == GenerationStatus.COMPLETED.value

    def is_failed(self) -> bool:
        """判断是否为失败状态"""
        return self.status == GenerationStatus.FAILED.value

    def start_generation(self):
        """开始生成"""
        self.status = GenerationStatus.RUNNING.value
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def complete_generation(self, generated_count: int, result: Dict[str, Any] = None):
        """
        完成生成
        
        Args:
            generated_count: 生成数量
            result: 生成结果
        """
        self.status = GenerationStatus.COMPLETED.value
        self.generated_count = generated_count
        self.generation_result = result or {}
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def fail_generation(self, error_message: str):
        """
        生成失败
        
        Args:
            error_message: 错误信息
        """
        self.status = GenerationStatus.FAILED.value
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def get_requirement_summary(self, max_length: int = 50) -> str:
        """
        获取需求摘要
        
        Args:
            max_length: 最大长度
            
        Returns:
            需求摘要
        """
        if not self.requirement_text:
            return ""
        
        if len(self.requirement_text) <= max_length:
            return self.requirement_text
        
        return self.requirement_text[:max_length] + "..."

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            生成历史信息字典
        """
        return {
            "id": self.id,
            "task_id": self.task_id,
            "requirement_text": self.requirement_text,
            "requirement_summary": self.get_requirement_summary(),
            "test_type": self.test_type,
            "priority": self.priority,
            "generated_count": self.generated_count,
            "status": self.status,
            "created_by_id": self.created_by_id,
            "agent_id": self.agent_id,
            "generation_config": self.generation_config,
            "generation_result": self.generation_result,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<TestCaseGenerationHistory(id={self.id}, task_id='{self.task_id}', status='{self.status}')>"
