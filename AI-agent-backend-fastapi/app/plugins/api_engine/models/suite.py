# Copyright (c) 2025 左岚. All rights reserved.
"""
测试套件数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ApiEngineSuite(Base):
    """测试套件表"""
    __tablename__ = "t_plugin_api_engine_suite"

    suite_id = Column(Integer, primary_key=True, autoincrement=True, comment="套件ID")
    name = Column(String(200), nullable=False, comment="套件名称")
    description = Column(Text, nullable=True, comment="套件描述")
    global_context = Column(JSON, nullable=True, comment="全局变量配置(context.yaml内容)")
    
    # 关联关系
    created_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by], backref="api_engine_suites")
    cases = relationship("ApiEngineCase", back_populates="suite", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ApiEngineSuite(suite_id={self.suite_id}, name='{self.name}')>"

