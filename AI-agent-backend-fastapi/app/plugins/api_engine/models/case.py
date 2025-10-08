# Copyright (c) 2025 左岚. All rights reserved.
"""
测试用例数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ApiEngineCase(Base):
    """测试用例表"""
    __tablename__ = "t_plugin_api_engine_case"

    case_id = Column(Integer, primary_key=True, autoincrement=True, comment="用例ID")
    suite_id = Column(Integer, ForeignKey("t_plugin_api_engine_suite.suite_id"), nullable=False, comment="所属套件ID")
    name = Column(String(200), nullable=False, comment="用例名称")
    description = Column(Text, nullable=True, comment="用例描述")
    
    # 配置模式: form(表单配置) / yaml(YAML编辑)
    config_type = Column(String(10), default='form', comment="配置类型:form/yaml")
    
    # 表单模式配置(JSON格式存储)
    config_data = Column(JSON, nullable=True, comment="表单配置数据")
    
    # YAML模式配置
    yaml_content = Column(Text, nullable=True, comment="YAML内容")
    
    # 其他字段
    sort_order = Column(Integer, default=0, comment="排序序号")
    status = Column(String(20), default='draft', comment="状态:draft/active/disabled")
    tags = Column(String(200), nullable=True, comment="标签,逗号分隔")
    
    # 关联关系
    created_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    suite = relationship("ApiEngineSuite", back_populates="cases")
    creator = relationship("User", foreign_keys=[created_by], backref="api_engine_cases")
    executions = relationship("ApiEngineExecution", back_populates="case", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ApiEngineCase(case_id={self.case_id}, name='{self.name}', config_type='{self.config_type}')>"

