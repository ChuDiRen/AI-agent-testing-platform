"""
Agent Execution 历史模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class AgentExecution(Base):
    """Agent 执行历史模型"""

    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True, comment="执行 ID")
    execution_id = Column(Integer, ForeignKey("executions.id"), nullable=False, index=True, comment="Execution ID")
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, comment="Agent ID")
    status = Column(String(20), nullable=False, comment="执行状态")
    input_data = Column(Text, comment="输入数据 (JSON)")
    output_data = Column(Text, comment="输出数据 (JSON)")
    error_message = Column(Text, comment="错误信息")
    tokens_used = Column(Integer, default=0, comment="使用 Token 数")
    execution_time = Column(Float, comment="执行时间（秒）")
    cost = Column(Float, default=0.0, comment="成本")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    completed_at = Column(DateTime, comment="完成时间")

    # 关联关系
    execution = relationship("Execution", back_populates="agent_records")
    agent = relationship("Agent", back_populates="executions_history")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "agent_id": self.agent_id,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "tokens_used": self.tokens_used,
            "execution_time": self.execution_time,
            "cost": self.cost,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


# 导出
__all__ = ["AgentExecution"]
