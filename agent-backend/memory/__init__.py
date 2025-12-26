"""
公用记忆服务模块

提供统一的记忆管理接口，可被多个模块使用：
|- server.py (LangGraph API Server)
|- text2sql
|- text2case
|- 等等

存储配置说明：
=============

1. 使用 `langgraph dev` 命令时：
   - LangGraph API 服务器会读取 langgraph.json 中的 checkpointer 和 store 配置
   - 配置的工厂函数（get_checkpointer, get_store）会被调用
   - 数据保存在 data/agent_memory.db（SQLite）
   
2. 使用 `langgraph up` 命令时（Docker）：
   - 同样读取 langgraph.json 配置
   - 可配置 PostgreSQL 等其他存储后端

3. 直接在 Python 中使用图时（如 run_text2case_sync）：
   - 需要手动传入 checkpointer 和 store
   - 或使用 MemorySaver 等内存存储

langgraph.json 配置示例：
========================
{
  "store": {
    "path": "./memory/store.py:get_store",
    "ttl": { ... }
  },
  "checkpointer": {
    "path": "./memory/checkpointer.py:get_checkpointer",
    "ttl": { ... }
  }
}

重要：图工厂函数（get_app）必须返回未编译的 StateGraph，
让 LangGraph API 服务器负责编译并注入 checkpointer 和 store。

使用示例:
    from memory import get_memory_manager, MemoryManager

    # 获取全局单例
    memory = get_memory_manager()

    # 在 LangGraph 图中使用（直接调用时）
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
