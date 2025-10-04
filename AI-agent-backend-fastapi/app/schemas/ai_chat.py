# Copyright (c) 2025 左岚. All rights reserved.
"""AI聊天Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessageBase(BaseModel):
    """聊天消息基础模型"""
    role: str = Field(..., description="角色: user/assistant/system")
    content: str = Field(..., description="消息内容")


class ChatMessageCreate(ChatMessageBase):
    """创建聊天消息"""
    session_id: Optional[int] = Field(None, description="会话ID")


class ChatMessageResponse(ChatMessageBase):
    """聊天消息响应"""
    message_id: int
    session_id: int
    tokens: Optional[int] = None
    model: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    """聊天会话基础模型"""
    title: str = Field("新对话", description="会话标题")
    model: str = Field("gpt-3.5-turbo", description="AI模型")
    system_prompt: Optional[str] = Field(None, description="系统提示词")


class ChatSessionCreate(ChatSessionBase):
    """创建聊天会话"""
    pass


class ChatSessionUpdate(BaseModel):
    """更新聊天会话"""
    title: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None


class ChatSessionResponse(ChatSessionBase):
    """聊天会话响应"""
    session_id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatSessionDetail(ChatSessionResponse):
    """聊天会话详情"""
    messages: List[ChatMessageResponse] = []
    context: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    session_id: Optional[int] = Field(None, description="会话ID，不传则创建新会话")
    model: Optional[str] = Field(None, description="指定模型")
    stream: bool = Field(False, description="是否流式返回")
    temperature: Optional[float] = Field(None, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="最大Token数")


class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: int
    message: ChatMessageResponse
    usage: Optional[Dict[str, int]] = None


class AIModelBase(BaseModel):
    """AI模型基础模型"""
    name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商: openai/claude/local")
    model_key: str = Field(..., description="模型标识")
    api_key: Optional[str] = Field(None, description="API密钥")
    api_base: Optional[str] = Field(None, description="API基础URL")
    max_tokens: int = Field(4096, description="最大Token数")
    temperature: str = Field("0.7", description="温度参数")
    description: Optional[str] = Field(None, description="模型描述")
    config: Optional[Dict[str, Any]] = Field(None, description="额外配置")


class AIModelCreate(AIModelBase):
    """创建AI模型"""
    is_enabled: bool = Field(True, description="是否启用")


class AIModelUpdate(BaseModel):
    """更新AI模型"""
    name: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[str] = None
    is_enabled: Optional[bool] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class AIModelResponse(AIModelBase):
    """AI模型响应"""
    model_id: int
    is_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TestCaseGenerateRequest(BaseModel):
    """测试用例生成请求"""
    requirement: str = Field(..., description="需求描述")
    test_type: str = Field("API", description="测试类型: API/WEB/APP")
    module: Optional[str] = Field(None, description="所属模块")
    count: int = Field(5, ge=1, le=20, description="生成数量")


class TestCaseGenerateResponse(BaseModel):
    """测试用例生成响应"""
    testcases: List[Dict[str, Any]] = Field(..., description="生成的测试用例列表")
    total: int = Field(..., description="生成数量")

