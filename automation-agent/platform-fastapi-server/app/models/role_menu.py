"""
角色菜单关联表
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class RoleMenu(Base):
    """角色菜单关联表"""
    __tablename__ = "t_role_menu"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    role_id = Column(Integer, ForeignKey('t_role.id'), nullable=False, comment='角色ID')
    menu_id = Column(Integer, ForeignKey('t_menu.id'), nullable=False, comment='菜单ID')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    
    # 关系
    role = relationship("Role", back_populates="menus")
    menu = relationship("Menu", back_populates="roles")
