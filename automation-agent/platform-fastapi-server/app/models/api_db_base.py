"""
API 数据库基础配置模型
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApiDbBase(Base):
    """API 数据库基础配置表"""
    __tablename__ = "t_api_database"
    
    project_id = Column(Integer, ForeignKey('t_api_project.id', ondelete='CASCADE'), nullable=False, index=True, comment='项目ID')
    name = Column(String(100), nullable=False, comment='连接名')
    ref_name = Column(String(50), nullable=False, comment='引用变量')
    db_type = Column(String(20), nullable=False, comment='数据库类型(mysql/postgresql/oracle/sqlserver等)')
    db_config = Column(JSON, nullable=False, comment='数据库连接配置(JSON格式)')
    is_enabled = Column(Boolean, nullable=False, default=True, comment='是否启用')
    
    # 关系
    project = relationship("ApiProject", backref="databases")
    
    __table_args__ = (
        UniqueConstraint('project_id', 'ref_name', name='uq_database_ref'),
        Index('idx_database_project_enabled', 'project_id', 'is_enabled'),
        {'comment': 'API数据库配置表'}
    )
