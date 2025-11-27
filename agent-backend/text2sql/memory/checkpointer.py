"""
短期记忆管理器

基于SqliteSaver封装，提供会话上下文管理
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from langgraph.checkpoint.sqlite import SqliteSaver


class CheckpointerManager:
    """短期记忆管理器
    
    封装SqliteSaver，提供会话上下文的存储和检索
    """
    
    def __init__(self, db_path: str = "data/agent_memory.db"):
        """初始化检查点管理器
        
        Args:
            db_path: SQLite数据库文件路径
        """
        self.db_path = Path(db_path)
        self._checkpointer: Optional[SqliteSaver] = None
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
        return self._conn
    
    def get_checkpointer(self) -> SqliteSaver:
        """获取SqliteSaver实例（带缓存）
        
        Returns:
            初始化好的SqliteSaver实例
        """
        if self._checkpointer is None:
            conn = self._get_connection()
            self._checkpointer = SqliteSaver(conn)
            self._checkpointer.setup()
        return self._checkpointer
    
    def delete_thread(self, thread_id: str) -> None:
        """删除指定线程的所有检查点
        
        Args:
            thread_id: 线程ID
        """
        checkpointer = self.get_checkpointer()
        checkpointer.delete_thread(thread_id)
        
    def list_threads(self) -> list[str]:
        """列出所有线程ID
        
        Returns:
            线程ID列表
        """
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT DISTINCT thread_id FROM checkpoints"
        )
        return [row[0] for row in cursor.fetchall()]
    
    def close(self) -> None:
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._checkpointer = None


# 全局管理器实例
_manager: Optional[CheckpointerManager] = None


def get_checkpointer(db_path: str = "data/agent_memory.db") -> SqliteSaver:
    """获取全局的SqliteSaver实例
    
    Args:
        db_path: 数据库路径
        
    Returns:
        SqliteSaver实例
    """
    global _manager
    if _manager is None:
        _manager = CheckpointerManager(db_path)
    return _manager.get_checkpointer()


def get_manager() -> CheckpointerManager:
    """获取全局管理器实例"""
    global _manager
    if _manager is None:
        _manager = CheckpointerManager()
    return _manager


@contextmanager
def checkpointer_context(db_path: str = "data/agent_memory.db"):
    """上下文管理器，自动关闭连接
    
    Usage:
        with checkpointer_context() as checkpointer:
            # 使用checkpointer
            pass
    """
    manager = CheckpointerManager(db_path)
    try:
        yield manager.get_checkpointer()
    finally:
        manager.close()
