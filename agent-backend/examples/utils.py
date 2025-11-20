"""
自定义工具模块
提供对硅基流动(SiliconFlow)等平台的支持
"""
import os
import random
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

# 常见浏览器的 USER_AGENT 列表
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# 设置随机 USER_AGENT 环境变量，避免警告信息
if "USER_AGENT" not in os.environ:
    os.environ["USER_AGENT"] = random.choice(USER_AGENTS)


def init_chat_model(
    model: str,
    *,
    model_provider: str | None = None,
    **kwargs: Any,
) -> BaseChatModel:
    """
    初始化聊天模型，支持硅基流动(SiliconFlow)平台
    
    参数:
        model: 模型名称，格式可以是:
            - "siliconflow:模型名称" (例如: "siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")
            - "模型名称" (需要同时指定 model_provider)
        model_provider: 模型提供商，支持 "siliconflow"
        **kwargs: 其他参数传递给底层模型
        
    返回:
        BaseChatModel: 初始化好的聊天模型实例
        
    示例:
        >>> # 方式1: 使用前缀格式
        >>> model = init_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")
        
        >>> # 方式2: 分别指定
        >>> model = init_chat_model(
        ...     "deepseek-ai/DeepSeek-V3.2-Exp",
        ...     model_provider="siliconflow"
        ... )
    """
    # 解析模型提供商
    if ":" in model and not model_provider:
        parts = model.split(":", 1)
        if parts[0].lower() == "siliconflow":
            model_provider = "siliconflow"
            model = parts[1]
    
    # 处理硅基流动平台
    if model_provider and model_provider.lower() == "siliconflow":
        # 获取API密钥
        api_key = kwargs.pop("api_key", None) or os.environ.get("SILICONFLOW_API_KEY")
        if not api_key:
            raise ValueError(
                "SILICONFLOW_API_KEY 未设置。请设置环境变量或通过 api_key 参数传递。"
            )
        
        # 获取base_url，默认使用硅基流动的API地址
        base_url = kwargs.pop("base_url", None) or "https://api.siliconflow.cn/v1"
        
        # 使用 ChatOpenAI 作为底层实现（硅基流动兼容OpenAI API）
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )
    
    # 如果不是硅基流动，回退到原始的 langchain init_chat_model
    from langchain.chat_models import init_chat_model as langchain_init_chat_model
    return langchain_init_chat_model(model, model_provider=model_provider, **kwargs)
