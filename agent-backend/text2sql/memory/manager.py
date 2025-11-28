"""
记忆统一管理器

整合短期记忆和长期记忆的统一接口
"""

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.memory import InMemoryStore

from .checkpointer import CheckpointerManager
from .store import StoreManager, MemoryItem


class MemoryManager:
    """记忆统一管理器
    
    提供短期记忆和长期记忆的统一管理接口
    """
    
    def __init__(self, db_path: str = "data/agent_memory.db"):
        """初始化记忆管理器
        
        Args:
            db_path: 数据库文件路径（短期和长期记忆共用）
        """
        self.db_path = db_path
        self._checkpointer_manager = CheckpointerManager(db_path)
        self._store_manager = StoreManager(db_path)
        
    @property
    def checkpointer(self) -> SqliteSaver:
        """获取短期记忆（会话检查点）"""
        return self._checkpointer_manager.get_checkpointer()
    
    @property
    def store(self) -> InMemoryStore:
        """获取长期记忆（知识存储）"""
        return self._store_manager.get_store()
    
    # ==================== Schema缓存 ====================
    
    def cache_schema(self, connection_id: int, schema_info: Dict[str, Any]) -> None:
        """缓存数据库Schema信息
        
        Args:
            connection_id: 数据库连接ID
            schema_info: Schema信息
        """
        namespace = ("schema_cache", str(connection_id))
        self._store_manager.put(namespace, "schema", schema_info)
        
    def get_cached_schema(self, connection_id: int) -> Optional[Dict[str, Any]]:
        """获取缓存的Schema信息
        
        Args:
            connection_id: 数据库连接ID
            
        Returns:
            Schema信息，如果不存在返回None
        """
        namespace = ("schema_cache", str(connection_id))
        return self._store_manager.get(namespace, "schema")
    
    def invalidate_schema_cache(self, connection_id: int) -> None:
        """使Schema缓存失效
        
        Args:
            connection_id: 数据库连接ID
        """
        namespace = ("schema_cache", str(connection_id))
        self._store_manager.clear_namespace(namespace)
        
    # ==================== 查询模式 ====================
    
    def save_query_pattern(
        self, 
        user_id: str, 
        pattern_id: str, 
        pattern: Dict[str, Any]
    ) -> None:
        """保存查询模式
        
        Args:
            user_id: 用户ID
            pattern_id: 模式ID
            pattern: 模式信息（包含查询模板、参数等）
        """
        namespace = ("query_patterns", user_id)
        self._store_manager.put(namespace, pattern_id, pattern)
        
    def get_similar_patterns(
        self, 
        user_id: str, 
        query: str, 
        limit: int = 5
    ) -> List[MemoryItem]:
        """获取相似的查询模式
        
        Args:
            user_id: 用户ID
            query: 当前查询
            limit: 最大返回数量
            
        Returns:
            相似模式列表
        """
        namespace = ("query_patterns", user_id)
        return self._store_manager.search(namespace, query=query, limit=limit)
    
    # ==================== 用户偏好 ====================
    
    def save_user_preference(
        self, 
        user_id: str, 
        key: str, 
        value: Any
    ) -> None:
        """保存用户偏好
        
        Args:
            user_id: 用户ID
            key: 偏好键
            value: 偏好值
        """
        namespace = ("user_preferences", user_id)
        self._store_manager.put(namespace, key, {"value": value})
        
    def get_user_preference(self, user_id: str, key: str) -> Optional[Any]:
        """获取用户偏好
        
        Args:
            user_id: 用户ID
            key: 偏好键
            
        Returns:
            偏好值，如果不存在返回None
        """
        namespace = ("user_preferences", user_id)
        result = self._store_manager.get(namespace, key)
        return result.get("value") if result else None
    
    def get_all_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户的所有偏好
        
        Args:
            user_id: 用户ID
            
        Returns:
            偏好字典
        """
        namespace = ("user_preferences", user_id)
        items = self._store_manager.search(namespace, limit=100)
        return {item.key: item.value.get("value") for item in items}
    
    # ==================== 会话管理 ====================
    
    def delete_session(self, thread_id: str) -> None:
        """删除会话
        
        Args:
            thread_id: 会话线程ID
        """
        self._checkpointer_manager.delete_thread(thread_id)
        
    def list_sessions(self) -> List[str]:
        """列出所有会话
        
        Returns:
            会话线程ID列表
        """
        return self._checkpointer_manager.list_threads()
    
    # ==================== 清理 ====================
    
    def close(self) -> None:
        """关闭所有连接"""
        self._checkpointer_manager.close()
        self._store_manager.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 全局管理器实例
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager(db_path: str = "data/agent_memory.db") -> MemoryManager:
    """获取全局记忆管理器实例
    
    Args:
        db_path: 数据库路径
        
    Returns:
        MemoryManager实例
    """
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(db_path)
    return _memory_manager
