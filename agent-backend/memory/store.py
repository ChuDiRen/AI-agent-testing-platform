# memory/store.py - 内联工厂逻辑版
from pathlib import Path
from typing import Optional, cast
from langgraph.store.base import BaseStore

# 使用绝对导入
import sys
sys.path.append(str(Path(__file__).parent.parent))
from memory.plugins.manager import MemoryPluginManager
from memory.plugins.store_plugin import StorePlugin

# 数据目录与全局实例
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = str(DATA_DIR / "agent_memory.db")
_plugin_manager: Optional[MemoryPluginManager] = None


async def _ensure_plugin_manager() -> MemoryPluginManager:
    """返回全局插件管理器实例（首次调用时初始化）"""
    global _plugin_manager
    if _plugin_manager is None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        _plugin_manager = MemoryPluginManager(DB_PATH)
    return _plugin_manager


async def _get_or_enable_plugin(plugin_cls, name: str):
    """注册并启用插件，返回插件实例"""
    mgr = await _ensure_plugin_manager()
    if name not in [p["name"] for p in mgr.list_plugins()]:
        mgr.register(plugin_cls)
    await mgr.enable_plugin(name)
    return mgr.get(name)


async def get_store() -> BaseStore:
    """获取 Store - 供 langgraph.json 配置使用"""
    plugin = await _get_or_enable_plugin(StorePlugin, "store")
    return cast(BaseStore, plugin)