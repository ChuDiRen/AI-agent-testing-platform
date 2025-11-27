"""
配置管理模块

支持动态模型切换和系统配置
"""

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Dict, Optional

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI


@dataclass
class LLMConfig:
    """LLM配置类
    
    支持多种模型提供商的动态切换
    """
    # 模型提供商: siliconflow, openai, anthropic
    provider: str = "siliconflow"
    
    # 模型名称
    model_name: str = "deepseek-ai/DeepSeek-V3"
    
    # API配置
    api_url: str = "https://api.siliconflow.cn/v1"
    api_key: Optional[str] = None
    
    # 模型参数
    temperature: float = 0.0
    max_tokens: int = 4096
    streaming: bool = True
    
    # 超时配置
    timeout: int = 60
    max_retries: int = 3
    
    def get_api_key(self) -> str:
        """获取API密钥，优先使用配置值，否则从环境变量读取"""
        if self.api_key:
            return self.api_key
        
        env_key_map = {
            "siliconflow": "SILICONFLOW_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY"
        }
        
        env_key = env_key_map.get(self.provider.lower(), "SILICONFLOW_API_KEY")
        return os.getenv(env_key, "")


@dataclass
class DatabaseConfig:
    """数据库配置类"""
    db_type: str = "sqlite"  # mysql, postgresql, sqlite, oracle, etc.
    host: str = "localhost"
    port: int = 3306
    database: str = ""
    username: str = ""
    password: str = ""
    
    # 连接池配置
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # 查询配置
    query_timeout: int = 30
    default_limit: int = 100
    max_limit: int = 1000


@dataclass
class MemoryConfig:
    """记忆系统配置"""
    # 数据库路径
    db_path: str = "data/agent_memory.db"
    
    # 短期记忆配置
    max_messages: int = 20
    max_tokens: int = 8000
    
    # 长期记忆配置
    enable_semantic_search: bool = True
    embedding_model: str = "text-embedding-ada-002"


@dataclass  
class ConcurrencyConfig:
    """并发控制配置"""
    # 最大并发请求数
    max_concurrent_requests: int = 100
    
    # 限流配置 (每分钟请求数)
    rate_limit_per_minute: int = 60
    
    # 请求队列大小
    queue_size: int = 1000
    
    # Worker数量
    num_workers: int = 10


@dataclass
class SystemConfig:
    """系统总配置"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    concurrency: ConcurrencyConfig = field(default_factory=ConcurrencyConfig)
    
    # 项目路径
    project_root: str = ""
    prompts_dir: str = "prompts"
    
    # 调试模式
    debug: bool = False


# 全局配置实例
_config: Optional[SystemConfig] = None


def get_config() -> SystemConfig:
    """获取全局配置"""
    global _config
    if _config is None:
        _config = SystemConfig()
    return _config


def set_config(config: SystemConfig) -> None:
    """设置全局配置"""
    global _config
    _config = config


def get_model(config: Optional[LLMConfig] = None) -> BaseChatModel:
    """获取LLM模型实例
    
    Args:
        config: LLM配置，如果为None则使用全局配置
        
    Returns:
        初始化好的聊天模型实例
    """
    if config is None:
        config = get_config().llm
    
    api_key = config.get_api_key()
    if not api_key:
        raise ValueError(
            f"API key not found for provider '{config.provider}'. "
            f"Please set the appropriate environment variable."
        )
    
    # 硅基流动使用OpenAI兼容接口
    if config.provider.lower() == "siliconflow":
        return ChatOpenAI(
            model=config.model_name,
            api_key=api_key,
            base_url=config.api_url,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            streaming=config.streaming,
            timeout=config.timeout,
            max_retries=config.max_retries
        )
    
    # 其他提供商使用langchain的init_chat_model
    model_str = f"{config.provider}:{config.model_name}"
    return init_chat_model(
        model_str,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        streaming=config.streaming
    )


# 预定义的模型配置
PRESET_MODELS: Dict[str, LLMConfig] = {
    "deepseek-v3": LLMConfig(
        provider="siliconflow",
        model_name="deepseek-ai/DeepSeek-V3",
        api_url="https://api.siliconflow.cn/v1"
    ),
    "deepseek-v3-exp": LLMConfig(
        provider="siliconflow", 
        model_name="deepseek-ai/DeepSeek-V3.2-Exp",
        api_url="https://api.siliconflow.cn/v1"
    ),
    "gpt-4o": LLMConfig(
        provider="openai",
        model_name="gpt-4o",
        api_url="https://api.openai.com/v1"
    ),
    "claude-3-5-sonnet": LLMConfig(
        provider="anthropic",
        model_name="claude-3-5-sonnet-latest",
        api_url="https://api.anthropic.com"
    )
}


def get_preset_model(name: str) -> BaseChatModel:
    """获取预定义的模型
    
    Args:
        name: 模型名称 (deepseek-v3, gpt-4o, claude-3-5-sonnet等)
        
    Returns:
        初始化好的聊天模型实例
    """
    if name not in PRESET_MODELS:
        raise ValueError(f"Unknown preset model: {name}. Available: {list(PRESET_MODELS.keys())}")
    
    return get_model(PRESET_MODELS[name])
