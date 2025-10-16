from sqlmodel import SQLModel, Field
from sqlalchemy import Text
from typing import Optional
from datetime import datetime


class AiMessage(SQLModel, table=True):
    """AI对话消息表 - 存储对话中的每条消息"""

    __tablename__ = "ai_message"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(index=True)  # 所属会话ID
    role: str = Field(max_length=20, index=True)  # 角色（user/assistant/system）
    content: str = Field(sa_type=Text)  # 消息内容
    message_type: str = Field(max_length=20, default="text", index=True)  # 消息类型（text/testcase/error/file/command）
    test_cases_json: Optional[str] = Field(default=None, sa_type=Text)  # 生成的测试用例JSON
    message_metadata: Optional[str] = Field(default=None, sa_type=Text)  # 元数据（如文件信息、参数等）
    create_time: datetime = Field(default_factory=datetime.now, index=True)  # 创建时间

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 1,
                "role": "user",
                "content": "帮我生成10个用户登录的API测试用例",
                "message_type": "text",
                "test_cases_json": None,
                "message_metadata": None
            }
        }
