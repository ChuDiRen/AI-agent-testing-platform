"""
API 操作类型模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base
from datetime import datetime


class ApiOperationType(Base):
    """API 操作类型表"""
    __tablename__ = "t_api_operation_type"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operation_type_name = Column(String(255), comment='操作类型名称')
    operation_type_desc = Column(String(255), comment='操作类型描述')
    operation_type_fun_name = Column(String(255), comment='方法名')
    operation_type_value = Column(Text, comment='方法体')
    is_enabled = Column(String(255), comment='是否启用')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
