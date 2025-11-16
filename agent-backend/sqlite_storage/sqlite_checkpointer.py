"""
SQLite Checkpointer Implementation for LangGraph

这个模块实现了基于SQLite的checkpointer，用于存储线程状态和对话历史。
可以通过langgraph.yaml配置文件来使用此checkpointer。
"""

import json
import sqlite3
from contextlib import contextmanager, asynccontextmanager
from typing import Any, Iterator, Optional, Sequence

import aiosqlite
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
)
from langgraph.checkpoint.serde.base import SerializerProtocol


class SqliteCheckpointer(BaseCheckpointSaver):
    """
    基于SQLite的Checkpointer实现
    
    用于存储和检索线程的checkpoint数据，包括：
    - 线程状态
    - 对话历史
    - 元数据
    
    使用方法：
        在langgraph.yaml中配置：
        checkpointer:
          path: ./examples/sqlite_storage/sqlite_checkpointer.py:create_checkpointer
    """

    def __init__(
        self,
        db_path: str = "langgraph.db",
        serde: Optional[SerializerProtocol] = None,
    ):
        """
        初始化SQLite Checkpointer
        
        Args:
            db_path: SQLite数据库文件路径（统一数据库）
            serde: 序列化器，用于序列化/反序列化checkpoint数据
        """
        super().__init__(serde=serde)
        self.db_path = db_path
        self._setup_database()
        
        # 自动初始化SqliteStore，确保store_items表被创建（用于长期记忆）
        self._init_store()

    def _setup_database(self):
        """创建必要的数据库表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建checkpoints表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    thread_id TEXT NOT NULL,
                    checkpoint_ns TEXT NOT NULL DEFAULT '',
                    checkpoint_id TEXT NOT NULL,
                    parent_checkpoint_id TEXT,
                    type TEXT,
                    checkpoint BLOB NOT NULL,
                    metadata BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
                )
            """)
            
            # 创建writes表（用于存储pending writes）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkpoint_writes (
                    thread_id TEXT NOT NULL,
                    checkpoint_ns TEXT NOT NULL DEFAULT '',
                    checkpoint_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    idx INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    type TEXT,
                    value BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
                )
            """)
            
            # 创建对话消息表（用于存储完整的对话内容）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT NOT NULL,
                    checkpoint_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引以提高查询性能
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id 
                ON checkpoints(thread_id, checkpoint_ns, checkpoint_id DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_checkpoint_writes_thread_id 
                ON checkpoint_writes(thread_id, checkpoint_ns, checkpoint_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_messages_thread_id 
                ON conversation_messages(thread_id, checkpoint_id, created_at)
            """)
            
            conn.commit()
    
    def _init_store(self):
        """初始化Store表（用于长期记忆）"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建store_items表（用于长期记忆存储）
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

    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        """
        获取指定配置的checkpoint
        
        Args:
            config: 包含thread_id和checkpoint_id的配置字典
            
        Returns:
            CheckpointTuple或None
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if checkpoint_id:
                # 获取特定的checkpoint
                cursor.execute(
                    """
                    SELECT thread_id, checkpoint_id, parent_checkpoint_id, 
                           type, checkpoint, metadata
                    FROM checkpoints
                    WHERE thread_id = ? AND checkpoint_ns = ? AND checkpoint_id = ?
                    """,
                    (thread_id, checkpoint_ns, checkpoint_id),
                )
            else:
                # 获取最新的checkpoint
                cursor.execute(
                    """
                    SELECT thread_id, checkpoint_id, parent_checkpoint_id, 
                           type, checkpoint, metadata
                    FROM checkpoints
                    WHERE thread_id = ? AND checkpoint_ns = ?
                    ORDER BY checkpoint_id DESC
                    LIMIT 1
                    """,
                    (thread_id, checkpoint_ns),
                )
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # 反序列化checkpoint和metadata
            checkpoint = self.serde.loads_typed((row["type"], row["checkpoint"]))
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}
            
            # 获取pending writes
            cursor.execute(
                """
                SELECT task_id, channel, type, value
                FROM checkpoint_writes
                WHERE thread_id = ? AND checkpoint_ns = ? AND checkpoint_id = ?
                ORDER BY task_id, idx
                """,
                (thread_id, checkpoint_ns, row["checkpoint_id"]),
            )
            
            pending_writes = []
            for write_row in cursor.fetchall():
                pending_writes.append(
                    (
                        write_row["task_id"],
                        write_row["channel"],
                        self.serde.loads_typed((write_row["type"], write_row["value"])),
                    )
                )
            
            # 构建配置
            checkpoint_config = {
                "configurable": {
                    "thread_id": row["thread_id"],
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": row["checkpoint_id"],
                }
            }
            
            parent_config = None
            if row["parent_checkpoint_id"]:
                parent_config = {
                    "configurable": {
                        "thread_id": row["thread_id"],
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": row["parent_checkpoint_id"],
                    }
                }
            
            return CheckpointTuple(
                config=checkpoint_config,
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=parent_config,
                pending_writes=pending_writes,
            )

    def list(
        self,
        config: Optional[dict] = None,
        *,
        filter: Optional[dict] = None,
        before: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        """
        列出checkpoints
        
        Args:
            config: 配置字典，包含thread_id
            filter: 过滤条件
            before: 在此checkpoint之前的checkpoints
            limit: 返回的最大数量
            
        Yields:
            CheckpointTuple迭代器
        """
        thread_id = config["configurable"]["thread_id"] if config else None
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "") if config else ""
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT thread_id, checkpoint_id, parent_checkpoint_id, 
                       type, checkpoint, metadata
                FROM checkpoints
                WHERE 1=1
            """
            params = []
            
            if thread_id:
                query += " AND thread_id = ?"
                params.append(thread_id)
            
            if checkpoint_ns:
                query += " AND checkpoint_ns = ?"
                params.append(checkpoint_ns)
            
            if before:
                query += " AND checkpoint_id < ?"
                params.append(get_checkpoint_id(before))
            
            query += " ORDER BY checkpoint_id DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                checkpoint = self.serde.loads_typed((row["type"], row["checkpoint"]))
                metadata = json.loads(row["metadata"]) if row["metadata"] else {}
                
                checkpoint_config = {
                    "configurable": {
                        "thread_id": row["thread_id"],
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": row["checkpoint_id"],
                    }
                }
                
                parent_config = None
                if row["parent_checkpoint_id"]:
                    parent_config = {
                        "configurable": {
                            "thread_id": row["thread_id"],
                            "checkpoint_ns": checkpoint_ns,
                            "checkpoint_id": row["parent_checkpoint_id"],
                        }
                    }
                
                yield CheckpointTuple(
                    config=checkpoint_config,
                    checkpoint=checkpoint,
                    metadata=metadata,
                    parent_config=parent_config,
                )

    def put(
        self,
        config: dict,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict,
    ) -> dict:
        """
        保存checkpoint
        
        Args:
            config: 配置字典
            checkpoint: checkpoint数据
            metadata: 元数据
            new_versions: 新版本信息
            
        Returns:
            更新后的配置字典
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        
        type_, serialized_checkpoint = self.serde.dumps_typed(checkpoint)
        serialized_metadata = json.dumps(metadata, ensure_ascii=False).encode("utf-8")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取parent checkpoint id
            parent_checkpoint_id = config["configurable"].get("checkpoint_id")
            
            # 插入或更新checkpoint
            cursor.execute(
                """
                INSERT OR REPLACE INTO checkpoints 
                (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, 
                 type, checkpoint, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    thread_id,
                    checkpoint_ns,
                    checkpoint_id,
                    parent_checkpoint_id,
                    type_,
                    serialized_checkpoint,
                    serialized_metadata,
                ),
            )
            
            # 保存完整的对话消息内容
            self.save_conversation_messages(cursor, thread_id, checkpoint_id, checkpoint)
            
            conn.commit()
        
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }
    
    def save_conversation_messages(self, cursor, thread_id: str, checkpoint_id: str, checkpoint: Checkpoint):
        """
        保存完整的对话消息内容到独立表
        
        Args:
            cursor: 数据库游标
            thread_id: 线程ID
            checkpoint_id: checkpoint ID
            checkpoint: checkpoint数据
        """
        # 从checkpoint中提取消息
        channel_values = checkpoint.get("channel_values", {})
        messages = channel_values.get("messages", [])
        
        if not messages:
            return
        
        # 只保存最新的消息（避免重复保存）
        # 获取已保存的消息数量
        cursor.execute(
            "SELECT COUNT(*) as count FROM conversation_messages WHERE thread_id = ?",
            (thread_id,)
        )
        existing_count = cursor.fetchone()["count"]
        
        # 只保存新增的消息
        new_messages = messages[existing_count:]
        
        for msg in new_messages:
            # 提取消息信息
            message_type = msg.__class__.__name__
            
            # 确定角色
            if hasattr(msg, 'type'):
                role = msg.type
            elif 'Human' in message_type:
                role = 'user'
            elif 'AI' in message_type:
                role = 'assistant'
            elif 'System' in message_type:
                role = 'system'
            else:
                role = 'unknown'
            
            # 提取内容
            content = msg.content if hasattr(msg, 'content') else str(msg)
            
            # 提取元数据
            msg_metadata = {}
            if hasattr(msg, 'additional_kwargs'):
                msg_metadata['additional_kwargs'] = msg.additional_kwargs
            if hasattr(msg, 'response_metadata'):
                msg_metadata['response_metadata'] = msg.response_metadata
            if hasattr(msg, 'id'):
                msg_metadata['id'] = msg.id
            if hasattr(msg, 'name'):
                msg_metadata['name'] = msg.name
            
            metadata_json = json.dumps(msg_metadata, ensure_ascii=False) if msg_metadata else None
            
            # 插入消息
            cursor.execute(
                """
                INSERT INTO conversation_messages 
                (thread_id, checkpoint_id, message_type, role, content, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (thread_id, checkpoint_id, message_type, role, content, metadata_json)
            )
    
    async def _asave_conversation_messages(self, cursor, thread_id: str, checkpoint_id: str, checkpoint: Checkpoint):
        """
        异步保存完整的对话消息内容到独立表
        
        Args:
            cursor: 异步数据库游标
            thread_id: 线程ID
            checkpoint_id: checkpoint ID
            checkpoint: checkpoint数据
        """
        # 从checkpoint中提取消息
        channel_values = checkpoint.get("channel_values", {})
        messages = channel_values.get("messages", [])
        
        if not messages:
            return
        
        # 只保存最新的消息（避免重复保存）
        # 获取已保存的消息数量
        await cursor.execute(
            "SELECT COUNT(*) as count FROM conversation_messages WHERE thread_id = ?",
            (thread_id,)
        )
        row = await cursor.fetchone()
        existing_count = row["count"]
        
        # 只保存新增的消息
        new_messages = messages[existing_count:]
        
        for msg in new_messages:
            # 提取消息信息
            message_type = msg.__class__.__name__
            
            # 确定角色
            if hasattr(msg, 'type'):
                role = msg.type
            elif 'Human' in message_type:
                role = 'user'
            elif 'AI' in message_type:
                role = 'assistant'
            elif 'System' in message_type:
                role = 'system'
            else:
                role = 'unknown'
            
            # 提取内容
            content = msg.content if hasattr(msg, 'content') else str(msg)
            
            # 提取元数据
            msg_metadata = {}
            if hasattr(msg, 'additional_kwargs'):
                msg_metadata['additional_kwargs'] = msg.additional_kwargs
            if hasattr(msg, 'response_metadata'):
                msg_metadata['response_metadata'] = msg.response_metadata
            if hasattr(msg, 'id'):
                msg_metadata['id'] = msg.id
            if hasattr(msg, 'name'):
                msg_metadata['name'] = msg.name
            
            metadata_json = json.dumps(msg_metadata, ensure_ascii=False) if msg_metadata else None
            
            # 插入消息
            await cursor.execute(
                """
                INSERT INTO conversation_messages 
                (thread_id, checkpoint_id, message_type, role, content, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (thread_id, checkpoint_id, message_type, role, content, metadata_json)
            )

    def put_writes(
        self,
        config: dict,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
    ) -> None:
        """
        保存pending writes
        
        Args:
            config: 配置字典
            writes: 写入操作列表
            task_id: 任务ID
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for idx, (channel, value) in enumerate(writes):
                type_, serialized_value = self.serde.dumps_typed(value)
                
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO checkpoint_writes
                    (thread_id, checkpoint_ns, checkpoint_id, task_id, idx, 
                     channel, type, value)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        thread_id,
                        checkpoint_ns,
                        checkpoint_id,
                        task_id,
                        idx,
                        channel,
                        type_,
                        serialized_value,
                    ),
                )
            
            conn.commit()

    # ==================== 异步方法实现 ====================
    # 以下方法是对应同步方法的异步版本，使用 aiosqlite 实现真正的异步操作
    
    async def aget_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        """
        异步获取指定配置的checkpoint
        
        Args:
            config: 包含thread_id和checkpoint_id的配置字典
            
        Returns:
            CheckpointTuple或None
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)
        
        async with self._get_async_connection() as conn:
            cursor = await conn.cursor()
            
            if checkpoint_id:
                # 获取特定的checkpoint
                await cursor.execute(
                    """
                    SELECT thread_id, checkpoint_id, parent_checkpoint_id, 
                           type, checkpoint, metadata
                    FROM checkpoints
                    WHERE thread_id = ? AND checkpoint_ns = ? AND checkpoint_id = ?
                    """,
                    (thread_id, checkpoint_ns, checkpoint_id),
                )
            else:
                # 获取最新的checkpoint
                await cursor.execute(
                    """
                    SELECT thread_id, checkpoint_id, parent_checkpoint_id, 
                           type, checkpoint, metadata
                    FROM checkpoints
                    WHERE thread_id = ? AND checkpoint_ns = ?
                    ORDER BY checkpoint_id DESC
                    LIMIT 1
                    """,
                    (thread_id, checkpoint_ns),
                )
            
            row = await cursor.fetchone()
            if not row:
                return None
            
            # 反序列化checkpoint和metadata
            checkpoint = self.serde.loads_typed((row["type"], row["checkpoint"]))
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}
            
            # 获取pending writes
            await cursor.execute(
                """
                SELECT task_id, channel, type, value
                FROM checkpoint_writes
                WHERE thread_id = ? AND checkpoint_ns = ? AND checkpoint_id = ?
                ORDER BY task_id, idx
                """,
                (thread_id, checkpoint_ns, row["checkpoint_id"]),
            )
            
            pending_writes = []
            async for write_row in cursor:
                pending_writes.append(
                    (
                        write_row["task_id"],
                        write_row["channel"],
                        self.serde.loads_typed((write_row["type"], write_row["value"])),
                    )
                )
            
            # 构建配置
            checkpoint_config = {
                "configurable": {
                    "thread_id": row["thread_id"],
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": row["checkpoint_id"],
                }
            }
            
            parent_config = None
            if row["parent_checkpoint_id"]:
                parent_config = {
                    "configurable": {
                        "thread_id": row["thread_id"],
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": row["parent_checkpoint_id"],
                    }
                }
            
            return CheckpointTuple(
                config=checkpoint_config,
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=parent_config,
                pending_writes=pending_writes,
            )
    
    async def alist(
        self,
        config: Optional[dict] = None,
        *,
        filter: Optional[dict] = None,
        before: Optional[dict] = None,
        limit: Optional[int] = None,
    ):
        """
        异步列出checkpoints
        
        Args:
            config: 配置字典，包含thread_id
            filter: 过滤条件
            before: 在此checkpoint之前的checkpoints
            limit: 返回的最大数量
            
        Yields:
            CheckpointTuple迭代器
        """
        thread_id = config["configurable"]["thread_id"] if config else None
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "") if config else ""
        
        async with self._get_async_connection() as conn:
            cursor = await conn.cursor()
            
            query = """
                SELECT thread_id, checkpoint_id, parent_checkpoint_id, 
                       type, checkpoint, metadata
                FROM checkpoints
                WHERE 1=1
            """
            params = []
            
            if thread_id:
                query += " AND thread_id = ?"
                params.append(thread_id)
            
            if checkpoint_ns:
                query += " AND checkpoint_ns = ?"
                params.append(checkpoint_ns)
            
            if before:
                query += " AND checkpoint_id < ?"
                params.append(get_checkpoint_id(before))
            
            query += " ORDER BY checkpoint_id DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            await cursor.execute(query, params)
            
            async for row in cursor:
                checkpoint = self.serde.loads_typed((row["type"], row["checkpoint"]))
                metadata = json.loads(row["metadata"]) if row["metadata"] else {}
                
                checkpoint_config = {
                    "configurable": {
                        "thread_id": row["thread_id"],
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": row["checkpoint_id"],
                    }
                }
                
                parent_config = None
                if row["parent_checkpoint_id"]:
                    parent_config = {
                        "configurable": {
                            "thread_id": row["thread_id"],
                            "checkpoint_ns": checkpoint_ns,
                            "checkpoint_id": row["parent_checkpoint_id"],
                        }
                    }
                
                yield CheckpointTuple(
                    config=checkpoint_config,
                    checkpoint=checkpoint,
                    metadata=metadata,
                    parent_config=parent_config,
                )
    
    async def aput(
        self,
        config: dict,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict,
    ) -> dict:
        """
        异步保存checkpoint
        
        Args:
            config: 配置字典
            checkpoint: checkpoint数据
            metadata: 元数据
            new_versions: 新版本信息
            
        Returns:
            更新后的配置字典
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        
        type_, serialized_checkpoint = self.serde.dumps_typed(checkpoint)
        serialized_metadata = json.dumps(metadata, ensure_ascii=False).encode("utf-8")
        
        async with self._get_async_connection() as conn:
            cursor = await conn.cursor()
            
            # 获取parent checkpoint id
            parent_checkpoint_id = config["configurable"].get("checkpoint_id")
            
            # 插入或更新checkpoint
            await cursor.execute(
                """
                INSERT OR REPLACE INTO checkpoints 
                (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, 
                 type, checkpoint, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    thread_id,
                    checkpoint_ns,
                    checkpoint_id,
                    parent_checkpoint_id,
                    type_,
                    serialized_checkpoint,
                    serialized_metadata,
                ),
            )
            
            # 保存完整的对话消息内容
            await self._asave_conversation_messages(cursor, thread_id, checkpoint_id, checkpoint)
            
            await conn.commit()
        
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }
    
    async def aput_writes(
        self,
        config: dict,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
    ) -> None:
        """
        异步保存pending writes
        
        Args:
            config: 配置字典
            writes: 写入操作列表
            task_id: 任务ID
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)
        
        async with self._get_async_connection() as conn:
            cursor = await conn.cursor()
            
            for idx, (channel, value) in enumerate(writes):
                type_, serialized_value = self.serde.dumps_typed(value)
                
                await cursor.execute(
                    """
                    INSERT OR REPLACE INTO checkpoint_writes
                    (thread_id, checkpoint_ns, checkpoint_id, task_id, idx, 
                     channel, type, value)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        thread_id,
                        checkpoint_ns,
                        checkpoint_id,
                        task_id,
                        idx,
                        channel,
                        type_,
                        serialized_value,
                    ),
                )
            
            await conn.commit()
    
    # 异步方法已按照 LangGraph 标准命名为 aput/aput_writes


def create_checkpointer() -> SqliteCheckpointer:
    """
    工厂函数：创建 SQLite checkpointer 实例。
    与 SqliteStore 使用相同的数据库位置：sqlite_storage/data/langgraph_server.db
    """
    from pathlib import Path

    db_dir = Path(__file__).parent / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "langgraph_server.db"

    print(f"[Checkpointer] 使用数据库: {db_path}")
    return SqliteCheckpointer(db_path=str(db_path))
