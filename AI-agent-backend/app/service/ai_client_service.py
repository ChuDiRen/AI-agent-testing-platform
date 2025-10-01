"""
AI客户端服务
提供统一的AI模型调用接口，支持多种AI提供商
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, AsyncGenerator, Union
from dataclasses import dataclass
from enum import Enum

import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.core.config import settings
from app.core.logger import get_logger
from app.entity.ai_model import AIModel
from app.utils.exceptions import BusinessException

logger = get_logger(__name__)


class MessageRole(str, Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    """聊天消息"""
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatRequest:
    """聊天请求"""
    messages: List[ChatMessage]
    large_model_id: int
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False
    user_id: Optional[int] = None


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    large_model_id: int
    tokens_used: int
    cost: float
    response_time: float
    metadata: Dict[str, Any]


class BaseAIClient(ABC):
    """AI客户端基类"""
    
    def __init__(self, model: AIModel):
        self.model = model
        self.provider = model.provider
        self.api_key = model.api_key
        self.api_endpoint = model.api_endpoint
        self.config = model.config or {}
    
    @abstractmethod
    async def chat(self, request: ChatRequest) -> Union[ChatResponse, AsyncGenerator[str, None]]:
        """聊天接口"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """测试连接"""
        pass
    
    def calculate_cost(self, tokens_used: int) -> float:
        """计算费用"""
        pricing = self.model.pricing or {}
        input_cost = pricing.get('input_cost_per_token', 0.0)
        output_cost = pricing.get('output_cost_per_token', 0.0)
        
        # 简化计算，实际应该区分输入输出token
        return tokens_used * (input_cost + output_cost) / 2


class OpenAIClient(BaseAIClient):
    """OpenAI客户端"""
    
    def __init__(self, model: AIModel):
        super().__init__(model)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.api_endpoint or "https://api.openai.com/v1"
        )
    
    async def chat(self, request: ChatRequest) -> Union[ChatResponse, AsyncGenerator[str, None]]:
        """OpenAI聊天接口"""
        try:
            start_time = time.time()
            
            # 转换消息格式
            messages = [
                {"role": msg.role.value, "content": msg.content}
                for msg in request.messages
            ]
            
            # 设置参数
            params = {
                "model": self.model.name,
                "messages": messages,
                "temperature": request.temperature or self.model.temperature,
                "max_tokens": request.max_tokens or self.model.max_tokens,
                "stream": request.stream
            }
            
            if request.stream:
                return self._stream_chat(params, start_time)
            else:
                return await self._complete_chat(params, start_time)
                
        except Exception as e:
            logger.error(f"OpenAI chat error: {str(e)}")
            raise BusinessException(f"OpenAI调用失败: {str(e)}")
    
    async def _complete_chat(self, params: Dict[str, Any], start_time: float) -> ChatResponse:
        """完整聊天响应"""
        response = await self.client.chat.completions.create(**params)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        cost = self.calculate_cost(tokens_used)
        
        return ChatResponse(
            content=content,
            model_id=self.model.id,
            tokens_used=tokens_used,
            cost=cost,
            response_time=response_time,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "model": response.model,
                "usage": response.usage.model_dump()
            }
        )
    
    async def _stream_chat(self, params: Dict[str, Any], start_time: float) -> AsyncGenerator[str, None]:
        """流式聊天响应"""
        async for chunk in await self.client.chat.completions.create(**params):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试OpenAI连接"""
        try:
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=self.model.name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            end_time = time.time()
            
            return {
                "success": True,
                "response_time": end_time - start_time,
                "model": response.model,
                "message": "连接成功"
            }
            
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "连接失败"
            }


