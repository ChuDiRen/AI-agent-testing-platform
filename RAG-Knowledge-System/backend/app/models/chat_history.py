"""
聊天历史模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class ChatHistory(SQLModel, table=True):
    """聊天历史表"""

    __tablename__ = "kb_chat_history"

    id: Optional[int] = Field(default=None, primary_key=True, description="记录ID")
    conversation_id: str = Field(max_length=64, index=True, description="会话ID")
    user_id: int = Field(foreign_key="sys_user.id", index=True, description="用户ID")
    question: str = Field(description="用户问题")
    answer: str = Field(description="AI回答")
    citations: Optional[str] = Field(default=None, description="引用信息(JSON）")

    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    deleted: int = Field(default=0, description="删除标记")
