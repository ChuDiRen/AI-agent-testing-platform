"""
DeepSeek模型客户端 - OpenAI兼容接口
"""
import os
import httpx
from typing import Optional, List
from loguru import logger


class DeepSeekClient:
    """
    DeepSeek API客户端（OpenAI兼容接口）
    
    使用方式:
        client = DeepSeekClient(api_key="your_key", base_url="https://api.deepseek.com/v1")
        response = await client.chat_completion(
            messages=[{"role": "user", "content": "Hello"}],
            model="deepseek-chat",
            temperature=0.7,
            max_tokens=2000
        )
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com/v1"
    ):
        """
        初始化DeepSeek客户端

        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )

    async def chat_completion(
        self,
        messages: List[dict],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> dict:
        """
        调用DeepSeek聊天API

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数（0-2）
            max_tokens: 最大生成token数
            stream: 是否流式响应

        Returns:
            API响应字典
        """
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }

            response = await self.client.post(
                "/chat/completions",
                json=payload
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"DeepSeek API HTTP错误: {e.response.status_code}")
            logger.error(f"响应内容: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {str(e)}")
            raise

    async def stream_chat_completion(
        self,
        messages: List[dict],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        流式调用DeepSeek聊天API

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数

        Yields:
            流式响应chunk
        """
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }

            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    line = line.strip()
                    if line.startswith("data: "):
                        data = line[6:]
                        yield data
                    elif line == "[DONE]":
                        break

        except Exception as e:
            logger.error(f"流式API调用失败: {str(e)}")
            raise

    async def close(self):
        """关闭客户端连接"""
        await self.client.aclose()
        logger.info("DeepSeek客户端已关闭")


# 全局客户端实例
_deepseek_client: Optional[DeepSeekClient] = None


def get_deepseek_client(api_key: str, base_url: str = "https://api.deepseek.com/v1") -> DeepSeekClient:
    """
    获取DeepSeek客户端实例（单例模式）

    Args:
        api_key: API密钥
        base_url: API基础URL

    Returns:
        DeepSeekClient实例
    """
    global _deepseek_client

    if _deepseek_client is None:
        _deepseek_client = DeepSeekClient(api_key, base_url)

    return _deepseek_client