class AnthropicClient(BaseAIClient):
    """Anthropic客户端"""
    
    def __init__(self, model: AIModel):
        super().__init__(model)
        self.client = AsyncAnthropic(
            api_key=self.api_key,
            base_url=self.api_endpoint or "https://api.anthropic.com"
        )
    
    async def chat(self, request: ChatRequest) -> Union[ChatResponse, AsyncGenerator[str, None]]:
        """Anthropic聊天接口"""
        try:
            start_time = time.time()
            
            # 转换消息格式 - Anthropic需要分离system消息
            system_message = ""
            messages = []
            
            for msg in request.messages:
                if msg.role == MessageRole.SYSTEM:
                    system_message = msg.content
                else:
                    messages.append({
                        "role": msg.role.value,
                        "content": msg.content
                    })
            
            # 设置参数
            params = {
                "model": self.model.name,
                "messages": messages,
                "temperature": request.temperature or self.model.temperature,
                "max_tokens": request.max_tokens or self.model.max_tokens,
                "stream": request.stream
            }
            
            if system_message:
                params["system"] = system_message
            
            if request.stream:
                return self._stream_chat(params, start_time)
            else:
                return await self._complete_chat(params, start_time)
                
        except Exception as e:
            logger.error(f"Anthropic chat error: {str(e)}")
            raise BusinessException(f"Anthropic调用失败: {str(e)}")
    
    async def _complete_chat(self, params: Dict[str, Any], start_time: float) -> ChatResponse:
        """完整聊天响应"""
        response = await self.client.messages.create(**params)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        content = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        cost = self.calculate_cost(tokens_used)
        
        return ChatResponse(
            content=content,
            model_id=self.model.id,
            tokens_used=tokens_used,
            cost=cost,
            response_time=response_time,
            metadata={
                "stop_reason": response.stop_reason,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
        )
    
    async def _stream_chat(self, params: Dict[str, Any], start_time: float) -> AsyncGenerator[str, None]:
        """流式聊天响应"""
        async with self.client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                yield text
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试Anthropic连接"""
        try:
            start_time = time.time()
            
            response = await self.client.messages.create(
                model=self.model.name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            end_time = time.time()
            
            return {
                "success": True,
                "response_time": end_time - start_time,
                "model": response.model,
                "message": "连接成功"
            }
            
        except Exception as e:
            logger.error(f"Anthropic connection test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "连接失败"
            }


class AIClientFactory:
    """AI客户端工厂"""

    @staticmethod
    def create_client(model: AIModel) -> BaseAIClient:
        """根据模型创建对应的AI客户端"""
        provider = model.provider.lower()

        if provider == "openai":
            return OpenAIClient(model)
        elif provider == "anthropic":
            return AnthropicClient(model)
        elif provider in ["custom", "deepseek", "qianwen", "baidu", "google"]:
            return CustomAPIClient(model)
        else:
            raise BusinessException(f"不支持的AI提供商: {provider}")


class AIClientService:
    """AI客户端服务"""

    def __init__(self):
        self._clients: Dict[int, BaseAIClient] = {}

    def get_client(self, model: AIModel) -> BaseAIClient:
        """获取AI客户端"""
        if model.id not in self._clients:
            self._clients[model.id] = AIClientFactory.create_client(model)
        return self._clients[model.id]

    def clear_client(self, model_id: int):
        """清除客户端缓存"""
        if model_id in self._clients:
            del self._clients[model_id]

    def clear_all_clients(self):
        """清除所有客户端缓存"""
        self._clients.clear()

    async def chat(self, model: AIModel, request: ChatRequest) -> Union[ChatResponse, AsyncGenerator[str, None]]:
        """聊天接口"""
        client = self.get_client(model)
        return await client.chat(request)

    async def test_connection(self, model: AIModel) -> Dict[str, Any]:
        """测试连接"""
        client = self.get_client(model)
        return await client.test_connection()


# 全局AI客户端服务实例
ai_client_service = AIClientService()


class CustomAPIClient(BaseAIClient):
    """自定义API客户端"""
    
    async def chat(self, request: ChatRequest) -> Union[ChatResponse, AsyncGenerator[str, None]]:
        """自定义API聊天接口"""
        try:
            start_time = time.time()
            
            # 构建请求数据
            data = {
                "model": self.model.name,
                "messages": [
                    {"role": msg.role.value, "content": msg.content}
                    for msg in request.messages
                ],
                "temperature": request.temperature or self.model.temperature,
                "max_tokens": request.max_tokens or self.model.max_tokens,
                "stream": request.stream
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_endpoint}/chat/completions",
                    json=data,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                
                end_time = time.time()
                response_time = end_time - start_time
                
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                cost = self.calculate_cost(tokens_used)
                
                return ChatResponse(
                    content=content,
                    model_id=self.model.id,
                    tokens_used=tokens_used,
                    cost=cost,
                    response_time=response_time,
                    metadata=result.get("usage", {})
                )
                
        except Exception as e:
            logger.error(f"Custom API chat error: {str(e)}")
            raise BusinessException(f"自定义API调用失败: {str(e)}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试自定义API连接"""
        try:
            start_time = time.time()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model.name,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_endpoint}/chat/completions",
                    json=data,
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                end_time = time.time()
                
                return {
                    "success": True,
                    "response_time": end_time - start_time,
                    "message": "连接成功"
                }
                
        except Exception as e:
            logger.error(f"Custom API connection test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "连接失败"
            }
