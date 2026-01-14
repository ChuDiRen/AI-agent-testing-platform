# memory/plugins/manager.py
from typing import Dict, List, Optional, Type, Any
from memory.plugins.base import MemoryPlugin, PluginState

class MemoryPluginManager:
    """记忆插件管理器 - 单例模式"""

    _instance: Optional["MemoryPluginManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: str):
        if hasattr(self, "_initialized"):
            return
        self.db_path = db_path
        self._plugins: Dict[str, MemoryPlugin] = {}
        self._initialized = True

    def register(self, plugin_class: Type[MemoryPlugin]) -> None:
        """注册插件类"""
        plugin = plugin_class(self.db_path)
        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> None:
        """注销插件"""
        if name in self._plugins:
            del self._plugins[name]

    def get(self, name: str) -> Optional[MemoryPlugin]:
        """获取插件实例"""
        return self._plugins.get(name)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """列出所有插件"""
        return [
            {
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "state": p.state.value
            }
            for p in self._plugins.values()
        ]

    async def enable_plugin(self, name: str) -> bool:
        """启用指定插件"""
        plugin = self._plugins.get(name)
        if plugin:
            await plugin.enable()
            return True
        return False

    async def disable_plugin(self, name: str) -> bool:
        """禁用指定插件"""
        plugin = self._plugins.get(name)
        if plugin:
            await plugin.disable()
            return True
        return False

    async def enable_all(self) -> None:
        """启用所有插件"""
        for plugin in self._plugins.values():
            await plugin.enable()

    async def disable_all(self) -> None:
        """禁用所有插件"""
        for plugin in self._plugins.values():
            await plugin.disable()