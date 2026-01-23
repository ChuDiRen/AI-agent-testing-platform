"""
部门模型
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class Dept(Base):
    """部门表"""
    __tablename__ = "t_dept"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    name = Column(String(50), nullable=False, comment='部门名称')
    desc = Column(String(200), nullable=True, comment='部门描述')
    parent_id = Column(Integer, default=0, nullable=False, comment='父部门ID（0=顶级部门）')
    order = Column(Integer, default=0, nullable=False, comment='排序号（越小越靠前）')
    is_deleted = Column(Boolean, default=False, nullable=False, comment='是否删除')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    # 关系
    users = relationship("User", back_populates="dept")
