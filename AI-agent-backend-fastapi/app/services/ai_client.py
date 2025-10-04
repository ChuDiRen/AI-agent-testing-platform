# Copyright (c) 2025 左岚. All rights reserved.
"""AI客户端统一封装"""
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Dict, Any, List
import asyncio
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.models.ai_chat import AIModel


class BaseAIClient(ABC):
    """AI客户端基类"""
    
    def __init__(self, model: AIModel):
        self.model = model
        self.client = None
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None] | Dict[str, Any]:
        """聊天接口"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """测试连接"""
        pass


class OpenAIClient(BaseAIClient):
    """OpenAI客户端"""
    
    def __init__(self, model: AIModel):
        super().__init__(model)
        self.client = AsyncOpenAI(
            api_key=model.api_key,
            base_url=model.api_base if model.api_base else None
        )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None] | Dict[str, Any]:
        """OpenAI聊天"""
        params = {
            "model": self.model.model_key,
            "messages": messages,
            "temperature": temperature or float(self.model.temperature),
            "max_tokens": max_tokens or self.model.max_tokens,
            "stream": stream
        }
        
        if stream:
            return self._stream_chat(params)
        else:
            return await self._complete_chat(params)
    
    async def _stream_chat(self, params: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """流式聊天"""
        stream = await self.client.chat.completions.create(**params)
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _complete_chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """完整聊天"""
        response = await self.client.chat.completions.create(**params)
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试OpenAI连接"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model.model_key,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return {
                "success": True,
                "model": response.model,
                "message": "连接成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "连接失败"
            }


class ClaudeClient(BaseAIClient):
    """Claude客户端"""
    
    def __init__(self, model: AIModel):
        super().__init__(model)
        self.client = AsyncAnthropic(
            api_key=model.api_key,
            base_url=model.api_base if model.api_base else None
        )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None] | Dict[str, Any]:
        """Claude聊天"""
        # Claude需要分离system消息
        system_message = ""
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                chat_messages.append(msg)
        
        params = {
            "model": self.model.model_key,
            "messages": chat_messages,
            "temperature": temperature or float(self.model.temperature),
            "max_tokens": max_tokens or self.model.max_tokens,
            "stream": stream
        }
        
        if system_message:
            params["system"] = system_message
        
        if stream:
            return self._stream_chat(params)
        else:
            return await self._complete_chat(params)
    
    async def _stream_chat(self, params: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """流式聊天"""
        async with self.client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                yield text
    
    async def _complete_chat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """完整聊天"""
        response = await self.client.messages.create(**params)
        return {
            "content": response.content[0].text,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试Claude连接"""
        try:
            response = await self.client.messages.create(
                model=self.model.model_key,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return {
                "success": True,
                "model": response.model,
                "message": "连接成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "连接失败"
            }


class AIClientFactory:
    """AI客户端工厂"""
    
    @staticmethod
    def create_client(model: AIModel) -> BaseAIClient:
        """创建AI客户端"""
        provider = model.provider.lower()
        
        if provider == "openai":
            return OpenAIClient(model)
        elif provider == "claude" or provider == "anthropic":
            return ClaudeClient(model)
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")


class AIClientService:
    """AI客户端服务"""
    
    def __init__(self):
        self._clients: Dict[int, BaseAIClient] = {}  # 客户端缓存
    
    def get_client(self, model: AIModel) -> BaseAIClient:
        """获取AI客户端"""
        if model.model_id not in self._clients:
            self._clients[model.model_id] = AIClientFactory.create_client(model)
        return self._clients[model.model_id]
    
    def clear_client(self, model_id: int):
        """清除客户端缓存"""
        if model_id in self._clients:
            del self._clients[model_id]
    
    def clear_all_clients(self):
        """清除所有客户端缓存"""
        self._clients.clear()


# 全局AI客户端服务实例
ai_client_service = AIClientService()

