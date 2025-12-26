"""
LangGraph Runtime Patch

解决 langgraph dev 模式下自定义 checkpointer 不生效的问题。

问题原因：
- langgraph dev 使用 langgraph_runtime_inmem 运行时
- langgraph_runtime_inmem.checkpoint.Checkpointer() 硬编码使用 InMemorySaver
- langgraph.json 中的 checkpointer.path 配置被忽略

解决方案：
- 在服务启动前 Monkey Patch langgraph_runtime_inmem.checkpoint 模块
- 替换 Checkpointer 工厂函数为我们的 SQLite 实现
"""

import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def patch_runtime_checkpointer():
    """
    Patch langgraph_runtime_inmem 使用自定义 SQLite Checkpointer
    
    必须在 langgraph dev 启动前调用！
    """
    try:
        # 设置必要的环境变量（langgraph_runtime_inmem 需要）
        if not os.environ.get("LANGGRAPH_RUNTIME_EDITION"):
            os.environ["LANGGRAPH_RUNTIME_EDITION"] = "inmem"
        
        # 导入我们的 SQLite checkpointer
        from memory.checkpointer import get_checkpointer as get_sqlite_checkpointer
        
        # 获取 SQLite checkpointer 实例
        sqlite_checkpointer = get_sqlite_checkpointer()
        
        # Patch langgraph_runtime_inmem.checkpoint 模块
        import langgraph_runtime_inmem.checkpoint as inmem_checkpoint
        
        # 保存原始的 Checkpointer
        _original_checkpointer = inmem_checkpoint.Checkpointer
        _original_memory = inmem_checkpoint.MEMORY
        
        # 创建新的 Checkpointer 工厂函数
        def patched_checkpointer(*args, **kwargs):
            """返回 SQLite Checkpointer 而不是 InMemorySaver"""
            return sqlite_checkpointer
        
        # 替换模块级别的 Checkpointer 和 MEMORY
        inmem_checkpoint.Checkpointer = patched_checkpointer
        inmem_checkpoint.MEMORY = sqlite_checkpointer
        
        # 同时 patch langgraph_runtime.checkpoint（如果存在别名）
        try:
            import langgraph_runtime.checkpoint as runtime_checkpoint
            runtime_checkpoint.Checkpointer = patched_checkpointer
        except ImportError:
            pass
        
        logger.info(f"✅ Patched langgraph_runtime_inmem to use SQLite checkpointer")
        logger.info(f"   Database: {sqlite_checkpointer.conn.execute('PRAGMA database_list').fetchone()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to patch runtime checkpointer: {e}")
        return False


def unpatch_runtime_checkpointer():
    """恢复原始的 Checkpointer（用于测试）"""
    try:
        import langgraph_runtime_inmem.checkpoint as inmem_checkpoint
        from langgraph_runtime_inmem.checkpoint import InMemorySaver
        
        # 恢复原始实现
        inmem_checkpoint.MEMORY = None
        
        def original_checkpointer(*args, unpack_hook=None, **kwargs):
            if inmem_checkpoint.MEMORY is None:
                inmem_checkpoint.MEMORY = InMemorySaver()
            if unpack_hook is not None:
                from langgraph_api.serde import Serializer
                saver = InMemorySaver(
                    serde=Serializer(__unpack_ext_hook__=unpack_hook), **kwargs
                )
                saver.writes = inmem_checkpoint.MEMORY.writes
                saver.blobs = inmem_checkpoint.MEMORY.blobs
                saver.storage = inmem_checkpoint.MEMORY.storage
                return saver
            return inmem_checkpoint.MEMORY
        
        inmem_checkpoint.Checkpointer = original_checkpointer
        
        logger.info("✅ Restored original langgraph_runtime_inmem Checkpointer")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to unpatch runtime checkpointer: {e}")
        return False


# 自动 patch（当模块被导入时）
_auto_patched = False


def auto_patch():
    """自动 patch（仅执行一次）"""
    global _auto_patched
    if not _auto_patched:
        _auto_patched = patch_runtime_checkpointer()
    return _auto_patched
