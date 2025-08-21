"""
数据库基类定义
SQLAlchemy声明性基类，所有模型都继承自此基类
"""

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime
from typing import Any


@as_declarative()
class Base:
    """
    SQLAlchemy声明性基类
    所有数据库模型都应该继承此类
    """
    __allow_unmapped__ = True  # 允许未映射的注解

    # 自动生成表名（类名转小写）
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # 通用字段
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    created_by = Column(String(50), comment="创建者")
    updated_by = Column(String(50), comment="更新者")
    is_deleted = Column(Integer, default=0, comment="是否删除(0:未删除,1:已删除)")

    def to_dict(self) -> dict:
        """
        将模型对象转换为字典
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def from_dict(cls, data: dict):
        """
        从字典创建模型对象
        """
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
