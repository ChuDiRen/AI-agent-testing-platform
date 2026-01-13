"""
API 集合信息模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base
from datetime import datetime


class ApiCollectionInfo(Base):
    """API 集合信息表"""
    __tablename__ = "t_api_collection_info"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, default=None, comment='项目ID')
    collection_name = Column(String(255), default=None, comment='测试集合名称')
    collection_desc = Column(String(255), default=None, comment='测试集合描述')
    collection_env = Column(Text, default=None, comment='测试集合全局变量')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
