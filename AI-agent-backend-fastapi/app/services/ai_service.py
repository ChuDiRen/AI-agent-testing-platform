# Copyright (c) 2025 左岚. All rights reserved.
"""AI服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime
import json
import random

from app.models.ai_chat import ChatSession, ChatMessage, AIModel
from app.schemas.ai_chat import (
    ChatSessionCreate, ChatSessionUpdate, ChatMessageCreate,
    ChatRequest, ChatResponse, TestCaseGenerateRequest,
    AIModelCreate, AIModelUpdate
)
from app.services.ai_client import ai_client_service


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
        """处理聊天请求(非流式)"""
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

        # 获取AI模型
        model = await self._get_model_by_key(request.model or session.model)
        if not model:
            raise ValueError(f"模型不存在或未启用: {request.model or session.model}")

        # 构建消息历史
        messages = await self._build_messages(session)

        # 调用AI生成回复
        client = ai_client_service.get_client(model)
        ai_response = await client.chat(
            messages=messages,
            stream=False,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        # 保存AI回复
        assistant_message = await self.create_message(
            ChatMessageCreate(
                session_id=session.session_id,
                role="assistant",
                content=ai_response["content"],
                tokens=ai_response.get("usage", {}).get("total_tokens"),
                model=ai_response.get("model")
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

    async def chat_stream(self, request: ChatRequest, user_id: int) -> AsyncGenerator[str, None]:
        """处理聊天请求(流式)"""
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
        await self.create_message(
            ChatMessageCreate(
                session_id=session.session_id,
                role="user",
                content=request.message
            )
        )

        # 获取AI模型
        model = await self._get_model_by_key(request.model or session.model)
        if not model:
            raise ValueError(f"模型不存在或未启用: {request.model or session.model}")

        # 构建消息历史
        messages = await self._build_messages(session)

        # 调用AI生成回复(流式)
        client = ai_client_service.get_client(model)
        full_content = ""

        async for chunk in await client.chat(
            messages=messages,
            stream=True,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        ):
            full_content += chunk
            yield chunk

        # 保存完整的AI回复
        await self.create_message(
            ChatMessageCreate(
                session_id=session.session_id,
                role="assistant",
                content=full_content,
                model=model.model_key
            )
        )

        # 更新会话时间
        session.updated_at = datetime.now()
        await self.db.commit()

    async def _get_model_by_key(self, model_key: str) -> Optional[AIModel]:
        """根据模型标识获取模型"""
        result = await self.db.execute(
            select(AIModel).where(
                and_(
                    AIModel.model_key == model_key,
                    AIModel.is_enabled == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def _build_messages(self, session: ChatSession, max_messages: Optional[int] = None) -> List[Dict[str, str]]:
        """
        构建消息历史
        
        Args:
            session: 会话对象
            max_messages: 最大消息数,默认从配置读取
        
        Returns:
            消息列表
        """
        from app.core.config import settings
        
        messages = []

        # 添加系统提示词
        if session.system_prompt:
            messages.append({
                "role": "system",
                "content": session.system_prompt
            })

        # 获取历史消息(可配置数量)
        if max_messages is None:
            max_messages = settings.AI_MAX_CONTEXT_MESSAGES
            
        history = await self.get_session_messages(session.session_id, limit=max_messages)
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return messages
    
    # ==================== AI模型管理 ====================

    async def get_available_models(self) -> List[AIModel]:
        """获取可用的AI模型列表"""
        result = await self.db.execute(
            select(AIModel).where(AIModel.is_enabled == True)
        )
        return list(result.scalars().all())

    async def create_model(self, model_data: AIModelCreate) -> AIModel:
        """创建AI模型"""
        model = AIModel(**model_data.model_dump())
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model

    async def update_model(self, model_id: int, model_data: AIModelUpdate) -> Optional[AIModel]:
        """更新AI模型"""
        result = await self.db.execute(
            select(AIModel).where(AIModel.model_id == model_id)
        )
        model = result.scalar_one_or_none()

        if not model:
            return None

        update_data = model_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(model, key, value)

        model.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(model)

        # 清除客户端缓存
        ai_client_service.clear_client(model_id)

        return model

    async def delete_model(self, model_id: int) -> bool:
        """删除AI模型"""
        result = await self.db.execute(
            select(AIModel).where(AIModel.model_id == model_id)
        )
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self.db.delete(model)
        await self.db.commit()

        # 清除客户端缓存
        ai_client_service.clear_client(model_id)

        return True

    async def test_model_connection(self, model_id: int) -> Dict[str, Any]:
        """测试AI模型连接"""
        result = await self.db.execute(
            select(AIModel).where(AIModel.model_id == model_id)
        )
        model = result.scalar_one_or_none()

        if not model:
            return {
                "success": False,
                "message": "模型不存在"
            }

        try:
            client = ai_client_service.get_client(model)
            return await client.test_connection()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "连接测试失败"
            }
    
    async def generate_testcases(self, request: TestCaseGenerateRequest, user_id: int) -> List[Dict[str, Any]]:
        """
        使用 AI 生成测试用例
        
        Args:
            request: 测试用例生成请求
            user_id: 用户ID
        
        Returns:
            生成的测试用例列表
        """
        # 构建提示词
        prompt = f"""请根据以下需求生成 {request.count} 个{request.test_type}测试用例:

