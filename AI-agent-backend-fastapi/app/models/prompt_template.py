# Copyright (c) 2025 左岚. All rights reserved.
"""提示词模板模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class PromptTemplate(Base):
    """提示词模板表"""
    __tablename__ = "t_prompt_template"

    template_id = Column(Integer, primary_key=True, autoincrement=True, comment="模板ID")
    name = Column(String(200), nullable=False, comment="模板名称")
    template_type = Column(String(50), nullable=False, default="testcase_generation", comment="模板类型")
    test_type = Column(String(20), nullable=True, comment="测试类型: API/Web/App/通用")
    content = Column(Text, nullable=False, comment="提示词内容")
    variables = Column(Text, nullable=True, comment="变量说明(JSON格式)")
    is_default = Column(Boolean, default=False, comment="是否默认模板")
    is_active = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, nullable=True, comment="模板描述")
    
    created_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=True, comment="创建人ID")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    modify_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="修改时间")
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by], backref="created_prompt_templates")

