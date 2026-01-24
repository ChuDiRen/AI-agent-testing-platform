"""
API权限模型
"""
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class Api(Base):
    """API权限表"""
    __tablename__ = "t_api"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    path = Column(String(200), nullable=False, comment='API路径')
    method = Column(String(10), nullable=False, comment='HTTP方法')
    summary = Column(String(200), nullable=True, comment='API描述')
    tags = Column(String(100), nullable=True, comment='API标签')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    # 关系 - RoleApi关联对象
    roles = relationship("RoleApi", back_populates="api", cascade="all, delete-orphan")
    # 直接获取Role对象（通过secondary关系）- 参考vue-fastapi-admin
    role_objects = relationship("Role", secondary="t_role_api", back_populates="api_objects", viewonly=True)
