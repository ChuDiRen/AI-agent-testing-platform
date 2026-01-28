"""
角色API关联表
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class RoleApi(Base):
    """角色API关联表"""
    __tablename__ = "t_role_api"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    role_id = Column(Integer, ForeignKey('t_role.id', ondelete='CASCADE'), nullable=False, index=True, comment='角色ID')
    api_id = Column(Integer, ForeignKey('t_api.id', ondelete='CASCADE'), nullable=False, index=True, comment='API权限ID')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    
    # 关系
    role = relationship("Role", back_populates="apis")
    api = relationship("Api", back_populates="roles")
    
    __table_args__ = (
        UniqueConstraint('role_id', 'api_id', name='uq_role_api'),
        Index('idx_role_api_role', 'role_id'),
        Index('idx_role_api_api', 'api_id'),
        {'comment': '角色API关联表'}
    )
