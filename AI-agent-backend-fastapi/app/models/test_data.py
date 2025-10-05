"""
Copyright (c) 2025 左岚. All rights reserved.
测试数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class TestData(Base):
    """测试数据模型"""

    __tablename__ = "test_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="数据名称")
    data_type = Column(String(50), nullable=False, default="json", comment="数据类型: json, csv, text, sql")
    description = Column(Text, comment="描述")
    content = Column(Text, nullable=False, comment="数据内容")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "data_type": self.data_type,
            "description": self.description,
            "content": self.content,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }

