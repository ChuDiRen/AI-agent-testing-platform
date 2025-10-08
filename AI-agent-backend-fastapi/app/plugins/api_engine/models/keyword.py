# Copyright (c) 2025 左岚. All rights reserved.
"""
关键字数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ApiEngineKeyword(Base):
    """自定义关键字表"""
    __tablename__ = "t_plugin_api_engine_keyword"

    keyword_id = Column(Integer, primary_key=True, autoincrement=True, comment="关键字ID")
    name = Column(String(100), unique=True, nullable=False, comment="关键字名称")
    description = Column(Text, nullable=True, comment="关键字描述")
    
    # 参数定义(JSON格式)
    # 例如: [{"name": "url", "type": "string", "required": true, "description": "请求URL"}]
    parameters = Column(JSON, nullable=True, comment="参数定义")
    
    # Python代码
    code = Column(Text, nullable=False, comment="关键字实现代码(Python)")
    
    # 是否内置关键字
    is_builtin = Column(Boolean, default=False, comment="是否内置关键字")
    
    # 关联关系
    created_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=True, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by], backref="api_engine_keywords")
    
    def __repr__(self):
        return f"<ApiEngineKeyword(keyword_id={self.keyword_id}, name='{self.name}', is_builtin={self.is_builtin})>"

