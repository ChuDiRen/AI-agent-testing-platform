from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AiConversationCreate(BaseModel):
    """创建对话会话"""
    model_id: int
    test_type: Optional[str] = None
    project_id: Optional[int] = None
    session_title: Optional[str] = Field(default="新对话", max_length=200)


class AiConversationUpdate(BaseModel):
    """更新对话会话"""
    session_title: Optional[str] = None
    status: Optional[str] = None


class AiConversationResponse(BaseModel):
    """对话会话响应"""
    id: int
    user_id: int
    session_title: str
    model_id: int
    test_type: Optional[str]
    project_id: Optional[int]
    status: str
    message_count: int
    test_case_count: int
    create_time: datetime
    update_time: datetime
    last_message_time: Optional[datetime]

    class Config:
        from_attributes = True


class AiConversationListResponse(BaseModel):
    """对话列表响应"""
    total: int
    items: list[AiConversationResponse]