需求描述:
{request.requirement}

模块: {request.module or '未指定'}

请为每个测试用例生成以下内容:
1. 测试用例名称
2. 测试描述
3. 前置条件
4. 测试步骤(详细的步骤说明)
5. 预期结果
6. 优先级(P0/P1/P2/P3)

输出格式为 JSON 数组,每个测试用例包含: name, description, preconditions, test_steps, expected_result, priority
"""

        try:
            # 获取默认的 AI 模型
            models = await self.get_available_models()
            if not models:
                # 如果没有可用模型,返回模拟数据
                return self._generate_mock_testcases(request)
            
            # 使用第一个可用模型
            model = models[0]
            client = ai_client_service.get_client(model)
            
            # 调用 AI 生成
            response = await client.chat(
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.7,
                max_tokens=2000
            )
            
            # 解析 AI 响应
            content = response["content"]
            
            # 尝试提取 JSON
            import json
            import re
            
            # 查找 JSON 数组
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                testcases_data = json.loads(json_match.group())
                
                # 补充字段
                testcases = []
                for i, tc in enumerate(testcases_data):
                    testcase = {
                        "name": tc.get("name", f"{request.module or '功能'}测试用例 {i+1}"),
                        "test_type": request.test_type,
                        "module": request.module or tc.get("module", "默认模块"),
                        "description": tc.get("description", ""),
                        "preconditions": tc.get("preconditions", ""),
                        "test_steps": tc.get("test_steps", ""),
                        "expected_result": tc.get("expected_result", ""),
                        "priority": tc.get("priority", "P2"),
                        "status": "draft",
                        "tags": f"{request.test_type},AI生成"
                    }
                    testcases.append(testcase)
                
                return testcases
            else:
                # 如果无法解析,返回模拟数据
                return self._generate_mock_testcases(request)
                
        except Exception as e:
            print(f"❌ AI生成测试用例失败: {e}")
            # 失败时返回模拟数据
            return self._generate_mock_testcases(request)
    
    def _generate_mock_testcases(self, request: TestCaseGenerateRequest) -> List[Dict[str, Any]]:
        """生成模拟测试用例(当AI不可用时)"""
        testcases = []
        
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
                "tags": f"{request.test_type},模拟生成"
            }
            testcases.append(testcase)
        
        return testcases
    
    async def get_token_usage_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        获取 Token 使用统计
        
        Args:
            user_id: 用户ID
            days: 统计天数
        
        Returns:
            统计数据
        """
        from datetime import datetime, timedelta
        
        # 计算起始日期
        start_date = datetime.now() - timedelta(days=days)
        
        # 查询用户的消息
        result = await self.db.execute(
            select(ChatMessage)
            .join(ChatSession)
            .where(
                and_(
                    ChatSession.user_id == user_id,
                    ChatMessage.created_at >= start_date,
                    ChatMessage.tokens.isnot(None)
                )
            )
        )
        messages = result.scalars().all()
        
        # 统计
        total_tokens = sum(msg.tokens for msg in messages if msg.tokens)
        total_messages = len(messages)
        
        # 按模型统计
        model_stats = {}
        for msg in messages:
            if msg.model:
                if msg.model not in model_stats:
                    model_stats[msg.model] = {"count": 0, "tokens": 0}
                model_stats[msg.model]["count"] += 1
                if msg.tokens:
                    model_stats[msg.model]["tokens"] += msg.tokens
        
        return {
            "total_tokens": total_tokens,
            "total_messages": total_messages,
            "period_days": days,
            "by_model": model_stats,
            "avg_tokens_per_message": total_tokens / total_messages if total_messages > 0 else 0
        }

