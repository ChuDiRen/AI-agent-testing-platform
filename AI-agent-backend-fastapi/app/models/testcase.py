# Copyright (c) 2025 左岚. All rights reserved.
"""测试用例模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class TestCase(Base):
    """测试用例表"""
    __tablename__ = "t_testcase"

    testcase_id = Column(Integer, primary_key=True, autoincrement=True, comment="测试用例ID")  # 主键ID
    name = Column(String(200), nullable=False, comment="用例名称")  # 用例名称
    test_type = Column(String(20), nullable=False, comment="测试类型")  # API/WEB/APP
    module = Column(String(100), nullable=True, comment="所属模块")  # 所属模块
    description = Column(Text, nullable=True, comment="用例描述")  # 用例描述
    preconditions = Column(Text, nullable=True, comment="前置条件")  # 前置条件
    test_steps = Column(Text, nullable=True, comment="测试步骤")  # 测试步骤
    expected_result = Column(Text, nullable=True, comment="预期结果")  # 预期结果
    priority = Column(String(10), nullable=False, default="P2", comment="优先级")  # P0/P1/P2/P3
    status = Column(String(20), nullable=False, default="draft", comment="状态")  # draft/active/deprecated
    tags = Column(String(200), nullable=True, comment="标签")  # 标签,逗号分隔
    
    created_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="创建人ID")  # 创建人
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")  # 创建时间
    modify_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="修改时间")  # 修改时间
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by], backref="created_testcases")  # 创建人关系

