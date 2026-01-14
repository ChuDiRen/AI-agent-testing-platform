"""
统一记忆系统接口

提供简洁的 API 访问所有记忆插件
"""

from typing import Optional, List, Dict, Any
from memory.plugins.manager import MemoryPluginManager
from memory.plugins.checkpointer_plugin import CheckpointerPlugin
from memory.plugins.store_plugin import StorePlugin
from memory.plugins.user_memory_plugin import UserMemoryPlugin
from memory.config import MEMORY_CONFIG


class MemorySystem:
    """统一记忆系统入口"""

    def __init__(self):
        self._manager: Optional[MemoryPluginManager] = None

    async def initialize(self) -> None:
        """初始化记忆系统"""
        if self._manager is None:
            self._manager = MemoryPluginManager(MEMORY_CONFIG.db_path)

            # 注册所有插件
            self._manager.register(CheckpointerPlugin)
            self._manager.register(StorePlugin)
            self._manager.register(UserMemoryPlugin)

            # 启用配置中的插件
            for plugin_name in MEMORY_CONFIG.enabled_plugins:
                await self._manager.enable_plugin(plugin_name)

    async def get_checkpointer(self):
        """获取检查点"""
        return await self._manager.get("checkpointer").get_saver()

    async def get_store(self):
        """获取存储"""
        return self._manager.get("store")

    async def get_user_memory(self):
        """获取用户记忆"""
        return self._manager.get("user_memory")

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "plugins": self._manager.list_plugins(),
            "db_path": MEMORY_CONFIG.db_path
        }


# 全局实例
_memory_system: Optional[MemorySystem] = None


async def get_memory_system() -> MemorySystem:
    """获取记忆系统实例"""
    global _memory_system
    if _memory_system is None:
        _memory_system = MemorySystem()
        await _memory_system.initialize()
    return _memory_system

