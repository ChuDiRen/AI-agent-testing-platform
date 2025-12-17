"""
ModelService - 模型服务

支持国产大模型：DeepSeek、通义千问、智谱AI、Kimi、SiliconFlow
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

# 国产模型提供商配置
PROVIDER_CONFIGS: Dict[str, Dict[str, Any]] = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "display_name": "DeepSeek",
        "models": ["deepseek-chat", "deepseek-coder"],
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "deepseek-ai/DeepSeek-V3",
        "display_name": "SiliconFlow",
        "models": [
            "deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-R1",
            "Qwen/Qwen2.5-72B-Instruct",
        ],
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
        "display_name": "通义千问",
        "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
    },
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4",
        "display_name": "智谱AI",
        "models": ["glm-4", "glm-4-flash", "glm-4-air"],
    },
    "moonshot": {
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "moonshot-v1-8k",
        "display_name": "Kimi",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "display_name": "OpenAI",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
    },
}


class ModelService:
    """模型服务类"""

    @staticmethod
    def get_provider_config(provider: str) -> Dict[str, Any]:
        """获取提供商配置"""
        return PROVIDER_CONFIGS.get(provider.lower(), {})

    @staticmethod
    def get_base_url(provider: str) -> Optional[str]:
        """获取提供商的API基础URL"""
        config = PROVIDER_CONFIGS.get(provider.lower(), {})
        return config.get("base_url")

    @staticmethod
    def get_default_model(provider: str) -> Optional[str]:
        """获取提供商的默认模型"""
        config = PROVIDER_CONFIGS.get(provider.lower(), {})
        return config.get("default_model")

    @staticmethod
    def create_chat_model(
        provider: str,
        model_code: str,
        api_key: str,
        temperature: float = 0.7,
        timeout: float = 120.0,
        max_retries: int = 3,
        **kwargs,
    ) -> ChatOpenAI:
        """创建LangChain ChatOpenAI实例，支持国产模型"""
        config = PROVIDER_CONFIGS.get(provider.lower(), {})
        base_url = config.get("base_url") or kwargs.get("base_url")

        return ChatOpenAI(
            model=model_code,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs,
        )

    @staticmethod
    async def test_connection(
        provider: str,
        api_key: str,
        model_code: Optional[str] = None,
        timeout: float = 5.0,
    ) -> Dict[str, Any]:
        """测试模型连接，5秒超时"""
        config = PROVIDER_CONFIGS.get(provider.lower(), {})
        base_url = config.get("base_url")
        model = model_code or config.get("default_model")

        if not base_url or not model:
            return {"success": False, "error": f"Unknown provider: {provider}"}

        try:
            chat_model = ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
                max_retries=1,
            )
            response = await asyncio.wait_for(
                chat_model.ainvoke([{"role": "user", "content": "Hi"}]),
                timeout=timeout,
            )
            return {"success": True, "model": model, "response_length": len(response.content)}
        except asyncio.TimeoutError:
            return {"success": False, "error": "Connection timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def list_providers() -> list:
        """列出所有支持的提供商"""
        return [
            {
                "code": code,
                "name": config["display_name"],
                "base_url": config["base_url"],
                "models": config["models"],
            }
            for code, config in PROVIDER_CONFIGS.items()
        ]
