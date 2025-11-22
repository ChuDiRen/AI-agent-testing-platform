from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AiMessageCreate(BaseModel):
    """创建消息"""
    conversation_id: int
    content: str
    message_type: str = Field(default="text")
    test_cases_json: Optional[str] = None
    message_metadata: Optional[str] = None


class MessageStreamRequest(BaseModel):
    """流式对话请求"""
    conversation_id: int
    user_message: str
    model_id: int
    test_type: Optional[str] = None
    case_format: str = Field(default="JSON")
    case_count: int = Field(default=10, ge=1, le=20)
    include_context: bool = Field(default=True)
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: int = Field(default=2000, ge=500, le=4000)


class AiMessageResponse(BaseModel):
    """消息响应"""
    id: int
    conversation_id: int
    role: str
    content: str
    message_type: str
    test_cases_json: Optional[str]
    message_metadata: Optional[str]
    create_time: datetime

    class Config:
        from_attributes = True


class AiMessageListResponse(BaseModel):
    """消息列表响应"""
    total: int
    items: list[AiMessageResponse]
