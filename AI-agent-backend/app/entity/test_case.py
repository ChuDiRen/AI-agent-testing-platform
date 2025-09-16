# Copyright (c) 2025 左岚. All rights reserved.
"""
测试用例实体
定义AI智能测试用例生成相关的实体模型
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship

from .base import BaseEntity


class TestCaseStatus(str, Enum):
    """测试用例状态枚举"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 执行中
    PASSED = "passed"  # 通过
    FAILED = "failed"  # 失败
    SKIPPED = "skipped"  # 跳过
    BLOCKED = "blocked"  # 阻塞


class TestCasePriority(str, Enum):
    """测试用例优先级枚举"""
    P1 = "P1"  # 高
    P2 = "P2"  # 中高
    P3 = "P3"  # 中
    P4 = "P4"  # 中低
    P5 = "P5"  # 低


class TestCaseType(str, Enum):
    """测试用例类型枚举"""
    FUNCTIONAL = "functional"  # 功能测试
    PERFORMANCE = "performance"  # 性能测试
    SECURITY = "security"  # 安全测试
    UI = "ui"  # UI测试
    API = "api"  # 接口测试
    INTEGRATION = "integration"  # 集成测试
    UNIT = "unit"  # 单元测试


class TestCase(BaseEntity):
    """
    测试用例实体类
    定义智能生成的测试用例信息
    """
    __tablename__ = "test_case"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 用例名称 - 必填，最大200个字符
    name = Column(String(200), nullable=False, comment="用例名称")

    # 所属模块 - 可选，最大100个字符
    module = Column(String(100), nullable=True, comment="所属模块")

    # 用例描述 - 可选，文本类型
    description = Column(Text, nullable=True, comment="用例描述")

    # 前置条件 - 可选，文本类型
    preconditions = Column(Text, nullable=True, comment="前置条件")

    # 测试步骤 - 可选，文本类型
    test_steps = Column(Text, nullable=True, comment="测试步骤")

    # 预期结果 - 可选，文本类型
    expected_result = Column(Text, nullable=True, comment="预期结果")

    # 实际结果 - 可选，文本类型
    actual_result = Column(Text, nullable=True, comment="实际结果")

    # 用例状态 - 必填，使用枚举值
    status = Column(String(20), nullable=False, default=TestCaseStatus.DRAFT.value, comment="用例状态")

    # 用例优先级 - 必填，使用枚举值
    priority = Column(String(10), nullable=False, default=TestCasePriority.P3.value, comment="用例优先级")

    # 用例类型 - 必填，使用枚举值
    test_type = Column(String(20), nullable=False, default=TestCaseType.FUNCTIONAL.value, comment="用例类型")

    # 标签 - 可选，最大200个字符，用逗号分隔
    tags = Column(String(200), nullable=True, comment="标签")

    # 关联的代理ID - 外键关联代理表
    agent_id = Column(Integer, ForeignKey('agent.id'), nullable=True, comment="关联的代理ID")

    # 创建者ID - 外键关联用户表
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment="创建者ID")

    # 执行者ID - 外键关联用户表
    executor_id = Column(Integer, ForeignKey('user.id'), nullable=True, comment="执行者ID")

    # 执行时间
    executed_at = Column(DateTime, nullable=True, comment="执行时间")

    # 执行耗时（秒）
    execution_time = Column(Float, nullable=True, comment="执行耗时")

    # 备注
    remarks = Column(Text, nullable=True, comment="备注")

    # 附加数据 - JSON格式存储
    metadata = Column(JSON, nullable=True, comment="附加数据")

    # 关联关系
    # 测试用例-代理关联
    agent = relationship("Agent", back_populates="test_cases")

    # 测试用例-创建者关联
    creator = relationship("User", foreign_keys=[created_by_id])

    # 测试用例-执行者关联
    executor = relationship("User", foreign_keys=[executor_id])

    # 测试用例-测试报告关联
    test_reports = relationship("TestReport", back_populates="test_case")

    def __init__(self, name: str, module: str = None, description: str = None,
                 preconditions: str = None, test_steps: str = None, 
                 expected_result: str = None, priority: str = TestCasePriority.P3.value,
                 test_type: str = TestCaseType.FUNCTIONAL.value, tags: str = None,
                 agent_id: int = None, created_by_id: int = None, metadata: Dict[str, Any] = None):
        """
        初始化测试用例

        Args:
            name: 用例名称
            module: 所属模块
            description: 用例描述
            preconditions: 前置条件
            test_steps: 测试步骤
            expected_result: 预期结果
            priority: 用例优先级
            test_type: 用例类型
            tags: 标签
            agent_id: 关联的代理ID
            created_by_id: 创建者ID
            metadata: 附加数据
        """
        self.name = name
        self.module = module
        self.description = description
        self.preconditions = preconditions
        self.test_steps = test_steps
        self.expected_result = expected_result
        self.status = TestCaseStatus.DRAFT.value
        self.priority = priority
        self.test_type = test_type
        self.tags = tags
        self.agent_id = agent_id
        self.created_by_id = created_by_id
        self.metadata = metadata or {}

    def is_draft(self) -> bool:
        """判断是否为草稿状态"""
        return self.status == TestCaseStatus.DRAFT.value

    def is_pending(self) -> bool:
        """判断是否为待执行状态"""
        return self.status == TestCaseStatus.PENDING.value

    def is_running(self) -> bool:
        """判断是否为执行中状态"""
        return self.status == TestCaseStatus.RUNNING.value

    def is_passed(self) -> bool:
        """判断是否为通过状态"""
        return self.status == TestCaseStatus.PASSED.value

    def is_failed(self) -> bool:
        """判断是否为失败状态"""
        return self.status == TestCaseStatus.FAILED.value

    def is_high_priority(self) -> bool:
        """判断是否为高优先级"""
        return self.priority in [TestCasePriority.P1.value, TestCasePriority.P2.value]

    def set_pending(self):
        """设置为待执行状态"""
        self.status = TestCaseStatus.PENDING.value
        self.updated_at = datetime.utcnow()

    def set_running(self, executor_id: int = None):
        """
        设置为执行中状态
        
        Args:
            executor_id: 执行者ID
        """
        self.status = TestCaseStatus.RUNNING.value
        if executor_id:
            self.executor_id = executor_id
        self.executed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def set_passed(self, actual_result: str = None, execution_time: float = None):
        """
        设置为通过状态
        
        Args:
            actual_result: 实际结果
            execution_time: 执行耗时
        """
        self.status = TestCaseStatus.PASSED.value
        if actual_result:
            self.actual_result = actual_result
        if execution_time is not None:
            self.execution_time = execution_time
        self.updated_at = datetime.utcnow()

    def set_failed(self, actual_result: str = None, execution_time: float = None):
        """
        设置为失败状态
        
        Args:
            actual_result: 实际结果
            execution_time: 执行耗时
        """
        self.status = TestCaseStatus.FAILED.value
        if actual_result:
            self.actual_result = actual_result
        if execution_time is not None:
            self.execution_time = execution_time
        self.updated_at = datetime.utcnow()

    def set_skipped(self, reason: str = None):
        """
        设置为跳过状态
        
        Args:
            reason: 跳过原因
        """
        self.status = TestCaseStatus.SKIPPED.value
        if reason:
            self.remarks = reason
        self.updated_at = datetime.utcnow()

    def set_blocked(self, reason: str = None):
        """
        设置为阻塞状态
        
        Args:
            reason: 阻塞原因
        """
        self.status = TestCaseStatus.BLOCKED.value
        if reason:
            self.remarks = reason
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str):
        """
        添加标签
        
        Args:
            tag: 标签名称
        """
        if not self.tags:
            self.tags = tag
        else:
            tags_list = self.tags.split(',')
            if tag not in tags_list:
                tags_list.append(tag)
                self.tags = ','.join(tags_list)
        self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str):
        """
        移除标签
        
        Args:
            tag: 标签名称
        """
        if self.tags:
            tags_list = self.tags.split(',')
            if tag in tags_list:
                tags_list.remove(tag)
                self.tags = ','.join(tags_list) if tags_list else None
        self.updated_at = datetime.utcnow()

    def get_tags_list(self) -> List[str]:
        """
        获取标签列表
        
        Returns:
            标签列表
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def update_info(self, name: str = None, module: str = None, description: str = None,
                   preconditions: str = None, test_steps: str = None, 
                   expected_result: str = None, priority: str = None,
                   test_type: str = None, tags: str = None):
        """
        更新测试用例基本信息

        Args:
            name: 用例名称
            module: 所属模块
            description: 用例描述
            preconditions: 前置条件
            test_steps: 测试步骤
            expected_result: 预期结果
            priority: 用例优先级
            test_type: 用例类型
            tags: 标签
        """
        if name is not None:
            self.name = name
        if module is not None:
            self.module = module
        if description is not None:
            self.description = description
        if preconditions is not None:
            self.preconditions = preconditions
        if test_steps is not None:
            self.test_steps = test_steps
        if expected_result is not None:
            self.expected_result = expected_result
        if priority is not None:
            self.priority = priority
        if test_type is not None:
            self.test_type = test_type
        if tags is not None:
            self.tags = tags
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            测试用例信息字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "module": self.module,
            "description": self.description,
            "preconditions": self.preconditions,
            "test_steps": self.test_steps,
            "expected_result": self.expected_result,
            "actual_result": self.actual_result,
            "status": self.status,
            "priority": self.priority,
            "test_type": self.test_type,
            "tags": self.tags,
            "tags_list": self.get_tags_list(),
            "agent_id": self.agent_id,
            "created_by_id": self.created_by_id,
            "executor_id": self.executor_id,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "execution_time": self.execution_time,
            "remarks": self.remarks,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<TestCase(id={self.id}, name='{self.name}', status='{self.status}', priority='{self.priority}')>"