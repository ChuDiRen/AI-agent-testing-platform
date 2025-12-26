"""
短期记忆管理器

基于 SqliteSaver 封装，提供会话上下文管理
"""

import sqlite3
from pathlib import Path
from typing import Optional, List
from contextlib import contextmanager

from langgraph.checkpoint.sqlite import SqliteSaver


class CheckpointerManager:
    """短期记忆管理器

    封装 SqliteSaver，提供会话上下文的存储和检索
    """

    # 统一数据目录
    DATA_DIR = Path(__file__).parent.parent.resolve() / "data"

    def __init__(self, db_path: str = None):
        """初始化检查点管理器

        Args:
            db_path: SQLite 数据库文件路径，默认为 DATA_DIR/agent_memory.db
        """
        if db_path is None:
            db_path = str(self.DATA_DIR / "agent_memory.db")
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
        """获取 SqliteSaver 实例（带缓存）
        
        Returns:
            初始化好的 SqliteSaver 实例
        """
        if self._checkpointer is None:
            conn = self._get_connection()
            self._checkpointer = SqliteSaver(conn)
            self._checkpointer.setup()
        return self._checkpointer
    
    def delete_thread(self, thread_id: str) -> None:
        """删除指定线程的所有检查点
        
        Args:
            thread_id: 线程 ID
        """
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
            conn.commit()
        except sqlite3.OperationalError:
            pass  # 表可能不存在
        
    def list_threads(self) -> List[str]:
        """列出所有线程 ID
        
        Returns:
            线程 ID 列表
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT DISTINCT thread_id FROM checkpoints"
            )
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            return []
    
    def close(self) -> None:
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._checkpointer = None


@contextmanager
def checkpointer_context(db_path: str = None):
    """上下文管理器，自动关闭连接

    Usage:
        with checkpointer_context() as checkpointer:
            # 使用 checkpointer
            pass

    Args:
        db_path: SQLite 数据库文件路径，默认为 DATA_DIR/agent_memory.db
    """
    manager = CheckpointerManager(db_path)
    try:
        yield manager.get_checkpointer()
    finally:
        manager.close()


# ==================== LangGraph API 工厂函数 ====================

_checkpointer_manager: Optional[CheckpointerManager] = None


def get_checkpointer() -> SqliteSaver:
    """获取 Checkpointer 单例实例 - 供 LangGraph API 使用
    
    在 langgraph.json 中配置:
        "checkpointer": {
            "path": "./memory/checkpointer.py:get_checkpointer"
        }
    """
    global _checkpointer_manager
    if _checkpointer_manager is None:
        from pathlib import Path
        db_path = Path(__file__).parent.parent / "data" / "agent_memory.db"
        _checkpointer_manager = CheckpointerManager(str(db_path))
    return _checkpointer_manager.get_checkpointer()
