"""
角色菜单关联表
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class RoleMenu(Base):
    """角色菜单关联表"""
    __tablename__ = "t_role_menu"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    role_id = Column(Integer, ForeignKey('t_role.id', ondelete='CASCADE'), nullable=False, index=True, comment='角色ID')
    menu_id = Column(Integer, ForeignKey('t_menu.id', ondelete='CASCADE'), nullable=False, index=True, comment='菜单ID')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    
    # 关系
    role = relationship("Role", back_populates="menus")
    menu = relationship("Menu", back_populates="roles")
    
    __table_args__ = (
        UniqueConstraint('role_id', 'menu_id', name='uq_role_menu'),
        Index('idx_role_menu_role', 'role_id'),
        Index('idx_role_menu_menu', 'menu_id'),
        {'comment': '角色菜单关联表'}
    )
