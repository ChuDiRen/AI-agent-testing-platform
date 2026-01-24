"""
角色模型
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class Role(Base):
    """角色表"""
    __tablename__ = "t_role"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    name = Column(String(50), unique=True, nullable=False, comment='角色名称')
    desc = Column(String(200), nullable=True, comment='角色描述')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')

    # 关系 - RoleMenu关联对象
    users = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    user_objects = relationship("User", secondary="t_user_role", back_populates="role_objects", viewonly=True)
    menus = relationship("RoleMenu", back_populates="role", cascade="all, delete-orphan")
    apis = relationship("RoleApi", back_populates="role", cascade="all, delete-orphan")
    # 直接获取Menu对象（通过secondary关系）- 参考vue-fastapi-admin
    menu_objects = relationship("Menu", secondary="t_role_menu", back_populates="role_objects", viewonly=True)
    api_objects = relationship("Api", secondary="t_role_api", back_populates="role_objects", viewonly=True)
