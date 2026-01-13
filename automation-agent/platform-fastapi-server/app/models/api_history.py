"""
API 历史记录模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base
from datetime import datetime


class ApiHistory(Base):
    """API 历史记录表"""
    __tablename__ = "t_api_history"
    
    id = Column(Integer, primary_key=True, comment='记录编号')
    collection_info_id = Column(Integer, comment='关联t_app_collection_info表主键id')
    history_desc = Column(String(255), comment='运行记录简述')
    history_detail = Column(Text, comment='运行详细记录')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
