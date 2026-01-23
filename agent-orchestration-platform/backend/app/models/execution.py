"""
Execution 执行记录模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Execution(Base):
    """Execution 执行记录模型"""

    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, index=True, comment="Execution ID")
    workflow_id = Column(Integer, ForeignKey("workflows.id"), comment="Workflow ID")
    agent_id = Column(Integer, ForeignKey("agents.id"), comment="Agent ID")
    status = Column(String(20), default="pending", comment="执行状态: pending, running, completed, failed, cancelled")
    input_data = Column(Text, comment="输入数据 (JSON)")
    output_data = Column(Text, comment="输出数据 (JSON)")
    error_message = Column(Text, comment="错误信息")
    logs = Column(Text, comment="执行日志")
    started_at = Column(DateTime, server_default=func.now(), comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")

    # 关联关系
    workflow = relationship("Workflow", back_populates="executions")
    agent = relationship("Agent", back_populates="executions")
    agent_records = relationship("AgentExecution", back_populates="execution")


# 导出
__all__ = ["Execution"]
