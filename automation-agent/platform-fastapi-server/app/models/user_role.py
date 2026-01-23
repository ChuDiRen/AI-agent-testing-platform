"""
用户角色关联表
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class UserRole(Base):
    """用户角色关联表"""
    __tablename__ = "t_user_role"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    user_id = Column(Integer, ForeignKey('t_user.id'), nullable=False, comment='用户ID')
    role_id = Column(Integer, ForeignKey('t_role.id'), nullable=False, comment='角色ID')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    
    # 关系
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")
