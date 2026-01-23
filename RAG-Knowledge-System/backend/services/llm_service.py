"""
LLM服务 - 支持多种大语言模型
"""
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

from core.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)


class LLMProvider(ABC):
    """LLM提供者抽象基类"""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本

        Args:
            prompt: 提示词
            **kwargs: 额外参数

        Returns:
            生成的文本
        """
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        对话生成

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Returns:
            生成的回复
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """模型名称"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM提供者"""

    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        初始化OpenAI提供者

        Args:
            model: 模型名称
            api_key: API密钥
            base_url: API基础URL
            temperature: 温度参数
            max_tokens: 最大token数
        """
        try:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(
                api_key=api_key or settings.OPENAI_API_KEY,
                base_url=base_url or settings.OPENAI_BASE_URL
            )
            self._model = model
            self._temperature = temperature
            self._max_tokens = max_tokens

            logger.info(f"OpenAI LLM初始化成功: {model}")

        except ImportError:
            logger.warning("openai库未安装，OpenAI LLM功能不可用")
            raise ImportError("请安装 openai: pip install openai")

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            response = await self.client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", self._temperature),
                max_tokens=kwargs.get("max_tokens", self._max_tokens)
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI生成失败: {str(e)}")
            raise

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话生成"""
        try:
            response = await self.client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=kwargs.get("temperature", self._temperature),
                max_tokens=kwargs.get("max_tokens", self._max_tokens)
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI对话失败: {str(e)}")
            raise

    @property
    def model_name(self) -> str:
        """模型名称"""
        return self._model


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM提供者"""

    def __init__(
        self,
        model: str = "claude-3-opus-20240229",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        初始化Anthropic提供者

        Args:
            model: 模型名称
            api_key: API密钥
            temperature: 温度参数
            max_tokens: 最大token数
        """
        try:
            import anthropic

            self.client = anthropic.AsyncAnthropic(
                api_key=api_key or settings.ANTHROPIC_API_KEY
            )
            self._model = model
            self._temperature = temperature
            self._max_tokens = max_tokens

            logger.info(f"Anthropic LLM初始化成功: {model}")

        except ImportError:
            logger.warning("anthropic库未安装，Anthropic LLM功能不可用")
            raise ImportError("请安装 anthropic: pip install anthropic")

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            response = await self.client.messages.create(
                model=self._model,
                max_tokens=kwargs.get("max_tokens", self._max_tokens),
                temperature=kwargs.get("temperature", self._temperature),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic生成失败: {str(e)}")
            raise

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话生成"""
        try:
            # 转换消息格式
            anthropic_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    anthropic_messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    anthropic_messages.append({"role": "assistant", "content": msg["content"]})
                elif msg["role"] == "system":
                    # Anthropic需要在messages之前添加system message
                    pass

            response = await self.client.messages.create(
                model=self._model,
                max_tokens=kwargs.get("max_tokens", self._max_tokens),
                temperature=kwargs.get("temperature", self._temperature),
                messages=anthropic_messages
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic对话失败: {str(e)}")
            raise

    @property
    def model_name(self) -> str:
        """模型名称"""
        return self._model


class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM提供者"""

    def __init__(
        self,
        model: str = "deepseek-chat",
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com/v1",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        初始化DeepSeek提供者

        Args:
            model: 模型名称
            api_key: API密钥
            base_url: API基础URL
            temperature: 温度参数
            max_tokens: 最大token数
        """
        try:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(
                api_key=api_key or settings.DEEPSEEK_API_KEY,
                base_url=base_url
            )
            self._model = model
            self._temperature = temperature
            self._max_tokens = max_tokens

            logger.info(f"DeepSeek LLM初始化成功: {model}")

        except ImportError:
            logger.warning("openai库未安装，DeepSeek LLM功能不可用")
            raise ImportError("请安装 openai: pip install openai")

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            response = await self.client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", self._temperature),
                max_tokens=kwargs.get("max_tokens", self._max_tokens)
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"DeepSeek生成失败: {str(e)}")
            raise

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话生成"""
        try:
            response = await self.client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=kwargs.get("temperature", self._temperature),
                max_tokens=kwargs.get("max_tokens", self._max_tokens)
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"DeepSeek对话失败: {str(e)}")
            raise

    @property
    def model_name(self) -> str:
        """模型名称"""
        return self._model


class LLMService:
    """LLM服务"""

    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        初始化LLM服务

        Args:
            provider: LLM提供者，如果为None则根据配置自动选择
        """
        if provider:
            self.provider = provider
        else:
            self.provider = self._create_provider_from_config()

        logger.info("LLM服务初始化完成")

    def _create_provider_from_config(self) -> LLMProvider:
        """根据配置创建LLM提供者"""
        provider_type = settings.LLM_PROVIDER.lower()

        if provider_type == "openai":
            return OpenAIProvider(
                model=settings.LLM_MODEL,
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
        elif provider_type == "anthropic":
            return AnthropicProvider(
                model=settings.LLM_MODEL,
                api_key=settings.ANTHROPIC_API_KEY,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
        elif provider_type == "deepseek":
            return DeepSeekProvider(
                model=settings.LLM_MODEL,
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
        else:
            logger.warning(f"未知的LLM提供者类型: {provider_type}，使用OpenAI")
            return OpenAIProvider(model=settings.LLM_MODEL)

    async def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本

        Args:
            prompt: 提示词
            **kwargs: 额外参数

        Returns:
            生成的文本
        """
        return await self.provider.generate(prompt, **kwargs)

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        对话生成

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Returns:
            生成的回复
        """
        return await self.provider.chat(messages, **kwargs)

    @property
    def model_name(self) -> str:
        """模型名称"""
        return self.provider.model_name
