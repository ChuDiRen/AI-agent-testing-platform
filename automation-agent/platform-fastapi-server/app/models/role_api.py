"""
角色API关联表
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class RoleApi(Base):
    """角色API关联表"""
    __tablename__ = "t_role_api"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    role_id = Column(Integer, ForeignKey('t_role.id'), nullable=False, comment='角色ID')
    api_id = Column(Integer, ForeignKey('t_api.id'), nullable=False, comment='API权限ID')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    
    # 关系
    role = relationship("Role", back_populates="apis")
    api = relationship("Api", back_populates="roles")
