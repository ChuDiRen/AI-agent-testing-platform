# memory/plugins/checkpointer_plugin.py
import aiosqlite
from typing import List, Dict, Any, Optional
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from memory.plugins.base import MemoryPlugin, PluginState

class CheckpointerPlugin(MemoryPlugin):
    """短期记忆插件 - 基于 AsyncSqliteSaver"""

    name = "checkpointer"
    version = "1.0.0"
    description = "会话状态检查点管理，支持对话历史和状态回溯"

    def __init__(self, db_path: str):
        super().__init__(db_path)
        self._checkpointer: Optional[AsyncSqliteSaver] = None

    async def setup(self) -> None:
        """初始化检查点表"""
        self._conn = await aiosqlite.connect(self.db_path, check_same_thread=False)
        self._checkpointer = AsyncSqliteSaver(self._conn)
        await self._checkpointer.setup()  # 创建 checkpoints, writes 表
        self._state = PluginState.ENABLED

    async def teardown(self) -> None:
        """关闭连接"""
        if self._conn:
            await self._conn.close()
            self._conn = None
        self._checkpointer = None
        self._state = PluginState.DISABLED

    async def get_saver(self) -> AsyncSqliteSaver:
        """获取 AsyncSqliteSaver 实例"""
        if self._checkpointer is None:
            await self.setup()
        return self._checkpointer

    async def delete_thread(self, thread_id: str) -> None:
        """删除指定线程的所有检查点"""
        if self._conn:
            await self._conn.execute(
                "DELETE FROM checkpoints WHERE thread_id = ?",
                (thread_id,)
            )
            await self._conn.commit()

    async def list_threads(self) -> List[str]:
        """列出所有线程ID"""
        if self._conn:
            cursor = await self._conn.execute(
                "SELECT DISTINCT thread_id FROM checkpoints"
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
        return []

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            threads = await self.list_threads()
            return {
                "status": "healthy",
                "plugin": self.name,
                "threads_count": len(threads),
                "state": self._state.value
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}