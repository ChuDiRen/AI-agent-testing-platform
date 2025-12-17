import json
import logging
from typing import AsyncGenerator, List, Dict

import httpx

logger = logging.getLogger(__name__)


class AiStreamService:
    """AI流式调用服务 - 支持多个AI模型提供商的流式API调用"""
    
    @staticmethod
    async def call_ai_stream(
        model_code: str,
        api_key: str,
        api_url: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """
        流式调用AI模型
        
        Args:
            model_code: 模型代码(deepseek-chat、qwen-max等)
            api_key: API密钥
            api_url: API地址
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Yields:
            每个生成的内容块
        """
        if "deepseek" in model_code.lower():
            async for chunk in AiStreamService._call_deepseek_stream(
                api_key, messages, temperature, max_tokens
            ):
                yield chunk
        elif "qwen" in model_code.lower():
            async for chunk in AiStreamService._call_qwen_stream(
                api_key, api_url, messages, temperature, max_tokens
            ):
                yield chunk
        else:
            # 通用调用方式
            async for chunk in AiStreamService._call_generic_stream(
                api_url, api_key, messages, temperature, max_tokens
            ):
                yield chunk
    
    @staticmethod
    async def _call_deepseek_stream(
        api_key: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """DeepSeek流式调用"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                # ✅ P2修复: 降低日志级别,解析错误不是严重问题
                                logger.debug(f"Failed to parse JSON chunk: {data[:100]}")
                                continue
        # ✅ P2修复: 分层异常处理
        except httpx.TimeoutException as e:
            logger.error(f"DeepSeek API timeout: {str(e)}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"DeepSeek HTTP error: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.critical(f"DeepSeek unexpected error: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    async def _call_qwen_stream(
        api_key: str,
        api_url: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """阿里云通义千问流式调用"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    api_url or "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "qwen-max",
                        "input": {"messages": messages},
                        "parameters": {
                            "temperature": temperature,
                            "max_tokens": max_tokens
                        },
                        "incremental_output": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            data = line[5:]
                            if data.strip():
                                try:
                                    chunk = json.loads(data)
                                    content = chunk.get("output", {}).get("text", "")
                                    if content:
                                        yield content
                                except json.JSONDecodeError:
                                    # ✅ P2修复: 降低日志级别
                                    logger.debug(f"Failed to parse JSON chunk: {data[:100]}")
                                    continue
        # ✅ P2修复: 分层异常处理
        except httpx.TimeoutException as e:
            logger.error(f"Qwen API timeout: {str(e)}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"Qwen HTTP error: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.critical(f"Qwen unexpected error: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    async def _call_generic_stream(
        api_url: str,
        api_key: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """通用流式调用方式(兼容OpenAI风格API)"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    api_url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                # ✅ P2修复: 降低日志级别
                                logger.debug(f"Failed to parse JSON chunk: {data[:100]}")
                                continue
        # ✅ P2修复: 分层异常处理
        except httpx.TimeoutException as e:
            logger.error(f"Generic API timeout: {str(e)}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"Generic HTTP error: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.critical(f"Generic unexpected error: {str(e)}", exc_info=True)
            raise

