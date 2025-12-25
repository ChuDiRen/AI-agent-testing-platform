"""
公用记忆服务模块

提供统一的记忆管理接口，可被多个模块使用：
- server.py (LangGraph API Server)
- text2sql
- text2testcase
- 等等

所有数据统一存储在 data/agent_memory.db

使用示例:
    from memory import get_memory_manager, MemoryManager
    
    # 获取全局单例
    memory = get_memory_manager()
    
    # 在 LangGraph 图中使用
    graph = workflow.compile(
        checkpointer=memory.checkpointer,
        store=memory.store
    )
"""

from .manager import MemoryManager, get_memory_manager, reset_memory_manager
from .store import PersistentStore
from .checkpointer import CheckpointerManager, checkpointer_context

__all__ = [
    "MemoryManager",
    "get_memory_manager",
    "reset_memory_manager",
    "PersistentStore",
    "CheckpointerManager",
    "checkpointer_context",
]
