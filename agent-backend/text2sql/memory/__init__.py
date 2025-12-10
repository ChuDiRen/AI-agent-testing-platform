"""
记忆系统模块

提供短期记忆(Checkpointer)和长期记忆(Store)管理

短期记忆 (Short-term Memory):
- 基于 SqliteSaver (Checkpointer)
- 存储会话上下文、对话历史
- 通过 thread_id 区分不同会话
- 参考: https://docs.langchain.com/oss/python/langchain/short-term-memory

长期记忆 (Long-term Memory):
- 基于 PersistentStore (Store)
- 存储 Schema 缓存、查询模式、用户偏好
- 通过 namespace 和 key 组织数据
- 支持跨会话持久化
- 参考: https://docs.langchain.com/oss/python/langchain/long-term-memory
"""

from .checkpointer import get_checkpointer, CheckpointerManager, reset_checkpointer_manager
from .store import get_store, PersistentStore, MemoryItem
from .manager import MemoryManager, get_memory_manager, reset_memory_manager

# 保持向后兼容
StoreManager = PersistentStore

__all__ = [
    # 短期记忆
    "get_checkpointer",
    "CheckpointerManager",
    "reset_checkpointer_manager",
    # 长期记忆
    "get_store",
    "PersistentStore",
    "StoreManager",  # 向后兼容
    "MemoryItem",
    # 统一管理器
    "MemoryManager",
    "get_memory_manager",
    "reset_memory_manager"
]
