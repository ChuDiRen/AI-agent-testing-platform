"""
API资源模型
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class ApiResource(Base):
    """API资源表"""
    __tablename__ = "t_api_resource"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    path = Column(String(500), nullable=False, comment='API路径（如 /api/v1/user/list）')
    method = Column(String(10), nullable=False, comment='HTTP方法（GET, POST, PUT, DELETE等）')
    summary = Column(String(200), nullable=True, comment='API说明')
    tags = Column(String(200), nullable=True, comment='API标签（用逗号分隔）')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    # 关系
    roles = relationship("RoleApi", back_populates="api", cascade="all, delete-orphan")
