"""
数据库基础模块
定义 SQLAlchemy Base 基类
"""
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from datetime import datetime


@as_declarative()
class Base:
    """SQLAlchemy 模型基类"""
    id: int
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        """自动生成表名"""
        return cls.__name__.lower()
    
    # 公共字段
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
