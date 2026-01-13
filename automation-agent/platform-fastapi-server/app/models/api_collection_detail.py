"""
API 集合详情模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base
from datetime import datetime


class ApiCollectionDetail(Base):
    """API 集合详情表"""
    __tablename__ = "t_api_collection_detail"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_info_id = Column(Integer, comment='集合信息ID')
    api_info_id = Column(Integer, comment='API信息ID')
    run_order = Column(Integer, comment='执行顺序')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
