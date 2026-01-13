"""
API 关键字模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base
from datetime import datetime


class ApiKeyWord(Base):
    """API 关键字表"""
    __tablename__ = "t_api_keyword"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), comment='关键字名称')
    keyword_desc = Column(String(255), comment='关键字描述')
    operation_type_id = Column(Integer, comment='操作类型ID')
    keyword_fun_name = Column(String(255), comment='方法名')
    keyword_value = Column(Text, comment='方法体')
    is_enabled = Column(String(255), comment='是否启动')
    page_id = Column(Integer, comment='页面ID')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
