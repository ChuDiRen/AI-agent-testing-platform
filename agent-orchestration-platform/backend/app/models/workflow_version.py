"""
Workflow Version 数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class WorkflowVersion(Base):
    """Workflow 版本模型"""

    __tablename__ = "workflow_versions"

    id = Column(Integer, primary_key=True, index=True, comment="版本 ID")
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False, comment="Workflow ID")
    version = Column(Integer, nullable=False, comment="版本号")
    graph_data = Column(LargeBinary, comment="工作流图数据（二进制）")
    change_summary = Column(Text, comment="变更摘要")
    is_published = Column(Boolean, default=False, comment="是否发布")
    created_by = Column(Integer, comment="创建人 ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关联关系
    # workflow = relationship("Workflow", back_populates="versions")  # 暂时注释，避免循环导入

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "version": self.version,
            "graph_data": self.graph_data.decode() if self.graph_data else None,
            "change_summary": self.change_summary,
            "is_published": self.is_published,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# 导出
__all__ = ["WorkflowVersion"]
