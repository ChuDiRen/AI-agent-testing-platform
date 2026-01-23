"""
菜单模型
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class Menu(Base):
    """菜单表"""
    __tablename__ = "t_menu"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    name = Column(String(50), nullable=False, comment='菜单名称')
    menu_type = Column(String(10), default='menu', nullable=False, comment='菜单类型（menu=菜单，directory=目录）')
    icon = Column(String(50), nullable=True, comment='菜单图标（Element Plus图标名）')
    path = Column(String(200), nullable=False, comment='路由路径')
    component = Column(String(200), nullable=True, comment='组件路径')
    order = Column(Integer, default=0, nullable=False, comment='排序号（越小越靠前）')
    parent_id = Column(Integer, default=0, nullable=False, comment='父菜单ID（0=顶级菜单）')
    is_hidden = Column(Boolean, default=False, nullable=False, comment='是否隐藏')
    keepalive = Column(Boolean, default=True, nullable=False, comment='是否缓存')
    redirect = Column(String(200), nullable=True, comment='重定向路径')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    # 关系
    roles = relationship("RoleMenu", back_populates="menu", cascade="all, delete-orphan")
