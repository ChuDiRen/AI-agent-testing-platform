"""
记忆统一管理器

整合短期记忆(Checkpointer)和长期记忆(Store)的统一接口
参考: 
- https://docs.langchain.com/oss/python/langchain/short-term-memory
- https://docs.langchain.com/oss/python/langchain/long-term-memory
"""

import sqlite3
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.base import BaseStore

from .checkpointer import CheckpointerManager
from .store import PersistentStore


class MemoryManager:
    """记忆统一管理器
    
    提供短期记忆和长期记忆的统一管理接口
    
    短期记忆 (Checkpointer):
    - 会话上下文、对话历史
    - 通过 thread_id 区分不同会话
    - 自动管理消息历史
    
    长期记忆 (Store):
    - Schema 缓存
    - 查询模式
    - 用户偏好
    - 跨会话持久化
    """
    
    # 命名空间常量
    NS_SCHEMA_CACHE = "schema_cache"
    NS_QUERY_PATTERNS = "query_patterns"
    NS_USER_PREFERENCES = "user_preferences"
    NS_SUCCESSFUL_QUERIES = "successful_queries"

    # 统一数据目录
    DATA_DIR = Path(__file__).parent.parent.resolve() / "data"

    def __init__(self, db_path: str = None):
        """初始化记忆管理器

        Args:
            db_path: 数据库文件路径（短期和长期记忆共用），默认为 DATA_DIR/agent_memory.db
        """
        if db_path is None:
            db_path = str(self.DATA_DIR / "agent_memory.db")
        self.db_path = db_path
        self._checkpointer_manager = CheckpointerManager(db_path)
        self._store = PersistentStore(db_path=db_path)
        
    @property
    def checkpointer(self) -> SqliteSaver:
        """获取短期记忆（会话检查点）
        
        用于 LangGraph 图编译时传入
        """
        return self._checkpointer_manager.get_checkpointer()
    
    @property
    def store(self) -> BaseStore:
        """获取长期记忆（知识存储）
        
        用于 LangGraph 图编译时传入
        """
        return self._store
    
    # ==================== Schema 缓存 ====================
    
    def cache_schema(
        self, 
        connection_id: int, 
        schema_info: Dict[str, Any],
        ttl_hours: int = 24
    ) -> None:
        """缓存数据库 Schema 信息"""
        namespace = (self.NS_SCHEMA_CACHE, str(connection_id))
        self._store.put(namespace, "schema", {
            "data": schema_info,
            "cached_at": datetime.now().isoformat(),
            "ttl_hours": ttl_hours
        })
        
    def get_cached_schema(self, connection_id: int) -> Optional[Dict[str, Any]]:
        """获取缓存的 Schema 信息"""
        namespace = (self.NS_SCHEMA_CACHE, str(connection_id))
        item = self._store.get(namespace, "schema")
        
        if item is None:
            return None
        
        # 检查是否过期
        cached_at = item.value.get("cached_at")
        ttl_hours = item.value.get("ttl_hours", 24)
        
        if cached_at:
            cached_time = datetime.fromisoformat(cached_at)
            if datetime.now() - cached_time > timedelta(hours=ttl_hours):
                self._store.delete(namespace, "schema")
                return None
        
        return item.value.get("data")
    
    def invalidate_schema_cache(self, connection_id: int) -> None:
        """使 Schema 缓存失效"""
        namespace = (self.NS_SCHEMA_CACHE, str(connection_id))
        self._store.clear_namespace(namespace)
        
    # ==================== 查询模式 ====================
    
    def save_query_pattern(
        self, 
        user_id: str, 
        natural_query: str,
        sql: str,
        schema_context: Dict[str, Any],
        success: bool = True,
        execution_time_ms: float = 0
    ) -> str:
        """保存成功的查询模式"""
        pattern_id = hashlib.md5(
            f"{user_id}:{natural_query}".encode()
        ).hexdigest()[:12]
        
        namespace = (self.NS_QUERY_PATTERNS, user_id)
        self._store.put(namespace, pattern_id, {
            "natural_query": natural_query,
            "sql": sql,
            "schema_context": schema_context,
            "success": success,
            "execution_time_ms": execution_time_ms,
            "created_at": datetime.now().isoformat(),
            "use_count": 1
        })
        
        return pattern_id
    
    def get_similar_patterns(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """获取相似的查询模式"""
        namespace = (self.NS_QUERY_PATTERNS, user_id)
        items = self._store.search(namespace, query=query, limit=limit)
        
        return [{"pattern_id": item.key, **item.value} for item in items]
    
    # ==================== 成功查询历史 ====================
    
    def save_successful_query(
        self,
        connection_id: int,
        natural_query: str,
        sql: str,
        result_summary: Dict[str, Any]
    ) -> None:
        """保存成功执行的查询"""
        query_id = hashlib.md5(
            f"{connection_id}:{sql}".encode()
        ).hexdigest()[:12]
        
        namespace = (self.NS_SUCCESSFUL_QUERIES, str(connection_id))
        self._store.put(namespace, query_id, {
            "natural_query": natural_query,
            "sql": sql,
            "result_summary": result_summary,
            "executed_at": datetime.now().isoformat()
        })
    
    def get_successful_queries(
        self,
        connection_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取成功查询历史"""
        namespace = (self.NS_SUCCESSFUL_QUERIES, str(connection_id))
        items = self._store.search(namespace, limit=limit)
        return [item.value for item in items]
    
    # ==================== 用户偏好 ====================
    
    def save_user_preference(self, user_id: str, key: str, value: Any) -> None:
        """保存用户偏好"""
        namespace = (self.NS_USER_PREFERENCES, user_id)
        self._store.put(namespace, key, {
            "value": value,
            "updated_at": datetime.now().isoformat()
        })
        
    def get_user_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        """获取用户偏好"""
        namespace = (self.NS_USER_PREFERENCES, user_id)
        item = self._store.get(namespace, key)
        
        if item is None:
            return default
        
        return item.value.get("value", default)
    
    def get_all_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户的所有偏好"""
        namespace = (self.NS_USER_PREFERENCES, user_id)
        items = self._store.search(namespace, limit=100)
        return {item.key: item.value.get("value") for item in items}
    
    # ==================== 会话管理 ====================
    
    def delete_session(self, thread_id: str) -> None:
        """删除会话"""
        self._checkpointer_manager.delete_thread(thread_id)
        
    def list_sessions(self) -> List[str]:
        """列出所有会话"""
        return self._checkpointer_manager.list_threads()
    
    # ==================== 配置获取器 ====================
    
    def get_config_for_thread(
        self, 
        thread_id: str, 
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """获取线程配置（用于 LangGraph invoke/stream）"""
        return {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id
            }
        }
    
    # ==================== 清理 ====================
    
    def close(self) -> None:
        """关闭所有连接"""
        self._checkpointer_manager.close()
        self._store.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ==================== 全局实例管理 ====================

_memory_manager: Optional[MemoryManager] = None


def get_memory_manager(db_path: str = None) -> MemoryManager:
    """获取全局记忆管理器实例"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(db_path=db_path)
    return _memory_manager


def reset_memory_manager() -> None:
    """重置全局记忆管理器（主要用于测试）"""
    global _memory_manager
    if _memory_manager is not None:
        _memory_manager.close()
        _memory_manager = None
