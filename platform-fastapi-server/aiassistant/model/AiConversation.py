from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class AiConversation(SQLModel, table=True):
    """AI对话会话表 - 管理用户与AI的对话会话"""
    
    __tablename__ = "ai_conversation"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)  # 用户ID
    session_title: str = Field(max_length=200, index=True)  # 会话标题
    model_id: int = Field(index=True)  # 使用的AI模型ID
    test_type: Optional[str] = Field(default=None, max_length=20)  # 测试类型（API/Web/App）
    project_id: Optional[int] = Field(default=None, index=True)  # 关联的项目ID
    status: str = Field(max_length=20, default="active", index=True)  # 会话状态（active/archived/deleted）
    message_count: int = Field(default=0)  # 消息数量
    test_case_count: int = Field(default=0)  # 生成的测试用例数量
    create_time: datetime = Field(default_factory=datetime.now)  # 创建时间
    update_time: datetime = Field(default_factory=datetime.now)  # 更新时间
    last_message_time: Optional[datetime] = Field(default=None)  # 最后一条消息时间
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "session_title": "用户登录API测试",
                "model_id": 1,
                "test_type": "API",
                "project_id": 1,
                "status": "active",
                "message_count": 5,
                "test_case_count": 3
            }
        }
