# Copyright (c) 2025 左岚. All rights reserved.
"""AI服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import random

from app.models.ai_chat import ChatSession, ChatMessage, AIModel
from app.schemas.ai_chat import (
    ChatSessionCreate, ChatSessionUpdate, ChatMessageCreate,
    ChatRequest, ChatResponse, TestCaseGenerateRequest
)


class AIService:
    """AI服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_session(self, session_data: ChatSessionCreate, user_id: int) -> ChatSession:
        """创建聊天会话"""
        session = ChatSession(
            **session_data.model_dump(),
            user_id=user_id
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def get_session(self, session_id: int) -> Optional[ChatSession]:
        """获取聊天会话"""
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_sessions(self, user_id: int) -> List[ChatSession]:
        """获取用户的所有会话"""
        result = await self.db.execute(
            select(ChatSession)
            .where(and_(ChatSession.user_id == user_id, ChatSession.is_active == True))
            .order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())
    
    async def update_session(self, session_id: int, session_data: ChatSessionUpdate) -> Optional[ChatSession]:
        """更新聊天会话"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        update_data = session_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(session, key, value)
        
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def delete_session(self, session_id: int) -> bool:
        """删除聊天会话"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        await self.db.delete(session)
        await self.db.commit()
        return True
    
    async def create_message(self, message_data: ChatMessageCreate) -> ChatMessage:
        """创建聊天消息"""
        message = ChatMessage(**message_data.model_dump())
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def get_session_messages(self, session_id: int, limit: int = 50) -> List[ChatMessage]:
        """获取会话的消息列表"""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def chat(self, request: ChatRequest, user_id: int) -> ChatResponse:
        """处理聊天请求"""
        # 获取或创建会话
        if request.session_id:
            session = await self.get_session(request.session_id)
            if not session:
                raise ValueError("会话不存在")
        else:
            session = await self.create_session(
                ChatSessionCreate(
                    title=request.message[:20] + "..." if len(request.message) > 20 else request.message,
                    model=request.model or "gpt-3.5-turbo"
                ),
                user_id
            )
        
        # 保存用户消息
        user_message = await self.create_message(
            ChatMessageCreate(
                session_id=session.session_id,
                role="user",
                content=request.message
            )
        )
        
        # 调用AI生成回复（这里使用模拟回复）
        ai_response = await self._generate_ai_response(
            session, 
            request.message,
            request.model,
            request.temperature,
            request.max_tokens
        )
        
        # 保存AI回复
        assistant_message = await self.create_message(
            ChatMessageCreate(
                session_id=session.session_id,
                role="assistant",
                content=ai_response["content"]
            )
        )
        
        # 更新会话时间
        session.updated_at = datetime.now()
        await self.db.commit()
        
        return ChatResponse(
            session_id=session.session_id,
            message=assistant_message,
            usage=ai_response.get("usage")
        )
    
    async def _generate_ai_response(
        self, 
        session: ChatSession, 
        message: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """生成AI回复（模拟实现）"""
        # 这里是模拟实现，实际应该调用真实的AI API
        
        # 预设的智能回复模板
        responses = [
            "我理解您的需求。让我帮您分析一下这个问题...",
            "根据您提供的信息，我建议采用以下测试策略...",
            "这是一个很好的问题。从测试的角度来看...",
            "我可以帮您生成相关的测试用例。请问您需要哪种类型的测试？",
            "让我为您总结一下关键点：\n1. ...\n2. ...\n3. ...",
        ]
        
        # 关键词匹配智能回复
        if "测试用例" in message or "用例" in message:
            content = "我可以帮您生成测试用例。请告诉我：\n1. 测试类型（API/Web/App）\n2. 功能模块\n3. 具体需求描述\n\n我会根据这些信息为您生成详细的测试用例。"
        elif "API" in message.upper():
            content = "关于API测试，我建议关注以下几个方面：\n1. 接口功能验证\n2. 参数校验\n3. 异常处理\n4. 性能测试\n5. 安全性测试\n\n您想了解哪个方面的详细信息？"
        elif "报告" in message:
            content = "测试报告应该包含以下内容：\n1. 测试概述\n2. 测试环境\n3. 测试结果统计\n4. 缺陷分析\n5. 测试结论和建议\n\n我可以帮您生成标准的测试报告模板。"
        elif "帮助" in message or "help" in message.lower():
            content = "我是AI测试助手，可以帮您：\n1. 生成测试用例\n2. 分析测试需求\n3. 提供测试建议\n4. 解答测试相关问题\n5. 生成测试报告\n\n请告诉我您需要什么帮助？"
        else:
            content = random.choice(responses)
        
        return {
            "content": content,
            "usage": {
                "prompt_tokens": len(message),
                "completion_tokens": len(content),
                "total_tokens": len(message) + len(content)
            }
        }
    
    async def generate_testcases(self, request: TestCaseGenerateRequest, user_id: int) -> List[Dict[str, Any]]:
        """生成测试用例"""
        testcases = []
        
        # 模拟生成测试用例
        for i in range(request.count):
            testcase = {
                "name": f"{request.module or '功能'}测试用例 {i+1}",
                "test_type": request.test_type,
                "module": request.module or "默认模块",
                "description": f"基于需求'{request.requirement[:50]}'生成的测试用例",
                "preconditions": "1. 系统正常运行\n2. 用户已登录\n3. 测试数据已准备",
                "test_steps": f"1. 执行{request.test_type}测试操作\n2. 验证功能正常\n3. 检查返回结果",
                "expected_result": "1. 操作成功\n2. 返回正确的结果\n3. 无异常错误",
                "priority": random.choice(["P0", "P1", "P2", "P3"]),
                "status": "draft",
                "tags": f"{request.test_type},自动生成"
            }
            testcases.append(testcase)
        
        return testcases
    
    async def get_available_models(self) -> List[AIModel]:
        """获取可用的AI模型列表"""
        result = await self.db.execute(
            select(AIModel).where(AIModel.is_enabled == True)
        )
        return list(result.scalars().all())
    
    async def create_model(self, model_data: Dict[str, Any]) -> AIModel:
        """创建AI模型配置"""
        model = AIModel(**model_data)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model

