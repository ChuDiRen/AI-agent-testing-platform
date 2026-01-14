"""
工厂模式工具模块

提供:
1. 模型工厂 - 支持国产大模型（硅基流动、智谱、通义千问、DeepSeek、月之暗面）
2. MCP 工厂 - 支持动态加载 MCP 服务器
"""
import asyncio
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI


# ============== 模型工厂 ==============

@dataclass
class ModelProviderConfig:
    """模型提供商配置"""
    name: str
    base_url: str
    api_key_env: str
    default_model: Optional[str] = None
    api_key: Optional[str] = None
    model_class: Type[BaseChatModel] = field(default=ChatOpenAI)
    extra_kwargs: Dict[str, Any] = field(default_factory=dict)


class ModelFactory:
    """模型工厂 - 统一管理大模型的创建
    
    使用示例:
        model = load_chat_model("siliconflow:deepseek-ai/DeepSeek-V3")
        model = load_chat_model("zhipu:glm-4-flash")
        model = load_chat_model("deepseek:deepseek-chat")
        model = load_chat_model("qwen:qwen-plus")
        model = load_chat_model("moonshot:moonshot-v1-128k")
        
        # 注册自定义提供商
        register_model_provider(
            "my-vllm",
            base_url="http://localhost:8000/v1",
            api_key="dummy"
        )
        model = load_chat_model("my-vllm:qwen2.5-7b")
    """
    
    # 内置提供商配置
    BUILTIN_PROVIDERS: Dict[str, ModelProviderConfig] = {
        "siliconflow": ModelProviderConfig(
            name="SiliconFlow",
            base_url="https://api.siliconflow.cn/v1",
            api_key="sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem",
            api_key_env="SILICONFLOW_API_KEY",
            default_model="deepseek-ai/DeepSeek-V3",
        ),
        "zhipu": ModelProviderConfig(
            name="Zhipu AI",
            base_url="https://open.bigmodel.cn/api/paas/v4",
            api_key_env="ZHIPU_API_KEY",
            default_model="glm-4-flash",
        ),
        "qwen": ModelProviderConfig(
            name="Qwen",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key_env="DASHSCOPE_API_KEY",
            default_model="qwen-plus",
        ),
        "deepseek": ModelProviderConfig(
            name="DeepSeek",
            base_url="https://api.deepseek.com/v1",
            api_key_env="DEEPSEEK_API_KEY",
            default_model="deepseek-chat",
        ),
        "moonshot": ModelProviderConfig(
            name="Moonshot",
            base_url="https://api.moonshot.cn/v1",
            api_key_env="MOONSHOT_API_KEY",
            default_model="moonshot-v1-128k",
        ),
    }
    
    def __init__(self):
        self._providers: Dict[str, ModelProviderConfig] = {}
        self._custom_factories: Dict[str, Callable[..., BaseChatModel]] = {}
        for name, config in self.BUILTIN_PROVIDERS.items():
            self._providers[name] = config
    
    def register(
        self,
        name: str,
        *,
        base_url: str,
        api_key: Optional[str] = None,
        api_key_env: Optional[str] = None,
        default_model: Optional[str] = None,
        **extra_kwargs: Any,
    ) -> None:
        """注册新的模型提供商"""
        self._providers[name.lower()] = ModelProviderConfig(
            name=name,
            base_url=base_url,
            api_key=api_key,
            api_key_env=api_key_env or f"{name.upper()}_API_KEY",
            default_model=default_model,
            extra_kwargs=extra_kwargs,
        )
    
    def register_factory(self, name: str, factory: Callable[..., BaseChatModel]) -> None:
        """注册自定义模型工厂函数"""
        self._custom_factories[name.lower()] = factory
    
    def create(
        self,
        model: str,
        *,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ) -> BaseChatModel:
        """创建模型实例
        
        Args:
            model: 模型标识，格式为 "provider:model_name"
            provider: 提供商名称（可选）
            api_key: API Key（覆盖默认配置）
            base_url: API URL（覆盖默认配置）
            **kwargs: 额外参数
        """
        # 解析 provider:model 格式
        if ":" in model and not provider:
            provider, model = model.split(":", 1)
        
        provider = (provider or "").lower()
        
        # 检查自定义工厂
        if provider in self._custom_factories:
            return self._custom_factories[provider](model, **kwargs)
        
        # 检查已注册的提供商
        if provider not in self._providers:
            raise ValueError(f"未知提供商: {provider}, 可用: {list(self._providers.keys())}")
        
        config = self._providers[provider]
        
        # 获取 API Key
        final_api_key = api_key or config.api_key or os.environ.get(config.api_key_env)
        if not final_api_key:
            raise ValueError(f"{config.name} API Key 未设置，请设置 {config.api_key_env}")
        
        # 创建模型
        return config.model_class(
            model=model or config.default_model,
            api_key=final_api_key,
            base_url=base_url or config.base_url,
            **{**config.extra_kwargs, **kwargs},
        )
    
    def list_providers(self) -> List[str]:
        """列出所有提供商"""
        return list(self._providers.keys())


