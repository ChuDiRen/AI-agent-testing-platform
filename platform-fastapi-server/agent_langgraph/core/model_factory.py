"""
ModelFactory - 模型工厂

统一管理LLM模型实例的创建和配置
"""
import os
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from functools import lru_cache

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """模型配置"""
    provider: str = "siliconflow"
    model_name: str = "deepseek-ai/DeepSeek-V3"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.3
    timeout: float = 120.0
    max_retries: int = 3
    max_tokens: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """自动填充默认值"""
        if not self.api_key:
            self.api_key = self._get_default_api_key()
        if not self.base_url:
            self.base_url = self._get_default_base_url()
    
    def _get_default_api_key(self) -> str:
        """获取默认API Key"""
        return (
            os.getenv("SILICONFLOW_API_KEY") or 
            os.getenv("OPENAI_API_KEY") or 
            os.getenv("DEEPSEEK_API_KEY") or 
            ""
        )
    
    def _get_default_base_url(self) -> str:
        """获取默认Base URL"""
        provider_urls = {
            "siliconflow": "https://api.siliconflow.cn/v1",
            "openai": "https://api.openai.com/v1",
            "deepseek": "https://api.deepseek.com/v1",
            "zhipu": "https://open.bigmodel.cn/api/paas/v4",
            "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        }
        return os.getenv(
            f"{self.provider.upper()}_BASE_URL",
            provider_urls.get(self.provider, "https://api.siliconflow.cn/v1")
        )


class ModelFactory:
    """
    模型工厂
    
    提供统一的模型创建接口，支持缓存和配置管理
    """
    
    _instances: Dict[str, ChatOpenAI] = {}
    _default_config: Optional[ModelConfig] = None
    
    @classmethod
    def set_default_config(cls, config: ModelConfig):
        """设置默认配置"""
        cls._default_config = config
    
    @classmethod
    def get_model(
        cls,
        config: Optional[ModelConfig] = None,
        temperature: Optional[float] = None,
        use_cache: bool = True
    ) -> ChatOpenAI:
        """
        获取模型实例
        
        Args:
            config: 模型配置，为None时使用默认配置
            temperature: 覆盖配置中的temperature
            use_cache: 是否使用缓存
            
        Returns:
            ChatOpenAI实例
        """
        if config is None:
            config = cls._default_config or ModelConfig()
        
        if temperature is not None:
            config = ModelConfig(
                provider=config.provider,
                model_name=config.model_name,
                api_key=config.api_key,
                base_url=config.base_url,
                temperature=temperature,
                timeout=config.timeout,
                max_retries=config.max_retries,
                max_tokens=config.max_tokens,
                extra=config.extra,
            )
        
        cache_key = f"{config.provider}:{config.model_name}:{config.temperature}"
        
        if use_cache and cache_key in cls._instances:
            return cls._instances[cache_key]
        
        model = cls._create_model(config)
        
        if use_cache:
            cls._instances[cache_key] = model
        
        return model
    
    @classmethod
    def _create_model(cls, config: ModelConfig) -> ChatOpenAI:
        """创建模型实例"""
        kwargs = {
            "model": config.model_name,
            "api_key": config.api_key,
            "base_url": config.base_url,
            "temperature": config.temperature,
            "timeout": config.timeout,
            "max_retries": config.max_retries,
        }
        
        if config.max_tokens:
            kwargs["max_tokens"] = config.max_tokens
        
        kwargs.update(config.extra)
        
        logger.debug(f"Creating model: {config.model_name} @ {config.base_url}")
        return ChatOpenAI(**kwargs)
    
    @classmethod
    def clear_cache(cls):
        """清除模型缓存"""
        cls._instances.clear()
    
    @classmethod
    def get_default_model(cls, temperature: float = 0.3) -> ChatOpenAI:
        """获取默认模型（便捷方法）"""
        return cls.get_model(temperature=temperature)


# 便捷函数
def get_model(temperature: float = 0.3) -> ChatOpenAI:
    """获取默认模型实例"""
    return ModelFactory.get_default_model(temperature)
