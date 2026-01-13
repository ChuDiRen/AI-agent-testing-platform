"""
API 数据库基础配置模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base
from datetime import datetime


class ApiDbBase(Base):
    """API 数据库基础配置表"""
    __tablename__ = "t_api_database"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, comment='项目ID')
    name = Column(String(255), comment='连接名')
    ref_name = Column(String(255), comment='引用变量')
    db_type = Column(String(255), comment='数据库类型')
    db_info = Column(Text, comment='数据库连接信息')
    is_enabled = Column(String(255), comment='是否启用')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
