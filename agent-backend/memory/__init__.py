"""
记忆插件系统 - v2.0

基于插件式架构的记忆系统，支持：
- 短期记忆（Checkpointer）- 会话状态检查点
- 长期记忆（Store）- 知识存储
- 用户记忆（UserMemory）- 用户画像和语义记忆

全部使用 SQLite 持久化，兼容 langgraph dev
"""

from memory.plugins.base import MemoryPlugin, PluginState
from memory.plugins.manager import MemoryPluginManager
from memory.plugins.checkpointer_plugin import CheckpointerPlugin
from memory.plugins.store_plugin import StorePlugin
from memory.plugins.user_memory_plugin import UserMemoryPlugin
from memory.checkpointer import get_checkpointer
from memory.store import get_store
from memory.config import MemoryPluginConfig, MEMORY_CONFIG

__all__ = [
    # 插件基础
    "MemoryPlugin",
    "PluginState", 
    "MemoryPluginManager",
    
    # 具体插件
    "CheckpointerPlugin",
    "StorePlugin", 
    "UserMemoryPlugin",
    
    # 工厂函数
    "get_checkpointer",
    "get_store",
    
    # 配置
    "MemoryPluginConfig",
    "MEMORY_CONFIG",
]