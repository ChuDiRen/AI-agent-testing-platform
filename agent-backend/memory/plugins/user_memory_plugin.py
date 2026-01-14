# memory/plugins/user_memory_plugin.py
import json
import aiosqlite
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from memory.plugins.base import MemoryPlugin, PluginState

class UserMemoryPlugin(MemoryPlugin):
    """用户记忆插件 - 管理用户画像和语义记忆"""

    name = "user_memory"
    version = "1.0.0"
    description = "用户记忆管理，支持用户画像、偏好和事实记忆"

    async def setup(self) -> None:
        """初始化用户记忆表"""
        self._conn = await aiosqlite.connect(
            self.db_path, check_same_thread=False
        )
        self._conn.row_factory = aiosqlite.Row

        # 用户画像表
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                preferences TEXT DEFAULT '{}',
                context TEXT DEFAULT '{}',
                interaction_count INTEGER DEFAULT 0,
                last_interaction TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 语义记忆表
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS user_memories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                importance REAL DEFAULT 0.5,
                metadata TEXT DEFAULT '{}',
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
            )
        """)

        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_um_user ON user_memories(user_id)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_um_category ON user_memories(category)"
        )

        await self._conn.commit()
        self._state = PluginState.ENABLED

    async def teardown(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None
        self._state = PluginState.DISABLED

    # 用户画像操作
    async def get_or_create_profile(self, user_id: str) -> Dict[str, Any]:
        """获取或创建用户画像"""
        cursor = await self._conn.execute(
            "SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()

        if row:
            return dict(row)

        await self._conn.execute(
            "INSERT INTO user_profiles (user_id) VALUES (?)", (user_id,)
        )
        await self._conn.commit()
        return {"user_id": user_id, "preferences": "{}", "context": "{}"}

    async def update_profile(self, user_id: str, **kwargs) -> None:
        """更新用户画像"""
        fields = []
        values = []
        for k, v in kwargs.items():
            if k in ("name", "preferences", "context"):
                fields.append(f"{k} = ?")
                values.append(v if isinstance(v, str) else json.dumps(v))

        if fields:
            values.extend([user_id])
            await self._conn.execute(
                f"UPDATE user_profiles SET {', '.join(fields)}, "
                f"updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                values
            )
            await self._conn.commit()

    # 记忆操作
    async def remember(self, user_id: str, content: str,
                       category: str = "general", importance: float = 0.5) -> str:
        """记住一个事实"""
        memory_id = hashlib.md5(
            f"{user_id}:{content}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        await self._conn.execute("""
            INSERT INTO user_memories (id, user_id, content, category, importance)
            VALUES (?, ?, ?, ?, ?)
        """, (memory_id, user_id, content, category, importance))
        await self._conn.commit()

        return memory_id

    async def recall(self, user_id: str, query: Optional[str] = None,
                     category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """回忆相关记忆"""
        sql = "SELECT * FROM user_memories WHERE user_id = ?"
        params = [user_id]

        if category:
            sql += " AND category = ?"
            params.append(category)

        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")

        sql += " ORDER BY importance DESC, last_accessed DESC LIMIT ?"
        params.append(limit)

        cursor = await self._conn.execute(sql, params)
        rows = await cursor.fetchall()

        # 更新访问计数
        for row in rows:
            await self._conn.execute("""
                UPDATE user_memories
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (row["id"],))
        await self._conn.commit()

        return [dict(r) for r in rows]

    async def forget(self, memory_id: str) -> None:
        """删除记忆"""
        await self._conn.execute(
            "DELETE FROM user_memories WHERE id = ?", (memory_id,)
        )
        await self._conn.commit()

    async def health_check(self) -> Dict[str, Any]:
        cursor = await self._conn.execute(
            "SELECT COUNT(*) as users FROM user_profiles"
        )
        users = (await cursor.fetchone())["users"]

        cursor = await self._conn.execute(
            "SELECT COUNT(*) as memories FROM user_memories"
        )
        memories = (await cursor.fetchone())["memories"]

        return {
            "status": "healthy",
            "plugin": self.name,
            "users_count": users,
            "memories_count": memories,
            "state": self._state.value
        }