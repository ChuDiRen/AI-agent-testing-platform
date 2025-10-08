# Copyright (c) 2025 左岚. All rights reserved.
"""
测试执行记录数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ApiEngineExecution(Base):
    """测试执行记录表"""
    __tablename__ = "t_plugin_api_engine_execution"

    execution_id = Column(Integer, primary_key=True, autoincrement=True, comment="执行记录ID")
    case_id = Column(Integer, ForeignKey("t_plugin_api_engine_case.case_id"), nullable=False, comment="用例ID")
    task_id = Column(String(100), unique=True, nullable=False, comment="Celery任务ID")
    
    # 执行状态: pending(等待) / running(运行中) / success(成功) / failed(失败) / error(错误)
    status = Column(String(20), default='pending', comment="执行状态")
    
    # 执行结果
    result = Column(JSON, nullable=True, comment="执行结果(JSON格式)")
    logs = Column(Text, nullable=True, comment="执行日志")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 统计信息
    duration = Column(Float, nullable=True, comment="执行时长(秒)")
    steps_total = Column(Integer, default=0, comment="总步骤数")
    steps_passed = Column(Integer, default=0, comment="通过步骤数")
    steps_failed = Column(Integer, default=0, comment="失败步骤数")
    
    # 关联关系
    executed_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="执行人ID")
    executed_at = Column(DateTime, default=datetime.now, comment="执行时间")
    finished_at = Column(DateTime, nullable=True, comment="完成时间")
    
    # 关系
    case = relationship("ApiEngineCase", back_populates="executions")
    executor = relationship("User", foreign_keys=[executed_by], backref="api_engine_executions")
    
    def __repr__(self):
        return f"<ApiEngineExecution(execution_id={self.execution_id}, task_id='{self.task_id}', status='{self.status}')>"

