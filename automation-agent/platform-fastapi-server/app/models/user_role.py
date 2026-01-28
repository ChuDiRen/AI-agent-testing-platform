"""
用户角色关联表
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class UserRole(Base):
    """用户角色关联表"""
    __tablename__ = "t_user_role"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    user_id = Column(Integer, ForeignKey('t_user.id', ondelete='CASCADE'), nullable=False, index=True, comment='用户ID')
    role_id = Column(Integer, ForeignKey('t_role.id', ondelete='CASCADE'), nullable=False, index=True, comment='角色ID')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    
    # 关系
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
        Index('idx_user_role_user', 'user_id'),
        Index('idx_user_role_role', 'role_id'),
        {'comment': '用户角色关联表'}
    )
