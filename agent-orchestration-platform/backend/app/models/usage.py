"""
Usage 使用量统计模型
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class Usage(Base):
    """Usage 使用量统计模型"""

    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True, comment="Usage ID")
    execution_id = Column(Integer, ForeignKey("executions.id"), comment="Execution ID")
    agent_id = Column(Integer, ForeignKey("agents.id"), comment="Agent ID")
    user_id = Column(Integer, comment="用户 ID")
    tokens_used = Column(Integer, default=0, comment="使用 Token 数")
    execution_time = Column(Integer, comment="执行时间（秒）")
    api_calls = Column(Integer, default=1, comment="API 调用次数")
    cost = Column(Float, default=0.0, comment="成本")
    recorded_at = Column(DateTime, server_default=func.now(), comment="记录时间")


# 导出
__all__ = ["Usage"]
