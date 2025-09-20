# Copyright (c) 2025 左岚. All rights reserved.
"""
聊天会话实体
定义聊天会话的数据库模型
"""

from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from .base import BaseEntity


class ChatSession(BaseEntity):
    """
    聊天会话实体类
    定义聊天会话的基本信息
    """
    __tablename__ = "chat_session"
    __allow_unmapped__ = True

    # 会话ID - 唯一标识符
    session_id = Column(String(36), nullable=False, unique=True, index=True, comment="会话ID")

    # 用户ID - 外键关联用户表
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment="用户ID")

    # AI模型ID - 外键关联AI模型表
    model_id = Column(Integer, ForeignKey('ai_model.id'), nullable=False, comment="AI模型ID")

    # 会话标题
    title = Column(String(200), nullable=False, comment="会话标题")

    # 系统提示词
    system_prompt = Column(Text, nullable=True, comment="系统提示词")

    # 会话配置 - JSON格式存储
    config = Column(JSON, nullable=True, comment="会话配置")

    # 关联关系
    user = relationship("User", foreign_keys=[user_id])
    model = relationship("AIModel", foreign_keys=[model_id])
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_chat_session_user_created', 'user_id', 'created_at'),
        Index('idx_chat_session_model', 'model_id'),
    )

    def __init__(self, session_id: str, user_id: int, model_id: int,
                 title: str, system_prompt: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化聊天会话

        Args:
            session_id: 会话ID
            user_id: 用户ID
            model_id: AI模型ID
            title: 会话标题
            system_prompt: 系统提示词
            config: 会话配置
        """
        self.session_id = session_id
        self.user_id = user_id
        self.model_id = model_id
        self.title = title
        self.system_prompt = system_prompt
        self.config = config or {}

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        转换为字典格式

        Args:
            include_sensitive: 是否包含敏感信息

        Returns:
            会话信息字典
        """
        result = {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "model_id": self.model_id,
            "title": self.title,
            "system_prompt": self.system_prompt,
            "config": self.config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

        return result

    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}', title='{self.title}')>"


class ChatMessage(BaseEntity):
    """
    聊天消息实体类
    定义聊天消息的基本信息
    """
    __tablename__ = "chat_message"
    __allow_unmapped__ = True

    # 会话ID - 关联聊天会话
    session_id = Column(String(36), ForeignKey('chat_session.session_id'), nullable=False, comment="会话ID")

    # 消息角色 - system, user, assistant
    role = Column(String(20), nullable=False, comment="消息角色")

    # 消息内容
    content = Column(Text, nullable=False, comment="消息内容")

    # 消息元数据 - JSON格式存储
    message_metadata = Column(JSON, nullable=True, comment="消息元数据")

    # 令牌数量
    tokens = Column(Integer, default=0, comment="令牌数量")

    # 费用
    cost = Column(Integer, default=0, comment="费用(分)")

    # 关联关系
    session = relationship("ChatSession", back_populates="messages")

    # 索引
    __table_args__ = (
        Index('idx_chat_message_session_created', 'session_id', 'created_at'),
        Index('idx_chat_message_role', 'role'),
    )

    def __init__(self, session_id: str, role: str, content: str,
                 metadata: Optional[Dict[str, Any]] = None,
                 tokens: int = 0, cost: int = 0):
        """
        初始化聊天消息

        Args:
            session_id: 会话ID
            role: 消息角色
            content: 消息内容
            metadata: 消息元数据
            tokens: 令牌数量
            cost: 费用(分)
        """
        self.session_id = session_id
        self.role = role
        self.content = content
        self.message_metadata = metadata or {}
        self.tokens = tokens
        self.cost = cost

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        转换为字典格式

        Args:
            include_sensitive: 是否包含敏感信息

        Returns:
            消息信息字典
        """
        result = {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "metadata": self.message_metadata,
            "tokens": self.tokens,
            "cost": self.cost,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

        return result

    def __repr__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<ChatMessage(id={self.id}, role='{self.role}', content='{content_preview}')>"
