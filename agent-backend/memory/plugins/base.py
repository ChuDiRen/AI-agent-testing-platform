# memory/plugins/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum

class PluginState(Enum):
    """插件状态"""
    DISABLED = "disabled"      # 已禁用
    ENABLED = "enabled"        # 已启用
    INITIALIZING = "init"      # 初始化中
    ERROR = "error"            # 错误状态

class MemoryPlugin(ABC):
    """记忆插件基类 - 所有记忆插件必须继承此类"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._state = PluginState.DISABLED
        self._conn = None

    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称 (唯一标识)"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass

    @property
    def state(self) -> PluginState:
        """插件状态"""
        return self._state

    @abstractmethod
    async def setup(self) -> None:
        """初始化插件 (创建表、索引等)"""
        pass

    @abstractmethod
    async def teardown(self) -> None:
        """清理插件资源"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        pass

    async def enable(self) -> None:
        """启用插件"""
        await self.setup()
        self._state = PluginState.ENABLED

    async def disable(self) -> None:
        """禁用插件"""
        await self.teardown()
        self._state = PluginState.DISABLED