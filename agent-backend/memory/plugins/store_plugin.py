# memory/plugins/store_plugin.py
import json
import aiosqlite
import asyncio
from datetime import datetime, timedelta
from typing import Tuple, List, Optional, Dict, Any, Sequence
from langgraph.store.base import BaseStore, Item, SearchItem
from memory.config import MEMORY_CONFIG
from memory.plugins.base import MemoryPlugin, PluginState

class StorePlugin(MemoryPlugin, BaseStore):
    """长期记忆插件 - 实现 BaseStore 接口"""

    name = "store"
    version = "1.0.0"
    description = "长期知识存储，支持 namespace/key 结构化存储"

    async def setup(self) -> None:
        """初始化存储表并启动 TTL 清理任务"""
        self._conn = await aiosqlite.connect(
            self.db_path, check_same_thread=False
        )
        self._conn.row_factory = aiosqlite.Row

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id TEXT PRIMARY KEY,
                namespace TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(namespace, key)
            )
        """)

        await self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_ltm_namespace
            ON long_term_memory(namespace)
        """)

        await self._conn.commit()
        self._state = PluginState.ENABLED

        # 启动 TTL 清理任务
        ttl_days = MEMORY_CONFIG.store.get("ttl_days", 7)
        sweep_interval = MEMORY_CONFIG.store.get("sweep_interval", 3600)
        self._cleanup_task = asyncio.create_task(
            self._periodic_cleanup(ttl_days, sweep_interval)
        )

    async def teardown(self) -> None:
        """关闭连接并取消清理任务"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        if self._conn:
            await self._conn.close()
            self._conn = None
        self._state = PluginState.DISABLED

    async def _periodic_cleanup(self, ttl_days: int, interval_seconds: int) -> None:
        """后台定时清理过期记录"""
        try:
            while True:
                await asyncio.sleep(interval_seconds)
                await self._cleanup_expired(ttl_days)
        except asyncio.CancelledError:
            pass

    async def _cleanup_expired(self, ttl_days: int) -> None:
        """清理超过 ttl_days 的记录"""
        cutoff = datetime.utcnow() - timedelta(days=ttl_days)
        await self._conn.execute(
            "DELETE FROM long_term_memory WHERE updated_at < ?",
            (cutoff.isoformat(),)
        )
        await self._conn.commit()

    # BaseStore 接口实现保持不变
    async def put(self, namespace: Tuple[str, ...], key: str,
                  value: Dict[str, Any], index: Optional[bool] = None) -> None:
        ns_str = "/".join(namespace)
        val_str = json.dumps(value, ensure_ascii=False, default=str)
        await self._conn.execute("""
            INSERT INTO long_term_memory (id, namespace, key, value, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(namespace, key) DO UPDATE SET
                value = excluded.value, updated_at = CURRENT_TIMESTAMP
        """, (f"{ns_str}:{key}", ns_str, key, val_str))
        await self._conn.commit()

    async def get(self, namespace: Tuple[str, ...], key: str) -> Optional[Item]:
        ns_str = "/".join(namespace)
        cursor = await self._conn.execute(
            "SELECT value, created_at, updated_at FROM long_term_memory "
            "WHERE namespace = ? AND key = ?",
            (ns_str, key)
        )
        row = await cursor.fetchone()
        if row:
            return Item(
                namespace=namespace, key=key,
                value=json.loads(row["value"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        return None

    async def delete(self, namespace: Tuple[str, ...], key: str) -> None:
        ns_str = "/".join(namespace)
        await self._conn.execute(
            "DELETE FROM long_term_memory WHERE namespace = ? AND key = ?",
            (ns_str, key)
        )
        await self._conn.commit()

    async def search(self, namespace: Tuple[str, ...], *,
                     query: Optional[str] = None, limit: int = 10,
                     offset: int = 0, **kwargs) -> List[SearchItem]:
        ns_str = "/".join(namespace)
        sql = "SELECT * FROM long_term_memory WHERE namespace LIKE ?"
        params = [ns_str + "%"]

        if query:
            sql += " AND value LIKE ?"
            params.append(f"%{query}%")

        sql += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await self._conn.execute(sql, params)
        results = []
        async for row in cursor:
            results.append(SearchItem(
                namespace=tuple(row["namespace"].split("/")),
                key=row["key"],
                value=json.loads(row["value"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                score=1.0
            ))
        return results

    async def list_namespaces(
        self,
        *,
        prefix: Optional[Tuple[str, ...]] = None,
        suffix: Optional[Tuple[str, ...]] = None,
        max_depth: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Tuple[str, ...]]:
        sql = "SELECT DISTINCT namespace FROM long_term_memory"
        params = []
        
        if prefix:
            prefix_str = "/".join(prefix)
            sql += " WHERE namespace LIKE ?"
            params.append(f"{prefix_str}%")
        
        cursor = await self._conn.execute(sql, params)
        namespaces = set()
        
        async for row in cursor:
            ns = tuple(row["namespace"].split("/"))
            if max_depth and len(ns) > max_depth:
                ns = ns[:max_depth]
            namespaces.add(ns)
        
        result = sorted(list(namespaces))
        return result[offset:offset + limit]

    async def abatch(self, ops: Sequence[tuple]) -> List[Any]:
        results = []
        for op in ops:
            op_type = op[0]
            if op_type == "put":
                _, namespace, key, value = op
                await self.put(namespace, key, value)
                results.append(None)
            elif op_type == "get":
                _, namespace, key = op
                results.append(await self.get(namespace, key))
            elif op_type == "search":
                _, namespace, kwargs = op
                results.append(await self.search(namespace, **kwargs))
            else:
                results.append(None)
        return results

    async def batch(self, ops: Sequence[tuple]) -> List[Any]:
        return await self.abatch(ops)

    async def health_check(self) -> Dict[str, Any]:
        cursor = await self._conn.execute(
            "SELECT COUNT(*) as cnt FROM long_term_memory"
        )
        row = await cursor.fetchone()
        return {
            "status": "healthy",
            "plugin": self.name,
            "records_count": row["cnt"] if row else 0,
            "state": self._state.value
        }