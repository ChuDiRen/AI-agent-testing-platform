# Copyright (c) 2025 左岚. All rights reserved.
"""AI聊天模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ChatSession(Base):
    """聊天会话表"""
    __tablename__ = "t_chat_session"

    session_id = Column(Integer, primary_key=True, autoincrement=True, comment="会话ID")  # 主键ID
    user_id = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="用户ID")  # 用户ID
    title = Column(String(200), nullable=False, default="新对话", comment="会话标题")  # 会话标题
    model = Column(String(50), nullable=False, default="gpt-3.5-turbo", comment="AI模型")  # AI模型
    system_prompt = Column(Text, nullable=True, comment="系统提示词")  # 系统提示词
    context = Column(JSON, nullable=True, comment="上下文信息")  # 上下文信息
    is_active = Column(Boolean, default=True, comment="是否活跃")  # 是否活跃
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")  # 创建时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")  # 更新时间
    
    # 关系
    user = relationship("User", foreign_keys=[user_id], backref="chat_sessions")  # 用户关系
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")  # 消息关系


class ChatMessage(Base):
    """聊天消息表"""
    __tablename__ = "t_chat_message"

    message_id = Column(Integer, primary_key=True, autoincrement=True, comment="消息ID")  # 主键ID
    session_id = Column(Integer, ForeignKey("t_chat_session.session_id"), nullable=False, comment="会话ID")  # 会话ID
    role = Column(String(20), nullable=False, comment="角色")  # user/assistant/system
    content = Column(Text, nullable=False, comment="消息内容")  # 消息内容
    tokens = Column(Integer, nullable=True, comment="Token数量")  # Token数量
    model = Column(String(50), nullable=True, comment="使用的模型")  # 使用的模型
    metadata = Column(JSON, nullable=True, comment="元数据")  # 元数据
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")  # 创建时间
    
    # 关系
    session = relationship("ChatSession", back_populates="messages")  # 会话关系


class AIModel(Base):
    """AI模型配置表"""
    __tablename__ = "t_ai_model"

    model_id = Column(Integer, primary_key=True, autoincrement=True, comment="模型ID")  # 主键ID
    name = Column(String(100), nullable=False, comment="模型名称")  # 模型名称
    provider = Column(String(50), nullable=False, comment="提供商")  # openai/claude/local
    model_key = Column(String(100), nullable=False, comment="模型标识")  # 模型标识
    api_key = Column(String(500), nullable=True, comment="API密钥")  # API密钥
    api_base = Column(String(500), nullable=True, comment="API基础URL")  # API基础URL
    max_tokens = Column(Integer, nullable=True, default=4096, comment="最大Token数")  # 最大Token数
    temperature = Column(String(10), nullable=True, default="0.7", comment="温度参数")  # 温度参数
    is_enabled = Column(Boolean, default=True, comment="是否启用")  # 是否启用
    description = Column(Text, nullable=True, comment="模型描述")  # 模型描述
    config = Column(JSON, nullable=True, comment="配置信息")  # 配置信息
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")  # 创建时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")  # 更新时间

