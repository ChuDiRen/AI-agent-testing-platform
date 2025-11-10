"""
SQLite Store Implementation for LangGraph

这个模块实现了基于SQLite的store，用于存储长期记忆和文档数据。
可以通过langgraph.yaml配置文件来使用此store。
"""

import json
import sqlite3
from contextlib import contextmanager, asynccontextmanager
from typing import Iterator, Optional, Sequence

import aiosqlite

from langgraph.store.base import BaseStore, Item, Op, Result, GetOp, PutOp, SearchOp, ListNamespacesOp


class SqliteStore(BaseStore):
    """
    基于SQLite的Store实现
    
    用于存储和检索长期记忆数据，包括：
    - 文档存储
    - 命名空间管理
    - 元数据索引
    
    使用方法：
        在langgraph.yaml中配置：
        store:
          path: ./examples/sqlite_storage/sqlite_store.py:create_store
    """

    def __init__(self, db_path: str = "langgraph.db"):
        """
        初始化SQLite Store
        
        Args:
            db_path: SQLite数据库文件路径（统一数据库）
        """
        self.db_path = db_path
        self._setup_database()

    def _setup_database(self):
        """创建必要的数据库表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建items表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS store_items (
                    namespace TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (namespace, key)
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_store_namespace 
                ON store_items(namespace)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_store_updated_at 
                ON store_items(updated_at DESC)
            """)
            
            conn.commit()

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    @asynccontextmanager
    async def _get_async_connection(self):
        """获取异步数据库连接的上下文管理器"""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        try:
            yield conn
        finally:
            await conn.close()

    def batch(self, ops: Sequence[Op]) -> list[Result]:
        """
        批量执行操作
        
        Args:
            ops: 操作列表
            
        Returns:
            结果列表
        """
        results = []
        for op in ops:
            if isinstance(op, GetOp):
                results.append(self._get(op.namespace, op.key))
            elif isinstance(op, PutOp):
                results.append(self._put(op.namespace, op.key, op.value))
            elif isinstance(op, SearchOp):
                results.append(self._search(op.namespace_prefix, op.filter, op.limit, op.offset))
            elif isinstance(op, ListNamespacesOp):
                results.append(self._list_namespaces(op.prefix, op.suffix, op.max_depth, op.limit, op.offset))
            else:
                results.append(None)
        return results

    def _get(self, namespace: tuple[str, ...], key: str) -> Optional[Item]:
        """获取单个item"""
        namespace_str = "/".join(namespace)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT namespace, key, value, created_at, updated_at
                FROM store_items
                WHERE namespace = ? AND key = ?
                """,
                (namespace_str, key),
            )
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return Item(
                namespace=tuple(row["namespace"].split("/")),
                key=row["key"],
                value=json.loads(row["value"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    def _put(self, namespace: tuple[str, ...], key: str, value: dict) -> None:
        """存储item"""
        namespace_str = "/".join(namespace)
        value_str = json.dumps(value, ensure_ascii=False)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO store_items (namespace, key, value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (namespace_str, key, value_str),
            )
            conn.commit()

    def _search(
        self,
        namespace_prefix: tuple[str, ...],
        filter: Optional[dict] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Item]:
        """搜索items"""
        namespace_prefix_str = "/".join(namespace_prefix)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT namespace, key, value, created_at, updated_at
                FROM store_items
                WHERE namespace LIKE ?
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """
            
            cursor.execute(
                query,
                (f"{namespace_prefix_str}%", limit, offset),
            )
            
            items = []
            for row in cursor.fetchall():
                item = Item(
                    namespace=tuple(row["namespace"].split("/")),
                    key=row["key"],
                    value=json.loads(row["value"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                
                # 应用过滤器
                if filter:
                    match = True
                    for filter_key, filter_value in filter.items():
                        if item.value.get(filter_key) != filter_value:
                            match = False
                            break
                    if match:
                        items.append(item)
                else:
                    items.append(item)
            
            return items

    def _list_namespaces(
        self,
        prefix: Optional[tuple[str, ...]] = None,
        suffix: Optional[tuple[str, ...]] = None,
        max_depth: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[str, ...]]:
        """列出命名空间"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT DISTINCT namespace FROM store_items"
            params = []
            
            if prefix:
                prefix_str = "/".join(prefix)
                query += " WHERE namespace LIKE ?"
                params.append(f"{prefix_str}%")
            
            query += " ORDER BY namespace LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            namespaces = []
            for row in cursor.fetchall():
                namespace = tuple(row["namespace"].split("/"))
                
                # 应用max_depth过滤
                if max_depth and len(namespace) > max_depth:
                    continue
                
                # 应用suffix过滤
                if suffix:
                    if not namespace[-len(suffix):] == suffix:
                        continue
                
                namespaces.append(namespace)
            
            return namespaces

    def get(self, namespace: tuple[str, ...], key: str) -> Optional[Item]:
        """同步获取item"""
        return self._get(namespace, key)

    def put(self, namespace: tuple[str, ...], key: str, value: dict) -> None:
        """同步存储item"""
        self._put(namespace, key, value)

    def delete(self, namespace: tuple[str, ...], key: str) -> None:
        """删除item"""
        namespace_str = "/".join(namespace)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM store_items WHERE namespace = ? AND key = ?",
                (namespace_str, key),
            )
            conn.commit()

    def search(
        self,
        namespace_prefix: tuple[str, ...],
        filter: Optional[dict] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Item]:
        """同步搜索items"""
        return self._search(namespace_prefix, filter, limit, offset)

    def list_namespaces(
        self,
        prefix: Optional[tuple[str, ...]] = None,
        suffix: Optional[tuple[str, ...]] = None,
        max_depth: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[str, ...]]:
        """同步列出命名空间"""
        return self._list_namespaces(prefix, suffix, max_depth, limit, offset)

    # 异步方法实现
    async def aget(self, namespace: tuple[str, ...], key: str) -> Optional[Item]:
        """异步获取item"""
        namespace_str = "/".join(namespace)
        
        async with self._get_async_connection() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """
                SELECT namespace, key, value, created_at, updated_at
                FROM store_items
                WHERE namespace = ? AND key = ?
                """,
                (namespace_str, key),
            )
            
            row = await cursor.fetchone()
            if not row:
                return None
            
            return Item(
                namespace=tuple(row["namespace"].split("/")),
                key=row["key"],
                value=json.loads(row["value"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    async def aput(self, namespace: tuple[str, ...], key: str, value: dict) -> None:
        """异步存储item"""
        namespace_str = "/".join(namespace)
        value_str = json.dumps(value, ensure_ascii=False)
        
        async with self._get_async_connection() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """
                INSERT OR REPLACE INTO store_items (namespace, key, value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (namespace_str, key, value_str),
            )
            await conn.commit()

    async def adelete(self, namespace: tuple[str, ...], key: str) -> None:
        """异步删除item"""
        namespace_str = "/".join(namespace)
        
        async with self._get_async_connection() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "DELETE FROM store_items WHERE namespace = ? AND key = ?",
                (namespace_str, key),
            )
            await conn.commit()

    async def asearch(
        self,
        namespace_prefix: tuple[str, ...],
        filter: Optional[dict] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Item]:
        """异步搜索items"""
        namespace_prefix_str = "/".join(namespace_prefix)
        
        async with self._get_async_connection() as conn:
            cursor = await conn.cursor()
            
            query = """
                SELECT namespace, key, value, created_at, updated_at
                FROM store_items
                WHERE namespace LIKE ?
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """
            
            await cursor.execute(
                query,
                (f"{namespace_prefix_str}%", limit, offset),
            )
            
            items = []
            async for row in cursor:
                item = Item(
                    namespace=tuple(row["namespace"].split("/")),
                    key=row["key"],
                    value=json.loads(row["value"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                
                # 应用过滤器
                if filter:
                    match = True
                    for filter_key, filter_value in filter.items():
                        if item.value.get(filter_key) != filter_value:
                            match = False
                            break
                    if match:
                        items.append(item)
                else:
                    items.append(item)
            
            return items

    async def alist_namespaces(
        self,
        prefix: Optional[tuple[str, ...]] = None,
        suffix: Optional[tuple[str, ...]] = None,
        max_depth: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[str, ...]]:
        """异步列出命名空间"""
        async with self._get_async_connection() as conn:
            cursor = await conn.cursor()
            
            query = "SELECT DISTINCT namespace FROM store_items"
            params = []
            
            if prefix:
                prefix_str = "/".join(prefix)
                query += " WHERE namespace LIKE ?"
                params.append(f"{prefix_str}%")
            
            query += " ORDER BY namespace LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            await cursor.execute(query, params)
            
            namespaces = []
            async for row in cursor:
                namespace = tuple(row["namespace"].split("/"))
                
                # 应用max_depth过滤
                if max_depth and len(namespace) > max_depth:
                    continue
                
                # 应用suffix过滤
                if suffix:
                    if not namespace[-len(suffix):] == suffix:
                        continue
                
                namespaces.append(namespace)
            
            return namespaces

    async def abatch(self, ops: Sequence[Op]) -> list[Result]:
        """异步批量执行操作"""
        results = []
        for op in ops:
            if isinstance(op, GetOp):
                results.append(await self.aget(op.namespace, op.key))
            elif isinstance(op, PutOp):
                results.append(await self.aput(op.namespace, op.key, op.value))
            elif isinstance(op, SearchOp):
                results.append(await self.asearch(op.namespace_prefix, op.filter, op.limit, op.offset))
            elif isinstance(op, ListNamespacesOp):
                results.append(await self.alist_namespaces(op.prefix, op.suffix, op.max_depth, op.limit, op.offset))
            else:
                results.append(None)
        return results


def create_store() -> SqliteStore:
    """
    工厂函数：创建SQLite store实例
    
    这个函数会袾langgraph.yaml配置文件调用
    
    Returns:
        SqliteStore实例
    """
    return SqliteStore(db_path="./data/langgraph.db")
