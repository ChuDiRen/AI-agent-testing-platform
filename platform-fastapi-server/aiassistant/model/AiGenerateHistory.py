from sqlmodel import SQLModel, Field
from sqlalchemy import Text
from typing import Optional
from datetime import datetime


class AiGenerateHistory(SQLModel, table=True):
    """AI生成历史表 - 记录每次AI生成事件用于审计和追溯"""

    __tablename__ = "ai_generate_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)  # 用户ID
    conversation_id: int = Field(index=True)  # 对话会话ID
    model_id: int = Field(index=True)  # 使用的AI模型ID
    requirement_text: str = Field(sa_type=Text)  # 用户需求文本
    test_type: str = Field(max_length=20, index=True)  # 测试类型（API/Web/App）
    case_count: int = Field(default=0)  # 生成的测试用例数量
    generate_status: str = Field(max_length=20, default="success", index=True)  # 生成状态（success/failed/timeout）
    result_data: Optional[str] = Field(default=None, sa_type=Text)  # 生成的结果数据（JSON格式）
    error_message: Optional[str] = Field(default=None, max_length=500)  # 错误信息
    create_time: datetime = Field(default_factory=datetime.now, index=True)  # 创建时间
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "conversation_id": 1,
                "model_id": 1,
                "requirement_text": "为用户登录功能生成10个API测试用例",
                "test_type": "API",
                "case_count": 10,
                "generate_status": "success",
                "result_data": "[{...}]"
            }
        }
