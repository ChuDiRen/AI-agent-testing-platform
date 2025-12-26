"""
长期记忆存储

基于 LangGraph Store 封装，提供 SQLite 持久化知识存储
参考: https://docs.langchain.com/oss/python/langchain/long-term-memory
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Sequence
from dataclasses import dataclass
from datetime import datetime
import hashlib

from langgraph.store.base import BaseStore, Item, SearchItem


@dataclass
class MemoryItem:
    """记忆项"""
    namespace: Tuple[str, ...]
    key: str
    value: Dict[str, Any]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespace": list(self.namespace),
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class PersistentStore(BaseStore):
    """持久化长期记忆存储

    直接使用 SQLite 持久化存储，无内存缓存
    支持:
    - Schema 缓存
    - 查询模式存储
    - 用户偏好
    """

    # 统一数据目录
    DATA_DIR = Path(__file__).parent.parent.resolve() / "data"

    def __init__(self, db_path: str = None):
        """初始化持久化存储

        Args:
            db_path: SQLite 数据库文件路径，默认为 DATA_DIR/agent_memory.db
        """
        if db_path is None:
            db_path = str(self.DATA_DIR / "agent_memory.db")
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None

        # 初始化
        self._ensure_dir()
        self._init_tables()
        
    def _ensure_dir(self) -> None:
        """确保数据库目录存在"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def _init_tables(self) -> None:
        """初始化存储表"""
        conn = self._get_connection()
        
        # 主存储表
        conn.execute("""
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
        
        # 索引
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_namespace 
            ON long_term_memory(namespace)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_namespace_key 
            ON long_term_memory(namespace, key)
        """)
        
        conn.commit()
    
    def _namespace_to_str(self, namespace: Tuple[str, ...]) -> str:
        """将命名空间元组转换为字符串"""
        return "/".join(namespace)
    
    def _str_to_namespace(self, namespace_str: str) -> Tuple[str, ...]:
        """将字符串转换为命名空间元组"""
        return tuple(namespace_str.split("/"))
    
    def _generate_id(self, namespace: Tuple[str, ...], key: str) -> str:
        """生成唯一ID"""
        content = f"{self._namespace_to_str(namespace)}:{key}"
        return hashlib.md5(content.encode()).hexdigest()
    
    # ==================== BaseStore 接口实现 ====================
    
    def put(
        self, 
        namespace: Tuple[str, ...], 
        key: str, 
        value: Dict[str, Any],
        index: Optional[bool] = None
    ) -> None:
        """存储数据"""
        namespace_str = self._namespace_to_str(namespace)
        memory_id = self._generate_id(namespace, key)
        
        conn = self._get_connection()
        value_str = json.dumps(value, ensure_ascii=False, default=str)
        
        conn.execute("""
            INSERT INTO long_term_memory (id, namespace, key, value, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(namespace, key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
        """, (memory_id, namespace_str, key, value_str))
        conn.commit()
    
    def get(
        self, 
        namespace: Tuple[str, ...], 
        key: str
    ) -> Optional[Item]:
        """获取数据"""
        namespace_str = self._namespace_to_str(namespace)
        
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT value, created_at, updated_at FROM long_term_memory WHERE namespace = ? AND key = ?",
            (namespace_str, key)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return Item(
            namespace=namespace,
            key=key,
            value=json.loads(row["value"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
    
    def delete(self, namespace: Tuple[str, ...], key: str) -> None:
        """删除数据"""
        namespace_str = self._namespace_to_str(namespace)
        
        conn = self._get_connection()
        conn.execute(
            "DELETE FROM long_term_memory WHERE namespace = ? AND key = ?",
            (namespace_str, key)
        )
        conn.commit()
    
    def search(
        self, 
        namespace: Tuple[str, ...],
        *,
        query: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchItem]:
        """搜索数据"""
        namespace_str = self._namespace_to_str(namespace)
        
        conn = self._get_connection()
        
        sql = "SELECT namespace, key, value, created_at, updated_at FROM long_term_memory WHERE namespace LIKE ?"
        params = [namespace_str + "%"]
        
        if query:
            sql += " AND value LIKE ?"
            params.append(f"%{query}%")
        
        sql += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor = conn.execute(sql, params)
        results = []
        
        for row in cursor.fetchall():
            value = json.loads(row["value"])
            
            if filter:
                match = True
                for k, v in filter.items():
                    if value.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            
            results.append(SearchItem(
                namespace=self._str_to_namespace(row["namespace"]),
                key=row["key"],
                value=value,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                score=1.0
            ))
        
        return results
    
    def list_namespaces(
        self,
        *,
        prefix: Optional[Tuple[str, ...]] = None,
        suffix: Optional[Tuple[str, ...]] = None,
        max_depth: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Tuple[str, ...]]:
        """列出命名空间"""
        conn = self._get_connection()
        
        sql = "SELECT DISTINCT namespace FROM long_term_memory"
        params = []
        
        if prefix:
            prefix_str = self._namespace_to_str(prefix)
            sql += " WHERE namespace LIKE ?"
            params.append(prefix_str + "%")
        
        cursor = conn.execute(sql, params)
        
        namespaces = set()
        for row in cursor.fetchall():
            ns_str = row["namespace"]
            ns = self._str_to_namespace(ns_str)
            
            if max_depth and len(ns) > max_depth:
                ns = ns[:max_depth]
            
            if suffix:
                suffix_str = self._namespace_to_str(suffix)
                if not ns_str.endswith(suffix_str):
                    continue
            
            namespaces.add(ns)
        
        result = sorted(list(namespaces))
        return result[offset:offset + limit]
    
    # ==================== 便捷方法 ====================
    
    def clear_namespace(self, namespace: Tuple[str, ...]) -> None:
        """清除命名空间下的所有数据"""
        namespace_str = self._namespace_to_str(namespace)
        
        conn = self._get_connection()
        conn.execute(
            "DELETE FROM long_term_memory WHERE namespace LIKE ?",
            (namespace_str + "%",)
        )
        conn.commit()
    
    def get_all_in_namespace(
        self, 
        namespace: Tuple[str, ...]
    ) -> List[MemoryItem]:
        """获取命名空间下的所有数据"""
        items = self.search(namespace, limit=1000)
        return [
            MemoryItem(
                namespace=item.namespace,
                key=item.key,
                value=item.value,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            for item in items
        ]
    
    def close(self) -> None:
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    # ==================== 批量操作 ====================
    
    async def abatch(self, ops: Sequence[tuple]) -> List[Any]:
        """异步批量操作"""
        results = []
        for op in ops:
            op_type = op[0]
            if op_type == "put":
                _, namespace, key, value = op
                self.put(namespace, key, value)
                results.append(None)
            elif op_type == "get":
                _, namespace, key = op
                results.append(self.get(namespace, key))
            elif op_type == "search":
                _, namespace, kwargs = op
                results.append(self.search(namespace, **kwargs))
        return results
    
    def batch(self, ops: Sequence[tuple]) -> List[Any]:
        """同步批量操作"""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(self.abatch(ops))


# ==================== LangGraph API 工厂函数 ====================

_store_instance: Optional[PersistentStore] = None


def get_store() -> PersistentStore:
    """获取 Store 单例实例 - 供 LangGraph API 使用
    
    在 langgraph.json 中配置:
        "store": {
            "path": "./memory/store.py:get_store"
        }
    """
    global _store_instance
    if _store_instance is None:
        from pathlib import Path
        db_path = Path(__file__).parent.parent / "data" / "agent_memory.db"
        _store_instance = PersistentStore(str(db_path))
    return _store_instance
