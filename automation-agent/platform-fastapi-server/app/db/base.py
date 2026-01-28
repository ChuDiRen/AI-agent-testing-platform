"""
数据库基础模块
定义 SQLAlchemy Base 基类
"""
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from datetime import datetime


@as_declarative()
class Base:
    """SQLAlchemy 模型基类"""
    __name__: str
    __allow_unmapped__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        """自动生成表名"""
        return cls.__name__.lower()

    # 公共字段
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