# 全局模型工厂
_model_factory: Optional[ModelFactory] = None


def get_model_factory() -> ModelFactory:
    """获取模型工厂实例"""
    global _model_factory
    if _model_factory is None:
        _model_factory = ModelFactory()
    return _model_factory


def register_model_provider(
    name: str,
    *,
    base_url: str,
    api_key: Optional[str] = None,
    api_key_env: Optional[str] = None,
    default_model: Optional[str] = None,
    **extra_kwargs: Any,
) -> None:
    """注册模型提供商"""
    get_model_factory().register(
        name,
        base_url=base_url,
        api_key=api_key,
        api_key_env=api_key_env,
        default_model=default_model,
        **extra_kwargs,
    )


def load_chat_model(
    model: str,
    *,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs: Any,
) -> BaseChatModel:
    """加载聊天模型

    支持的提供商:
        - siliconflow: 硅基流动 (SILICONFLOW_API_KEY) - 默认
        - zhipu: 智谱AI (ZHIPU_API_KEY)
        - qwen: 通义千问 (DASHSCOPE_API_KEY)
        - deepseek: DeepSeek (DEEPSEEK_API_KEY)
        - moonshot: 月之暗面 (MOONSHOT_API_KEY)

    示例:
        # 不指定提供商时，默认使用硅基流动
        model = load_chat_model("deepseek-ai/DeepSeek-V3")

        # 指定提供商
        model = load_chat_model("siliconflow:deepseek-ai/DeepSeek-V3")
        model = load_chat_model("zhipu:glm-4-flash")
        model = load_chat_model("deepseek:deepseek-chat")
        model = load_chat_model("qwen:qwen-plus")
        model = load_chat_model("moonshot:moonshot-v1-128k")
    """
    # 如果 model 不包含提供商前缀，默认使用 siliconflow
    if ":" not in model and provider is None:
        model = f"siliconflow:{model}"

    return get_model_factory().create(
        model, provider=provider, api_key=api_key, base_url=base_url, **kwargs
    )


# ============== MCP 工厂 ==============

@dataclass
class MCPServerConfig:
    """MCP 服务器配置"""
    command: str
    args: List[str]
    transport: str = "stdio"
    env: Dict[str, str] = field(default_factory=dict)


