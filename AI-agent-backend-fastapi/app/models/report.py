# Copyright (c) 2025 左岚. All rights reserved.
"""测试报告模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class TestReport(Base):
    """测试报告表"""
    __tablename__ = "t_report"

    report_id = Column(Integer, primary_key=True, autoincrement=True, comment="报告ID")  # 主键ID
    name = Column(String(200), nullable=False, comment="报告名称")  # 报告名称
    description = Column(Text, nullable=True, comment="报告描述")  # 报告描述
    report_type = Column(String(20), nullable=False, default="execution", comment="报告类型")  # execution/summary/detailed/custom
    status = Column(String(20), nullable=False, default="generating", comment="状态")  # generating/completed/failed/archived
    
    # 关联信息
    test_case_id = Column(Integer, ForeignKey("t_testcase.testcase_id"), nullable=True, comment="关联测试用例ID")  # 关联测试用例
    agent_id = Column(Integer, nullable=True, comment="关联AI代理ID")  # 关联AI代理
    created_by_id = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="创建人ID")  # 创建人
    
    # 执行信息
    start_time = Column(DateTime, nullable=True, comment="开始时间")  # 开始时间
    end_time = Column(DateTime, nullable=True, comment="结束时间")  # 结束时间
    duration = Column(Float, nullable=True, comment="执行时长(秒)")  # 执行时长
    
    # 统计数据
    total_cases = Column(Integer, nullable=False, default=0, comment="总用例数")  # 总用例数
    passed_cases = Column(Integer, nullable=False, default=0, comment="通过用例数")  # 通过用例数
    failed_cases = Column(Integer, nullable=False, default=0, comment="失败用例数")  # 失败用例数
    skipped_cases = Column(Integer, nullable=False, default=0, comment="跳过用例数")  # 跳过用例数
    blocked_cases = Column(Integer, nullable=False, default=0, comment="阻塞用例数")  # 阻塞用例数
    executed_cases = Column(Integer, nullable=False, default=0, comment="已执行用例数")  # 已执行用例数
    remaining_cases = Column(Integer, nullable=False, default=0, comment="剩余用例数")  # 剩余用例数
    pass_rate = Column(Float, nullable=False, default=0.0, comment="通过率")  # 通过率
    execution_rate = Column(Float, nullable=False, default=0.0, comment="执行率")  # 执行率
    
    # 报告内容
    content = Column(JSON, nullable=True, comment="报告内容JSON")  # 报告详细内容
    file_path = Column(String(500), nullable=True, comment="报告文件路径")  # 报告文件路径
    summary = Column(Text, nullable=True, comment="报告摘要")  # 报告摘要
    issues = Column(JSON, nullable=True, comment="问题列表JSON")  # 问题列表
    extra_data = Column(JSON, nullable=True, comment="扩展数据JSON")  # 扩展数据
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")  # 创建时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")  # 更新时间
    
    # 关系
    testcase = relationship("TestCase", foreign_keys=[test_case_id], backref="reports")  # 测试用例关系
    creator = relationship("User", foreign_keys=[created_by_id], backref="created_reports")  # 创建人关系


class TestExecution(Base):
    """测试执行记录表"""
    __tablename__ = "t_execution"

    execution_id = Column(Integer, primary_key=True, autoincrement=True, comment="执行ID")  # 主键ID
    report_id = Column(Integer, ForeignKey("t_report.report_id"), nullable=False, comment="关联报告ID")  # 关联报告
    testcase_id = Column(Integer, ForeignKey("t_testcase.testcase_id"), nullable=False, comment="测试用例ID")  # 测试用例
    
    # 执行信息
    status = Column(String(20), nullable=False, default="pending", comment="执行状态")  # pending/running/passed/failed/skipped/blocked
    start_time = Column(DateTime, nullable=True, comment="开始时间")  # 开始时间
    end_time = Column(DateTime, nullable=True, comment="结束时间")  # 结束时间
    duration = Column(Float, nullable=True, comment="执行时长(秒)")  # 执行时长
    
    # 执行结果
    actual_result = Column(Text, nullable=True, comment="实际结果")  # 实际结果
    error_message = Column(Text, nullable=True, comment="错误信息")  # 错误信息
    stack_trace = Column(Text, nullable=True, comment="堆栈跟踪")  # 堆栈跟踪
    screenshots = Column(JSON, nullable=True, comment="截图列表JSON")  # 截图列表
    logs = Column(Text, nullable=True, comment="执行日志")  # 执行日志
    
    # 环境信息
    environment = Column(String(50), nullable=True, comment="执行环境")  # 执行环境
    executor = Column(String(100), nullable=True, comment="执行器")  # 执行器
    extra_data = Column(JSON, nullable=True, comment="扩展数据JSON")  # 扩展数据
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")  # 创建时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")  # 更新时间
    
    # 关系
    report = relationship("TestReport", foreign_keys=[report_id], backref="executions")  # 报告关系
    testcase = relationship("TestCase", foreign_keys=[testcase_id], backref="executions")  # 测试用例关系

