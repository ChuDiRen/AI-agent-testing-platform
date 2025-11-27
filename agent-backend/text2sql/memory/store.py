"""
长期记忆存储

基于InMemoryStore封装，提供持久化知识存储
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from langgraph.store.memory import InMemoryStore


@dataclass
class MemoryItem:
    """记忆项"""
    namespace: Tuple[str, ...]
    key: str
    value: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespace": list(self.namespace),
            "key": self.key,
            "value": self.value
        }


class StoreManager:
    """长期记忆存储管理器
    
    提供Schema缓存、查询模式和用户偏好的持久化存储
    """
    
    def __init__(self, db_path: str = "data/agent_memory.db"):
        """初始化存储管理器
        
        Args:
            db_path: SQLite数据库文件路径
        """
        self.db_path = Path(db_path)
        self._store: Optional[InMemoryStore] = None
        self._conn: Optional[sqlite3.Connection] = None
        
    def _ensure_dir(self) -> None:
        """确保数据库目录存在"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._conn is None:
            self._ensure_dir()
            self._conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._init_tables()
        return self._conn
    
    def _init_tables(self) -> None:
        """初始化存储表"""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory (
                namespace TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (namespace, key)
            )
        """)
        self._conn.commit()
        
    def get_store(self) -> InMemoryStore:
        """获取InMemoryStore实例
        
        返回内存存储，同时会加载持久化的数据
        """
        if self._store is None:
            self._store = InMemoryStore()
            self._load_from_db()
        return self._store
    
    def _load_from_db(self) -> None:
        """从数据库加载数据到内存存储"""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT namespace, key, value FROM long_term_memory"
        )
        for row in cursor.fetchall():
            namespace = tuple(row[0].split("/"))
            key = row[1]
            value = json.loads(row[2])
            self._store.put(namespace, key, value)
            
    def put(self, namespace: Tuple[str, ...], key: str, value: Dict[str, Any]) -> None:
        """存储数据
        
        同时保存到内存和数据库
        """
        # 保存到内存
        store = self.get_store()
        store.put(namespace, key, value)
        
        # 持久化到数据库
        conn = self._get_connection()
        namespace_str = "/".join(namespace)
        value_str = json.dumps(value, ensure_ascii=False)
        conn.execute("""
            INSERT OR REPLACE INTO long_term_memory (namespace, key, value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (namespace_str, key, value_str))
        conn.commit()
        
    def get(self, namespace: Tuple[str, ...], key: str) -> Optional[Dict[str, Any]]:
        """获取数据"""
        store = self.get_store()
        item = store.get(namespace, key)
        return item.value if item else None
    
    def search(
        self, 
        namespace: Tuple[str, ...], 
        query: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryItem]:
        """搜索数据
        
        Args:
            namespace: 命名空间
            query: 搜索查询（可选）
            limit: 最大返回数量
            
        Returns:
            匹配的记忆项列表
        """
        store = self.get_store()
        items = store.search(namespace, query=query, limit=limit)
        return [
            MemoryItem(
                namespace=item.namespace,
                key=item.key,
                value=item.value
            )
            for item in items
        ]
    
    def delete(self, namespace: Tuple[str, ...], key: str) -> None:
        """删除数据"""
        store = self.get_store()
        store.delete(namespace, key)
        
        # 从数据库删除
        conn = self._get_connection()
        namespace_str = "/".join(namespace)
        conn.execute(
            "DELETE FROM long_term_memory WHERE namespace = ? AND key = ?",
            (namespace_str, key)
        )
        conn.commit()
        
    def clear_namespace(self, namespace: Tuple[str, ...]) -> None:
        """清除命名空间下的所有数据"""
        conn = self._get_connection()
        namespace_str = "/".join(namespace)
        conn.execute(
            "DELETE FROM long_term_memory WHERE namespace LIKE ?",
            (namespace_str + "%",)
        )
        conn.commit()
        
        # 重新加载内存存储
        self._store = None
        
    def close(self) -> None:
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._store = None


# 全局管理器实例
_store_manager: Optional[StoreManager] = None


def get_store(db_path: str = "data/agent_memory.db") -> InMemoryStore:
    """获取全局的InMemoryStore实例"""
    global _store_manager
    if _store_manager is None:
        _store_manager = StoreManager(db_path)
    return _store_manager.get_store()


def get_store_manager() -> StoreManager:
    """获取全局存储管理器实例"""
    global _store_manager
    if _store_manager is None:
        _store_manager = StoreManager()
    return _store_manager
