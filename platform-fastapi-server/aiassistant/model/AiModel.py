from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class AiModel(SQLModel, table=True):
    """AI模型配置表 - 支持DeepSeek、通义千问等多种AI模型"""
    
    __tablename__ = "ai_model"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    model_name: str = Field(max_length=100, index=True)  # 模型名称（如：DeepSeek-Chat）
    model_code: str = Field(max_length=50, unique=True)  # 模型代码（如：deepseek-chat）
    provider: str = Field(max_length=50)  # 提供商（如：DeepSeek、阿里云、OpenAI）
    api_url: str = Field(max_length=500)  # API地址
    api_key: Optional[str] = Field(default=None, max_length=500)  # API密钥（加密存储）
    is_enabled: bool = Field(default=True)  # 是否启用
    description: Optional[str] = Field(default=None, max_length=500)  # 模型描述
    create_time: datetime = Field(default_factory=datetime.now)  # 创建时间
    modify_time: datetime = Field(default_factory=datetime.now)  # 修改时间
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "DeepSeek-Chat",
                "model_code": "deepseek-chat",
                "provider": "DeepSeek",
                "api_url": "https://api.deepseek.com/v1/chat/completions",
                "api_key": "sk-xxxxx",
                "is_enabled": True,
                "description": "DeepSeek AI模型，支持流式输出"
            }
        }

