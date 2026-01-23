"""
反馈模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Feedback(SQLModel, table=True):
    """反馈表"""

    __tablename__ = "kb_feedback"

    id: Optional[int] = Field(default=None, primary_key=True, description="反馈ID")
    chat_history_id: int = Field(foreign_key="kb_chat_history.id", description="聊天历史ID")
    helpful: bool = Field(description="是否有帮助")
    comment: Optional[str] = Field(default=None, max_length=500, description="评论")

    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    deleted: int = Field(default=0, description="删除标记")