class MCPFactory:
    """MCP 工厂 - 统一管理 MCP 服务器的加载
    
    使用示例:
        # 加载预定义服务器
        tools = await load_mcp_tools("chart")
        
        # 注册自定义服务器
        register_mcp_server(
            "my-server",
            command="npx",
            args=["-y", "@some/mcp-server"]
        )
        tools = await load_mcp_tools("my-server")
    """
    
    # 内置 MCP 服务器配置
    BUILTIN_SERVERS: Dict[str, MCPServerConfig] = {
        "chart": MCPServerConfig(
            command="npx",
            args=["-y", "@antv/mcp-server-chart"],
        ),
        "filesystem": MCPServerConfig(
            command="npx",
            args=["-y", "@anthropic/mcp-server-filesystem"],
        ),
        "github": MCPServerConfig(
            command="npx",
            args=["-y", "@anthropic/mcp-server-github"],
            env={"GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", "")},
        ),
        "playwright": MCPServerConfig(
            command="npx",
            args=["-y", "@anthropic/mcp-server-playwright"],
        ),
    }
    
    def __init__(self):
        self._servers: Dict[str, MCPServerConfig] = {}
        self._clients: Dict[str, Any] = {}
        self._tools: Dict[str, Dict[str, BaseTool]] = {}
        self._lock = asyncio.Lock()
        for name, config in self.BUILTIN_SERVERS.items():
            self._servers[name] = config
    
    def register(
        self,
        name: str,
        *,
        command: str,
        args: List[str],
        transport: str = "stdio",
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        """注册 MCP 服务器"""
        self._servers[name.lower()] = MCPServerConfig(
            command=command,
            args=args,
            transport=transport,
            env=env or {},
        )
    
    async def load(self, name: str) -> List[BaseTool]:
        """加载 MCP 服务器工具"""
        name = name.lower()
        
        async with self._lock:
            if name in self._tools:
                return list(self._tools[name].values())
            
            if name not in self._servers:
                raise ValueError(f"未知服务器: {name}, 可用: {list(self._servers.keys())}")
            
            config = self._servers[name]
            mcp_config = {
                f"mcp-{name}": {
                    "command": config.command,
                    "args": config.args,
                    "transport": config.transport,
                    **({"env": config.env} if config.env else {}),
                }
            }
            
            try:
                from langchain_mcp_adapters.client import MultiServerMCPClient
                
                print(f"[MCP] 正在初始化: {name}...")
                client = MultiServerMCPClient(mcp_config)
                tools = await client.get_tools()
                
                self._clients[name] = client
                self._tools[name] = {t.name: t for t in tools}
                print(f"[MCP] {name} 已加载 {len(tools)} 个工具")
                
                return tools
            except Exception as e:
                print(f"[MCP] {name} 初始化失败: {e}")
                self._tools[name] = {}
                return []
    
    async def load_custom(self, config: Dict[str, Dict[str, Any]], cache_key: str) -> List[BaseTool]:
        """加载自定义 MCP 配置"""
        async with self._lock:
            if cache_key in self._tools:
                return list(self._tools[cache_key].values())
            
            try:
                from langchain_mcp_adapters.client import MultiServerMCPClient
                
                print(f"[MCP] 正在初始化: {cache_key}...")
                client = MultiServerMCPClient(config)
                tools = await client.get_tools()
                
                self._clients[cache_key] = client
                self._tools[cache_key] = {t.name: t for t in tools}
                print(f"[MCP] {cache_key} 已加载 {len(tools)} 个工具")
                
                return tools
            except Exception as e:
                print(f"[MCP] {cache_key} 初始化失败: {e}")
                self._tools[cache_key] = {}
                return []
    
    def get_tools(self, name: str) -> Dict[str, BaseTool]:
        """获取已加载的工具"""
        return self._tools.get(name.lower(), {})
    
    def get_all_tools(self) -> List[BaseTool]:
        """获取所有已加载的工具"""
        return [t for tools in self._tools.values() for t in tools.values()]
    
    def list_servers(self) -> List[str]:
        """列出所有服务器"""
        return list(self._servers.keys())
    
    def reset(self, name: Optional[str] = None) -> None:
        """重置缓存"""
        if name:
            self._clients.pop(name.lower(), None)
            self._tools.pop(name.lower(), None)
        else:
            self._clients.clear()
            self._tools.clear()


# 全局 MCP 工厂
_mcp_factory: Optional[MCPFactory] = None


def get_mcp_factory() -> MCPFactory:
    """获取 MCP 工厂实例"""
    global _mcp_factory
    if _mcp_factory is None:
        _mcp_factory = MCPFactory()
    return _mcp_factory


def register_mcp_server(
    name: str,
    *,
    command: str,
    args: List[str],
    transport: str = "stdio",
    env: Optional[Dict[str, str]] = None,
) -> None:
    """注册 MCP 服务器"""
    get_mcp_factory().register(
        name, command=command, args=args, transport=transport, env=env
    )


async def load_mcp_tools(
    name: Optional[str] = None,
    config: Optional[Dict[str, Dict[str, Any]]] = None,
    cache_key: Optional[str] = None,
) -> List[BaseTool]:
    """加载 MCP 工具
    
    内置服务器:
        - chart: 图表生成
        - filesystem: 文件系统
        - github: GitHub 操作
        - playwright: 浏览器自动化
    
    示例:
        tools = await load_mcp_tools("chart")
        tools = await load_mcp_tools(config={...}, cache_key="custom")
    """
    factory = get_mcp_factory()
    
    if name:
        return await factory.load(name)
    elif config and cache_key:
        return await factory.load_custom(config, cache_key)
    else:
        raise ValueError("必须指定 name 或 (config + cache_key)")


# ============== 导出 ==============

__all__ = [
    # 模型工厂
    "ModelFactory",
    "ModelProviderConfig",
    "get_model_factory",
    "register_model_provider",
    "load_chat_model",
    # MCP 工厂
    "MCPFactory",
    "MCPServerConfig",
    "get_mcp_factory",
    "register_mcp_server",
    "load_mcp_tools",
]
