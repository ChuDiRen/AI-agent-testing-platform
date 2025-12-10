"""
记忆统一管理器

整合短期记忆(Checkpointer)和长期记忆(Store)的统一接口
参考: 
- https://docs.langchain.com/oss/python/langchain/short-term-memory
- https://docs.langchain.com/oss/python/langchain/long-term-memory
"""

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.base import BaseStore

from .checkpointer import CheckpointerManager
from .store import PersistentStore, MemoryItem


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
    
    def __init__(self, db_path: str = "data/agent_memory.db"):
        """初始化记忆管理器
        
        Args:
            db_path: 数据库文件路径（短期和长期记忆共用）
        """
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
        """缓存数据库 Schema 信息
        
        Args:
            connection_id: 数据库连接 ID
            schema_info: Schema 信息
            ttl_hours: 缓存有效期（小时）
        """
        namespace = (self.NS_SCHEMA_CACHE, str(connection_id))
        self._store.put(namespace, "schema", {
            "data": schema_info,
            "cached_at": datetime.now().isoformat(),
            "ttl_hours": ttl_hours
        })
        
    def get_cached_schema(
        self, 
        connection_id: int
    ) -> Optional[Dict[str, Any]]:
        """获取缓存的 Schema 信息
        
        Args:
            connection_id: 数据库连接 ID
            
        Returns:
            Schema 信息，如果不存在或过期返回 None
        """
        namespace = (self.NS_SCHEMA_CACHE, str(connection_id))
        item = self._store.get(namespace, "schema")
        
        if item is None:
            return None
        
        # 检查是否过期
        cached_at = item.value.get("cached_at")
        ttl_hours = item.value.get("ttl_hours", 24)
        
        if cached_at:
            from datetime import datetime, timedelta
            cached_time = datetime.fromisoformat(cached_at)
            if datetime.now() - cached_time > timedelta(hours=ttl_hours):
                # 缓存过期，删除并返回 None
                self._store.delete(namespace, "schema")
                return None
        
        return item.value.get("data")
    
    def invalidate_schema_cache(self, connection_id: int) -> None:
        """使 Schema 缓存失效
        
        Args:
            connection_id: 数据库连接 ID
        """
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
        """保存成功的查询模式
        
        Args:
            user_id: 用户 ID
            natural_query: 自然语言查询
            sql: 生成的 SQL
            schema_context: Schema 上下文
            success: 是否执行成功
            execution_time_ms: 执行时间
            
        Returns:
            模式 ID
        """
        # 生成模式 ID
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
        """获取相似的查询模式
        
        Args:
            user_id: 用户 ID
            query: 当前查询
            limit: 最大返回数量
            
        Returns:
            相似模式列表
        """
        namespace = (self.NS_QUERY_PATTERNS, user_id)
        items = self._store.search(
            namespace, 
            query=query, 
            limit=limit
        )
        
        return [
            {
                "pattern_id": item.key,
                **item.value
            }
            for item in items
        ]
    
    def increment_pattern_usage(self, user_id: str, pattern_id: str) -> None:
        """增加模式使用计数
        
        Args:
            user_id: 用户 ID
            pattern_id: 模式 ID
        """
        namespace = (self.NS_QUERY_PATTERNS, user_id)
        item = self._store.get(namespace, pattern_id)
        
        if item:
            value = item.value.copy()
            value["use_count"] = value.get("use_count", 0) + 1
            value["last_used_at"] = datetime.now().isoformat()
            self._store.put(namespace, pattern_id, value)
    
    # ==================== 成功查询历史 ====================
    
    def save_successful_query(
        self,
        connection_id: int,
        natural_query: str,
        sql: str,
        result_summary: Dict[str, Any]
    ) -> None:
        """保存成功执行的查询
        
        用于学习和优化
        
        Args:
            connection_id: 数据库连接 ID
            natural_query: 自然语言查询
            sql: SQL 语句
            result_summary: 结果摘要
        """
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
        """获取成功查询历史
        
        Args:
            connection_id: 数据库连接 ID
            limit: 最大返回数量
            
        Returns:
            查询历史列表
        """
        namespace = (self.NS_SUCCESSFUL_QUERIES, str(connection_id))
        items = self._store.search(namespace, limit=limit)
        
        return [item.value for item in items]
    
    # ==================== 用户偏好 ====================
    
    def save_user_preference(
        self, 
        user_id: str, 
        key: str, 
        value: Any
    ) -> None:
        """保存用户偏好
        
        Args:
            user_id: 用户 ID
            key: 偏好键
            value: 偏好值
        """
        namespace = (self.NS_USER_PREFERENCES, user_id)
        self._store.put(namespace, key, {
            "value": value,
            "updated_at": datetime.now().isoformat()
        })
        
    def get_user_preference(
        self, 
        user_id: str, 
        key: str,
        default: Any = None
    ) -> Any:
        """获取用户偏好
        
        Args:
            user_id: 用户 ID
            key: 偏好键
            default: 默认值
            
        Returns:
            偏好值
        """
        namespace = (self.NS_USER_PREFERENCES, user_id)
        item = self._store.get(namespace, key)
        
        if item is None:
            return default
        
        return item.value.get("value", default)
    
    def get_all_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户的所有偏好
        
        Args:
            user_id: 用户 ID
            
        Returns:
            偏好字典
        """
        namespace = (self.NS_USER_PREFERENCES, user_id)
        items = self._store.search(namespace, limit=100)
        
        return {
            item.key: item.value.get("value") 
            for item in items
        }
    
    # ==================== 会话管理 ====================
    
    def delete_session(self, thread_id: str) -> None:
        """删除会话
        
        Args:
            thread_id: 会话线程 ID
        """
        self._checkpointer_manager.delete_thread(thread_id)
        
    def list_sessions(self) -> List[str]:
        """列出所有会话
        
        Returns:
            会话线程 ID 列表
        """
        return self._checkpointer_manager.list_threads()
    
    # ==================== 配置获取器（用于 Tool） ====================
    
    def get_config_for_thread(
        self, 
        thread_id: str, 
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """获取线程配置
        
        用于传递给 LangGraph invoke/stream
        
        Args:
            thread_id: 会话线程 ID
            user_id: 用户 ID
            
        Returns:
            配置字典
        """
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


def get_memory_manager(db_path: str = "data/agent_memory.db") -> MemoryManager:
    """获取全局记忆管理器实例
    
    Args:
        db_path: 数据库路径
        
    Returns:
        MemoryManager 实例
    """
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
