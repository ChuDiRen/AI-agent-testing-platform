# Copyright (c) 2025 左岚. All rights reserved.
"""
浏览器自动化测试数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class BrowserTestSuite(Base):
    """浏览器测试套件表"""
    __tablename__ = "t_plugin_api_engine_browser_suite"

    suite_id = Column(Integer, primary_key=True, autoincrement=True, comment="测试套件ID")
    name = Column(String(200), nullable=False, comment="套件名称")
    description = Column(Text, nullable=True, comment="套件描述")

    # 浏览器配置
    browser_type = Column(String(20), default='chrome', comment="浏览器类型:chrome/firefox/edge/safari")
    browser_version = Column(String(50), nullable=True, comment="浏览器版本")
    headless = Column(Boolean, default=True, comment="是否无头模式")
    window_size = Column(String(20), default='1920x1080', comment="窗口大小")

    # 执行配置
    timeout = Column(Integer, default=30, comment="超时时间(秒)")
    retry_count = Column(Integer, default=0, comment="重试次数")
    parallel_execution = Column(Boolean, default=False, comment="是否并行执行")
    max_parallel = Column(Integer, default=3, comment="最大并行数")

    # 环境配置
    environment = Column(JSON, nullable=True, comment="环境配置")
    capabilities = Column(JSON, nullable=True, comment="浏览器能力配置")

    # 状态字段
    status = Column(String(20), default='active', comment="状态:active/inactive")
    tags = Column(String(200), nullable=True, comment="标签")

    # 时间字段
    created_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<BrowserTestSuite(suite_id={self.suite_id}, name='{self.name}')>"


class BrowserTestCase(Base):
    """浏览器测试用例表"""
    __tablename__ = "t_plugin_api_engine_browser_case"

    case_id = Column(Integer, primary_key=True, autoincrement=True, comment="测试用例ID")
    suite_id = Column(Integer, ForeignKey("t_plugin_api_engine_browser_suite.suite_id"), nullable=False, comment="所属套件ID")
    name = Column(String(200), nullable=False, comment="用例名称")
    description = Column(Text, nullable=True, comment="用例描述")

    # 测试步骤配置
    test_steps = Column(JSON, nullable=False, comment="测试步骤(JSON数组)")

    # 测试数据
    test_data = Column(JSON, nullable=True, comment="测试数据")

    # 验证断言
    assertions = Column(JSON, nullable=True, comment="验证断言配置")

    # 执行配置
    priority = Column(String(10), default='P2', comment="优先级:P0/P1/P2/P3")
    timeout = Column(Integer, nullable=True, comment="超时时间(秒)")
    retry_count = Column(Integer, nullable=True, comment="重试次数")

    # 状态字段
    status = Column(String(20), default='active', comment="状态:draft/active/inactive")
    tags = Column(String(200), nullable=True, comment="标签")
    sort_order = Column(Integer, default=0, comment="排序序号")

    # 时间字段
    created_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    suite = relationship("BrowserTestSuite", backref="cases")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<BrowserTestCase(case_id={self.case_id}, name='{self.name}')>"


class BrowserTestExecution(Base):
    """浏览器测试执行记录表"""
    __tablename__ = "t_plugin_api_engine_browser_execution"

    execution_id = Column(Integer, primary_key=True, autoincrement=True, comment="执行记录ID")
    case_id = Column(Integer, ForeignKey("t_plugin_api_engine_browser_case.case_id"), nullable=False, comment="用例ID")
    suite_id = Column(Integer, ForeignKey("t_plugin_api_engine_browser_suite.suite_id"), nullable=False, comment="套件ID")

    # 任务信息
    task_id = Column(String(100), unique=True, nullable=False, comment="Celery任务ID")
    batch_execution_id = Column(String(100), nullable=True, comment="批量执行ID")

    # 执行状态
    status = Column(String(20), default='pending', comment="执行状态:pending/running/success/failed/error")

    # 执行结果
    result = Column(JSON, nullable=True, comment="执行结果(JSON格式)")
    logs = Column(Text, nullable=True, comment="执行日志")
    error_message = Column(Text, nullable=True, comment="错误信息")
    screenshots = Column(JSON, nullable=True, comment="截图文件路径列表")

    # 性能指标
    duration = Column(Integer, nullable=True, comment="执行时长(毫秒)")
    memory_usage = Column(Integer, nullable=True, comment="内存使用峰值(MB)")
    cpu_usage = Column(Integer, nullable=True, comment="CPU使用峰值(%)")

    # 步骤统计
    steps_total = Column(Integer, default=0, comment="总步骤数")
    steps_passed = Column(Integer, default=0, comment="通过步骤数")
    steps_failed = Column(Integer, default=0, comment="失败步骤数")

    # 详细步骤结果
    step_results = Column(JSON, nullable=True, comment="步骤执行结果")

    # 浏览器信息
    browser_info = Column(JSON, nullable=True, comment="浏览器信息")
    environment_info = Column(JSON, nullable=True, comment="环境信息")

    # 时间信息
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")

    # 执行人
    executed_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="执行人ID")
    executed_at = Column(DateTime, default=datetime.now, comment="执行时间")
    finished_at = Column(DateTime, nullable=True, comment="完成时间")

    # 关系
    case = relationship("BrowserTestCase", backref="executions")
    suite = relationship("BrowserTestSuite")
    executor = relationship("User", foreign_keys=[executed_by])

    def __repr__(self):
        return f"<BrowserTestExecution(execution_id={self.execution_id}, status='{self.status}')>"


class BrowserTestStep(Base):
    """浏览器测试步骤表"""
    __tablename__ = "t_plugin_api_engine_browser_step"

    step_id = Column(Integer, primary_key=True, autoincrement=True, comment="步骤ID")
    case_id = Column(Integer, ForeignKey("t_plugin_api_engine_browser_case.case_id"), nullable=False, comment="所属用例ID")

    # 步骤信息
    step_number = Column(Integer, nullable=False, comment="步骤序号")
    step_name = Column(String(200), nullable=False, comment="步骤名称")
    step_type = Column(String(50), nullable=False, comment="步骤类型")

    # 步骤配置
    action_config = Column(JSON, nullable=False, comment="动作配置")
    wait_config = Column(JSON, nullable=True, comment="等待配置")

    # 验证配置
    validation_config = Column(JSON, nullable=True, comment="验证配置")

    # 截图配置
    screenshot_config = Column(JSON, nullable=True, comment="截图配置")

    # 条件配置
    condition_config = Column(JSON, nullable=True, comment="条件配置")

    # 状态字段
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, nullable=True, comment="步骤描述")

    # 关系
    case = relationship("BrowserTestCase", backref="steps")

    def __repr__(self):
        return f"<BrowserTestStep(step_id={self.step_id}, case_id={self.case_id}, step_type='{self.step_type}')>"


class BrowserTestEnvironment(Base):
    """浏览器测试环境表"""
    __tablename__ = "t_plugin_api_engine_browser_environment"

    env_id = Column(Integer, primary_key=True, autoincrement=True, comment="环境ID")
    name = Column(String(100), nullable=False, comment="环境名称")
    description = Column(Text, nullable=True, comment="环境描述")

    # 环境配置
    base_url = Column(String(500), nullable=True, comment="基础URL")
    proxy_config = Column(JSON, nullable=True, comment="代理配置")
    network_conditions = Column(JSON, nullable=True, comment="网络条件配置")

    # 浏览器配置
    browser_config = Column(JSON, nullable=True, comment="浏览器配置")
    capabilities = Column(JSON, nullable=True, comment="特殊能力配置")

    # 测试数据配置
    test_data_config = Column(JSON, nullable=True, comment="测试数据配置")
    variables = Column(JSON, nullable=True, comment="环境变量")

    # 状态字段
    is_default = Column(Boolean, default=False, comment="是否默认环境")
    is_active = Column(Boolean, default=True, comment="是否启用")

    # 时间字段
    created_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<BrowserTestEnvironment(env_id={self.env_id}, name='{self.name}')>"