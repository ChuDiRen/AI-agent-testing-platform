# Copyright (c) 2025 左岚. All rights reserved.
"""
测试报告实体
定义测试报告相关的实体模型
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship

from .base import BaseEntity


class ReportStatus(str, Enum):
    """报告状态枚举"""
    GENERATING = "generating"  # 生成中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 生成失败
    ARCHIVED = "archived"  # 已归档


class ReportType(str, Enum):
    """报告类型枚举"""
    EXECUTION = "execution"  # 执行报告
    SUMMARY = "summary"  # 汇总报告
    DETAILED = "detailed"  # 详细报告
    CUSTOM = "custom"  # 自定义报告


class TestReport(BaseEntity):
    """
    测试报告实体类
    定义测试执行报告信息
    """
    __tablename__ = "test_report"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 报告名称 - 必填，最大200个字符
    name = Column(String(200), nullable=False, comment="报告名称")

    # 报告描述 - 可选，文本类型
    description = Column(Text, nullable=True, comment="报告描述")

    # 报告类型 - 必填，使用枚举值
    report_type = Column(String(20), nullable=False, default=ReportType.EXECUTION.value, comment="报告类型")

    # 报告状态 - 必填，使用枚举值
    status = Column(String(20), nullable=False, default=ReportStatus.GENERATING.value, comment="报告状态")

    # 关联的测试用例ID - 外键关联测试用例表
    test_case_id = Column(Integer, ForeignKey('test_case.id'), nullable=True, comment="关联的测试用例ID")

    # 关联的代理ID - 外键关联代理表
    agent_id = Column(Integer, ForeignKey('agent.id'), nullable=True, comment="关联的代理ID")

    # 创建者ID - 外键关联用户表
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment="创建者ID")

    # 执行开始时间
    start_time = Column(DateTime, nullable=True, comment="执行开始时间")

    # 执行结束时间
    end_time = Column(DateTime, nullable=True, comment="执行结束时间")

    # 执行耗时（秒）
    duration = Column(Float, nullable=True, comment="执行耗时")

    # 总测试用例数
    total_cases = Column(Integer, default=0, comment="总测试用例数")

    # 通过用例数
    passed_cases = Column(Integer, default=0, comment="通过用例数")

    # 失败用例数
    failed_cases = Column(Integer, default=0, comment="失败用例数")

    # 跳过用例数
    skipped_cases = Column(Integer, default=0, comment="跳过用例数")

    # 阻塞用例数
    blocked_cases = Column(Integer, default=0, comment="阻塞用例数")

    # 通过率
    pass_rate = Column(Float, default=0.0, comment="通过率")

    # 报告内容 - JSON格式存储
    content = Column(JSON, nullable=True, comment="报告内容")

    # 报告文件路径 - 可选
    file_path = Column(String(500), nullable=True, comment="报告文件路径")

    # 报告摘要
    summary = Column(Text, nullable=True, comment="报告摘要")

    # 问题统计 - JSON格式存储
    issues = Column(JSON, nullable=True, comment="问题统计")

    # 附加数据 - JSON格式存储
    extra_data = Column(JSON, nullable=True, comment="附加数据")

    # 关联关系
    # 报告-测试用例关联
    test_case = relationship("TestCase", back_populates="test_reports")

    # 报告-代理关联
    agent = relationship("Agent", back_populates="test_reports")

    # 报告-创建者关联
    creator = relationship("User", foreign_keys=[created_by_id])

    def __init__(self, name: str, description: str = None, 
                 report_type: str = ReportType.EXECUTION.value,
                 test_case_id: int = None, agent_id: int = None, 
                 created_by_id: int = None, extra_data: Dict[str, Any] = None):
        """
        初始化测试报告

        Args:
            name: 报告名称
            description: 报告描述
            report_type: 报告类型
            test_case_id: 关联的测试用例ID
            agent_id: 关联的代理ID
            created_by_id: 创建者ID
            extra_data: 附加数据
        """
        self.name = name
        self.description = description
        self.report_type = report_type
        self.status = ReportStatus.GENERATING.value
        self.test_case_id = test_case_id
        self.agent_id = agent_id
        self.created_by_id = created_by_id
        self.total_cases = 0
        self.passed_cases = 0
        self.failed_cases = 0
        self.skipped_cases = 0
        self.blocked_cases = 0
        self.pass_rate = 0.0
        self.extra_data = extra_data or {}

    def is_generating(self) -> bool:
        """判断是否为生成中状态"""
        return self.status == ReportStatus.GENERATING.value

    def is_completed(self) -> bool:
        """判断是否为已完成状态"""
        return self.status == ReportStatus.COMPLETED.value

    def is_failed(self) -> bool:
        """判断是否为生成失败状态"""
        return self.status == ReportStatus.FAILED.value

    def is_archived(self) -> bool:
        """判断是否为已归档状态"""
        return self.status == ReportStatus.ARCHIVED.value

    def start_execution(self):
        """开始执行"""
        self.status = ReportStatus.GENERATING.value
        self.start_time = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def complete_execution(self, summary: str = None, file_path: str = None):
        """
        完成执行
        
        Args:
            summary: 报告摘要
            file_path: 报告文件路径
        """
        self.status = ReportStatus.COMPLETED.value
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
        if summary:
            self.summary = summary
        if file_path:
            self.file_path = file_path
        self.calculate_pass_rate()
        self.updated_at = datetime.utcnow()

    def fail_execution(self, error_message: str = None):
        """
        执行失败
        
        Args:
            error_message: 错误消息
        """
        self.status = ReportStatus.FAILED.value
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
        if error_message:
            self.summary = f"报告生成失败: {error_message}"
        self.updated_at = datetime.utcnow()

    def archive(self):
        """归档报告"""
        self.status = ReportStatus.ARCHIVED.value
        self.updated_at = datetime.utcnow()

    def update_statistics(self, total: int = None, passed: int = None, 
                         failed: int = None, skipped: int = None, blocked: int = None):
        """
        更新统计信息
        
        Args:
            total: 总用例数
            passed: 通过用例数
            failed: 失败用例数
            skipped: 跳过用例数
            blocked: 阻塞用例数
        """
        if total is not None:
            self.total_cases = total
        if passed is not None:
            self.passed_cases = passed
        if failed is not None:
            self.failed_cases = failed
        if skipped is not None:
            self.skipped_cases = skipped
        if blocked is not None:
            self.blocked_cases = blocked
        
        self.calculate_pass_rate()
        self.updated_at = datetime.utcnow()

    def calculate_pass_rate(self):
        """计算通过率"""
        if self.total_cases > 0:
            self.pass_rate = round(self.passed_cases / self.total_cases * 100, 2)
        else:
            self.pass_rate = 0.0

    def get_executed_cases(self) -> int:
        """获取已执行用例数"""
        return self.passed_cases + self.failed_cases

    def get_remaining_cases(self) -> int:
        """获取剩余用例数"""
        return self.total_cases - self.get_executed_cases() - self.skipped_cases - self.blocked_cases

    def get_execution_rate(self) -> float:
        """获取执行率"""
        if self.total_cases > 0:
            return round(self.get_executed_cases() / self.total_cases * 100, 2)
        return 0.0

    def add_issue(self, issue_type: str, description: str, severity: str = "medium"):
        """
        添加问题
        
        Args:
            issue_type: 问题类型
            description: 问题描述
            severity: 严重级别
        """
        if not self.issues:
            self.issues = []
        
        issue = {
            "type": issue_type,
            "description": description,
            "severity": severity,
            "created_at": datetime.utcnow().isoformat()
        }
        self.issues.append(issue)
        self.updated_at = datetime.utcnow()

    def update_content(self, content: Dict[str, Any]):
        """
        更新报告内容
        
        Args:
            content: 报告内容
        """
        if self.content is None:
            self.content = {}
        self.content.update(content)
        self.updated_at = datetime.utcnow()

    def update_info(self, name: str = None, description: str = None,
                   report_type: str = None, summary: str = None):
        """
        更新报告基本信息

        Args:
            name: 报告名称
            description: 报告描述
            report_type: 报告类型
            summary: 报告摘要
        """
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if report_type is not None:
            self.report_type = report_type
        if summary is not None:
            self.summary = summary
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            测试报告信息字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "report_type": self.report_type,
            "status": self.status,
            "test_case_id": self.test_case_id,
            "agent_id": self.agent_id,
            "created_by_id": self.created_by_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "skipped_cases": self.skipped_cases,
            "blocked_cases": self.blocked_cases,
            "executed_cases": self.get_executed_cases(),
            "remaining_cases": self.get_remaining_cases(),
            "pass_rate": self.pass_rate,
            "execution_rate": self.get_execution_rate(),
            "content": self.content,
            "file_path": self.file_path,
            "summary": self.summary,
            "issues": self.issues,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<TestReport(id={self.id}, name='{self.name}', status='{self.status}', pass_rate={self.pass_rate}%)>"