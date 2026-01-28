"""
API 项目模型
"""
from sqlalchemy import Column, String, Integer, ForeignKey, SmallInteger, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApiProject(Base):
    """API 项目表"""
    __tablename__ = "t_api_project"
    
    project_name = Column(String(100), nullable=False, unique=True, index=True, comment='项目名称')
    project_desc = Column(String(500), nullable=True, comment='项目描述')
    owner_id = Column(Integer, ForeignKey('t_user.id', ondelete='SET NULL'), nullable=True, index=True, comment='项目负责人ID')
    status = Column(SmallInteger, nullable=False, default=1, index=True, comment='状态(1启用/0禁用)')
    
    # 关系
    owner = relationship("User", foreign_keys=[owner_id], backref="owned_projects")
    
    __table_args__ = (
        Index('idx_project_owner_status', 'owner_id', 'status'),
        {'comment': 'API项目表'}
    )
