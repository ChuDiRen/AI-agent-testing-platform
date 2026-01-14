# 记忆插件系统设计方案 v2.0

> **核心原则**: 全部使用 SQLite 数据库持久化，禁止内存/文件存储，插件式可插拔设计

## 1. 概述

### 1.1 设计目标
- **全 SQLite 持久化**: 短期记忆、长期记忆全部存入 SQLite 数据库
- **禁止内存/文件存储**: 不使用 InMemoryStore、不使用文件系统存储
- **插件式架构**: 记忆模块可独立启用/禁用，支持热插拔
- **兼容 langgraph dev**: 完全兼容 `langgraph dev` 启动方式
- **单一数据源**: 所有记忆数据统一存储在 `agent_memory.db`

### 1.2 参考文档
- [LangGraph Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [LangGraph Memory Store](https://langchain-ai.github.io/langgraph/concepts/memory/)

---

## 2. 主逻辑流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           langgraph dev 启动流程                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. 读取 langgraph.json 配置                                                 │
│     ├── checkpointer.path → "./memory/checkpointer.py:get_checkpointer"     │
│     └── store.path → "./memory/store.py:get_store"                          │
│                                                                              │
│  2. 调用工厂函数初始化                                                        │
│     ├── get_checkpointer() → AsyncSqliteSaver(SQLite)                       │
│     └── get_store() → PersistentStore(SQLite)                               │
│                                                                              │
│  3. 编译 Graph 时自动注入                                                     │
│     graph.compile(checkpointer=checkpointer, store=store)                   │
│                                                                              │
│  4. 运行时自动管理                                                            │
│     ├── 每次 invoke/stream 自动保存 checkpoint                              │
│     └── 节点内可通过 config 访问 store                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           记忆插件架构                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    MemoryPluginManager (插件管理器)                      │ │
│  │  - register_plugin(plugin): 注册插件                                    │ │
│  │  - unregister_plugin(name): 注销插件                                    │ │
│  │  - get_plugin(name): 获取插件                                           │ │
│  │  - list_plugins(): 列出所有插件                                         │ │
│  │  - enable_plugin(name): 启用插件                                        │ │
│  │  - disable_plugin(name): 禁用插件                                       │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                               │                                              │
│            ┌──────────────────┼──────────────────┐                          │
│            ▼                  ▼                  ▼                          │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐            │
│  │ CheckpointerPlugin│ │  StorePlugin     │ │ UserMemoryPlugin │            │
│  │ (短期记忆插件)     │ │ (长期记忆插件)   │ │ (用户记忆插件)   │            │
│  │                  │ │                  │ │                  │            │
│  │ - SQLite存储     │ │ - SQLite存储     │ │ - SQLite存储     │            │
│  │ - thread_id隔离  │ │ - namespace隔离  │ │ - user_id隔离    │            │
│  │ - 状态检查点     │ │ - KV存储         │ │ - 语义记忆       │            │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘            │
│            │                  │                  │                          │
│            └──────────────────┼──────────────────┘                          │
│                               ▼                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    SQLite Database (agent_memory.db)                    │ │
│  │  ┌──────────────┬──────────────┬──────────────┬──────────────────────┐  │ │
│  │  │ checkpoints  │   writes     │long_term_mem │  user_memories       │  │ │
│  │  │   (短期)     │   (状态)     │   (长期)     │    (用户)            │  │ │
│  │  └──────────────┴──────────────┴──────────────┴──────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 插件接口设计

### 3.1 基础插件接口

```python
# memory/plugins/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum

class PluginState(Enum):
    """插件状态"""
    DISABLED = "disabled"      # 已禁用
    ENABLED = "enabled"        # 已启用
    INITIALIZING = "init"      # 初始化中
    ERROR = "error"            # 错误状态

class MemoryPlugin(ABC):
    """记忆插件基类 - 所有记忆插件必须继承此类"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._state = PluginState.DISABLED
        self._conn = None

    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称 (唯一标识)"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass

    @property
    def state(self) -> PluginState:
        """插件状态"""
        return self._state

    @abstractmethod
    async def setup(self) -> None:
        """初始化插件 (创建表、索引等)"""
        pass

    @abstractmethod
    async def teardown(self) -> None:
        """清理插件资源"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        pass

    async def enable(self) -> None:
        """启用插件"""
        await self.setup()
        self._state = PluginState.ENABLED

    async def disable(self) -> None:
        """禁用插件"""
        await self.teardown()
        self._state = PluginState.DISABLED
```

### 3.2 插件管理器

```python
# memory/plugins/manager.py
from typing import Dict, List, Optional, Type
from .base import MemoryPlugin, PluginState

class MemoryPluginManager:
    """记忆插件管理器 - 单例模式"""

    _instance: Optional["MemoryPluginManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: str):
        if hasattr(self, "_initialized"):
            return
        self.db_path = db_path
        self._plugins: Dict[str, MemoryPlugin] = {}
        self._initialized = True

    def register(self, plugin_class: Type[MemoryPlugin]) -> None:
        """注册插件类"""
        plugin = plugin_class(self.db_path)
        self._plugins[plugin.name] = plugin

    def unregister(self, name: str) -> None:
        """注销插件"""
        if name in self._plugins:
            del self._plugins[name]

    def get(self, name: str) -> Optional[MemoryPlugin]:
        """获取插件实例"""
        return self._plugins.get(name)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """列出所有插件"""
        return [
            {
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "state": p.state.value
            }
            for p in self._plugins.values()
        ]

    async def enable_plugin(self, name: str) -> bool:
        """启用指定插件"""
        plugin = self._plugins.get(name)
        if plugin:
            await plugin.enable()
            return True
        return False

    async def disable_plugin(self, name: str) -> bool:
        """禁用指定插件"""
        plugin = self._plugins.get(name)
        if plugin:
            await plugin.disable()
            return True
        return False

    async def enable_all(self) -> None:
        """启用所有插件"""
        for plugin in self._plugins.values():
            await plugin.enable()

    async def disable_all(self) -> None:
        """禁用所有插件"""
        for plugin in self._plugins.values():
            await plugin.disable()
```

---

## 4. 核心插件实现

### 4.1 短期记忆插件 (CheckpointerPlugin)

```python
# memory/plugins/checkpointer_plugin.py
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from .base import MemoryPlugin, PluginState

class CheckpointerPlugin(MemoryPlugin):
    """短期记忆插件 - 基于 AsyncSqliteSaver"""

    name = "checkpointer"
    version = "1.0.0"
    description = "会话状态检查点管理，支持对话历史和状态回溯"

    def __init__(self, db_path: str):
        super().__init__(db_path)
        self._checkpointer: Optional[AsyncSqliteSaver] = None

    async def setup(self) -> None:
        """初始化检查点表"""
        self._conn = await aiosqlite.connect(self.db_path, check_same_thread=False)
        self._checkpointer = AsyncSqliteSaver(self._conn)
        await self._checkpointer.setup()  # 创建 checkpoints, writes 表
        self._state = PluginState.ENABLED

    async def teardown(self) -> None:
        """关闭连接"""
        if self._conn:
            await self._conn.close()
            self._conn = None
        self._checkpointer = None
        self._state = PluginState.DISABLED

    async def get_saver(self) -> AsyncSqliteSaver:
        """获取 AsyncSqliteSaver 实例"""
        if self._checkpointer is None:
            await self.setup()
        return self._checkpointer

    async def delete_thread(self, thread_id: str) -> None:
        """删除指定线程的所有检查点"""
        if self._conn:
            await self._conn.execute(
                "DELETE FROM checkpoints WHERE thread_id = ?",
                (thread_id,)
            )
            await self._conn.commit()

    async def list_threads(self) -> List[str]:
        """列出所有线程ID"""
        if self._conn:
            cursor = await self._conn.execute(
                "SELECT DISTINCT thread_id FROM checkpoints"
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
        return []

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            threads = await self.list_threads()
            return {
                "status": "healthy",
                "plugin": self.name,
                "threads_count": len(threads),
                "state": self._state.value
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
```

### 4.2 长期记忆插件 (StorePlugin)

```python
# memory/plugins/store_plugin.py
import json
import aiosqlite
from typing import Tuple, List, Optional, Dict, Any
from langgraph.store.base import BaseStore, Item, SearchItem
from .base import MemoryPlugin, PluginState

class StorePlugin(MemoryPlugin, BaseStore):
    """长期记忆插件 - 实现 BaseStore 接口"""

    name = "store"
    version = "1.0.0"
    description = "长期知识存储，支持 namespace/key 结构化存储"

    async def setup(self) -> None:
        """初始化存储表"""
        self._conn = await aiosqlite.connect(
            self.db_path, check_same_thread=False
        )
        self._conn.row_factory = aiosqlite.Row

        await self._conn.execute("""
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

        await self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_ltm_namespace
            ON long_term_memory(namespace)
        """)

        await self._conn.commit()
        self._state = PluginState.ENABLED

    async def teardown(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None
        self._state = PluginState.DISABLED

    # BaseStore 接口实现
    async def put(self, namespace: Tuple[str, ...], key: str,
                  value: Dict[str, Any], index: Optional[bool] = None) -> None:
        """存储数据"""
        ns_str = "/".join(namespace)
        val_str = json.dumps(value, ensure_ascii=False, default=str)

        await self._conn.execute("""
            INSERT INTO long_term_memory (id, namespace, key, value, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(namespace, key) DO UPDATE SET
                value = excluded.value, updated_at = CURRENT_TIMESTAMP
        """, (f"{ns_str}:{key}", ns_str, key, val_str))
        await self._conn.commit()

    async def get(self, namespace: Tuple[str, ...], key: str) -> Optional[Item]:
        """获取数据"""
        ns_str = "/".join(namespace)
        cursor = await self._conn.execute(
            "SELECT value, created_at, updated_at FROM long_term_memory "
            "WHERE namespace = ? AND key = ?",
            (ns_str, key)
        )
        row = await cursor.fetchone()
        if row:
            return Item(
                namespace=namespace, key=key,
                value=json.loads(row["value"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        return None

    async def delete(self, namespace: Tuple[str, ...], key: str) -> None:
        """删除数据"""
        ns_str = "/".join(namespace)
        await self._conn.execute(
            "DELETE FROM long_term_memory WHERE namespace = ? AND key = ?",
            (ns_str, key)
        )
        await self._conn.commit()

    async def search(self, namespace: Tuple[str, ...], *,
                     query: Optional[str] = None, limit: int = 10,
                     offset: int = 0, **kwargs) -> List[SearchItem]:
        """搜索数据"""
        ns_str = "/".join(namespace)
        sql = "SELECT * FROM long_term_memory WHERE namespace LIKE ?"
        params = [ns_str + "%"]

        if query:
            sql += " AND value LIKE ?"
            params.append(f"%{query}%")

        sql += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await self._conn.execute(sql, params)
        results = []
        async for row in cursor:
            results.append(SearchItem(
                namespace=tuple(row["namespace"].split("/")),
                key=row["key"],
                value=json.loads(row["value"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                score=1.0
            ))
        return results

    async def health_check(self) -> Dict[str, Any]:
        cursor = await self._conn.execute(
            "SELECT COUNT(*) as cnt FROM long_term_memory"
        )
        row = await cursor.fetchone()
        return {
            "status": "healthy",
            "plugin": self.name,
            "records_count": row["cnt"] if row else 0,
            "state": self._state.value
        }
```

### 4.3 用户记忆插件 (UserMemoryPlugin)

```python
# memory/plugins/user_memory_plugin.py
import aiosqlite
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import MemoryPlugin, PluginState

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
```

---

## 5. LangGraph 集成 (langgraph dev 兼容)

### 5.1 工厂函数设计

```python
# memory/checkpointer.py - 更新版
from pathlib import Path
from typing import Optional
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from .plugins.manager import MemoryPluginManager
from .plugins.checkpointer_plugin import CheckpointerPlugin

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = str(DATA_DIR / "agent_memory.db")

_plugin_manager: Optional[MemoryPluginManager] = None

async def get_checkpointer() -> AsyncSqliteSaver:
    """获取 Checkpointer - 供 langgraph.json 配置使用

    langgraph.json 配置:
    {
      "checkpointer": {
        "path": "./memory/checkpointer.py:get_checkpointer"
      }
    }

    langgraph dev 会自动调用此函数获取 checkpointer 实例
    """
    global _plugin_manager

    # 确保数据目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 初始化插件管理器
    if _plugin_manager is None:
        _plugin_manager = MemoryPluginManager(DB_PATH)
        _plugin_manager.register(CheckpointerPlugin)
        await _plugin_manager.enable_plugin("checkpointer")

    # 获取插件并返回 saver
    plugin = _plugin_manager.get("checkpointer")
    return await plugin.get_saver()
```

```python
# memory/store.py - 更新版
from pathlib import Path
from typing import Optional
from langgraph.store.base import BaseStore
from .plugins.manager import MemoryPluginManager
from .plugins.store_plugin import StorePlugin

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = str(DATA_DIR / "agent_memory.db")

_plugin_manager: Optional[MemoryPluginManager] = None

async def get_store() -> BaseStore:
    """获取 Store - 供 langgraph.json 配置使用

    langgraph.json 配置:
    {
      "store": {
        "path": "./memory/store.py:get_store"
      }
    }

    langgraph dev 会自动调用此函数获取 store 实例
    """
    global _plugin_manager

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if _plugin_manager is None:
        _plugin_manager = MemoryPluginManager(DB_PATH)
        _plugin_manager.register(StorePlugin)
        await _plugin_manager.enable_plugin("store")

    return _plugin_manager.get("store")
```

### 5.2 langgraph.json 配置

```json
{
  "$schema": "https://langgra.ph/schema.json",
  "dependencies": ["."],
  "graphs": {
    "text2sql_agent": "./text2sql/chat_graph.py:get_app",
    "text2case_agent": "./text2case/chat_graph.py:get_app"
  },
  "env": ".env",
  "checkpointer": {
    "path": "./memory/checkpointer.py:get_checkpointer",
    "ttl": {
      "strategy": "delete",
      "sweep_interval_minutes": 10,
      "default_ttl": 43200
    }
  },
  "store": {
    "path": "./memory/store.py:get_store",
    "ttl": {
      "refresh_on_read": true,
      "default_ttl": 10080,
      "sweep_interval_minutes": 60
    }
  }
}
```

### 5.3 Graph 节点中使用记忆

```python
# text2sql/chat_graph.py
from langgraph.graph import StateGraph
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig

async def agent_node(
    state: AgentState,
    config: RunnableConfig,
    *,
    store: BaseStore  # langgraph dev 自动注入
):
    """Agent 节点 - store 由 langgraph 自动注入"""

    # 从 config 获取用户信息
    user_id = config["configurable"].get("user_id", "default")
    thread_id = config["configurable"].get("thread_id")

    # 使用 store 获取用户记忆
    namespace = ("user_preferences", user_id)
    prefs = await store.get(namespace, "settings")

    # 使用 store 获取历史查询模式
    patterns_ns = ("query_patterns", user_id)
    patterns = await store.search(patterns_ns, limit=5)

    # ... 处理逻辑

    # 保存成功的查询模式
    if result.success:
        await store.put(
            patterns_ns,
            f"pattern_{uuid4().hex[:8]}",
            {
                "query": state["input"],
                "sql": result.sql,
                "timestamp": datetime.now().isoformat()
            }
        )

    return state
```

---

## 6. 数据库表结构

### 6.1 完整表结构 (SQLite)

```sql
-- ============================================
-- 短期记忆表 (由 AsyncSqliteSaver 自动创建)
-- ============================================

-- checkpoints 表: 存储状态检查点
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint BLOB,
    metadata BLOB,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

-- writes 表: 存储待处理的写入
CREATE TABLE IF NOT EXISTS writes (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    channel TEXT NOT NULL,
    type TEXT,
    blob BLOB,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

-- ============================================
-- 长期记忆表 (由 StorePlugin 创建)
-- ============================================

CREATE TABLE IF NOT EXISTS long_term_memory (
    id TEXT PRIMARY KEY,
    namespace TEXT NOT NULL,         -- 格式: "type/user_id" 如 "schema_cache/1"
    key TEXT NOT NULL,
    value TEXT NOT NULL,             -- JSON 格式
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(namespace, key)
);

CREATE INDEX IF NOT EXISTS idx_ltm_namespace ON long_term_memory(namespace);
CREATE INDEX IF NOT EXISTS idx_ltm_ns_key ON long_term_memory(namespace, key);

-- ============================================
-- 用户记忆表 (由 UserMemoryPlugin 创建)
-- ============================================

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    preferences TEXT DEFAULT '{}',   -- JSON: 用户偏好设置
    context TEXT DEFAULT '{}',       -- JSON: 上下文信息
    interaction_count INTEGER DEFAULT 0,
    last_interaction TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_memories (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,           -- 记忆内容
    category TEXT DEFAULT 'general', -- fact, preference, pattern 等
    importance REAL DEFAULT 0.5,     -- 重要性 0.0-1.0
    metadata TEXT DEFAULT '{}',      -- JSON: 额外元数据
    access_count INTEGER DEFAULT 0,  -- 访问次数
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

CREATE INDEX IF NOT EXISTS idx_um_user ON user_memories(user_id);
CREATE INDEX IF NOT EXISTS idx_um_category ON user_memories(category);
CREATE INDEX IF NOT EXISTS idx_um_importance ON user_memories(importance DESC);
```

---

## 7. 插件启用/禁用配置

### 7.1 配置文件方式

```python
# memory/config.py
from dataclasses import dataclass, field
from typing import List
from pathlib import Path

@dataclass
class MemoryPluginConfig:
    """记忆插件配置"""

    # 数据库路径
    db_path: str = field(
        default_factory=lambda: str(
            Path(__file__).parent.parent / "data" / "agent_memory.db"
        )
    )

    # 启用的插件列表
    enabled_plugins: List[str] = field(
        default_factory=lambda: ["checkpointer", "store", "user_memory"]
    )

    # 插件特定配置
    checkpointer: dict = field(default_factory=lambda: {
        "ttl_days": 30,           # 检查点保留天数
        "sweep_interval": 600,    # 清理间隔(秒)
    })

    store: dict = field(default_factory=lambda: {
        "ttl_days": 7,            # 默认存储保留天数
        "max_items_per_namespace": 1000,
    })

    user_memory: dict = field(default_factory=lambda: {
        "max_memories_per_user": 500,
        "auto_cleanup_threshold": 0.1,  # 重要性低于此值自动清理
    })

# 全局配置实例
MEMORY_CONFIG = MemoryPluginConfig()
```

### 7.2 运行时启用/禁用

```python
# 使用示例
from memory.plugins.manager import MemoryPluginManager
from memory.plugins.checkpointer_plugin import CheckpointerPlugin
from memory.plugins.store_plugin import StorePlugin
from memory.plugins.user_memory_plugin import UserMemoryPlugin

async def setup_memory_system(db_path: str, enabled: List[str]):
    """初始化记忆系统"""
    manager = MemoryPluginManager(db_path)

    # 注册所有可用插件
    manager.register(CheckpointerPlugin)
    manager.register(StorePlugin)
    manager.register(UserMemoryPlugin)

    # 只启用配置中指定的插件
    for plugin_name in enabled:
        await manager.enable_plugin(plugin_name)

    return manager

# 运行时禁用某个插件
async def disable_user_memory():
    manager = MemoryPluginManager.get_instance()
    await manager.disable_plugin("user_memory")
    print("用户记忆插件已禁用")
```

---

## 8. 文件结构

```
agent-backend/memory/
├── __init__.py              # 模块导出
├── config.py                # 插件配置 [新增]
├── checkpointer.py          # Checkpointer 工厂函数 [更新]
├── store.py                 # Store 工厂函数 [更新]
├── manager.py               # 统一管理器 [更新]
├── plugins/                 # 插件目录 [新增]
│   ├── __init__.py
│   ├── base.py              # 插件基类
│   ├── manager.py           # 插件管理器
│   ├── checkpointer_plugin.py
│   ├── store_plugin.py
│   └── user_memory_plugin.py
└── migrations/              # 数据库迁移 [新增]
    ├── __init__.py
    ├── 001_init_tables.sql
    └── migrate.py
```

---

## 9. 测试验证

### 9.1 验证 SQLite 持久化

```python
# tests/test_memory_persistence.py
import pytest
import asyncio
from pathlib import Path

async def test_checkpointer_persistence():
    """测试短期记忆持久化到 SQLite"""
    from memory.checkpointer import get_checkpointer

    checkpointer = await get_checkpointer()

    # 验证是 AsyncSqliteSaver 类型
    assert type(checkpointer).__name__ == "AsyncSqliteSaver"

    # 验证数据库文件存在
    db_path = Path("data/agent_memory.db")
    assert db_path.exists()

async def test_store_persistence():
    """测试长期记忆持久化到 SQLite"""
    from memory.store import get_store

    store = await get_store()

    # 存储数据
    await store.put(("test", "user1"), "key1", {"data": "value"})

    # 验证可以读取
    item = await store.get(("test", "user1"), "key1")
    assert item.value["data"] == "value"

    # 重启后数据仍存在 (模拟重启)
    store2 = await get_store()
    item2 = await store2.get(("test", "user1"), "key1")
    assert item2.value["data"] == "value"

async def test_no_memory_storage():
    """确保没有使用内存存储"""
    from memory.store import get_store

    store = await get_store()

    # 验证不是 InMemoryStore
    assert "InMemory" not in type(store).__name__
```

### 9.2 验证插件可插拔

```python
async def test_plugin_enable_disable():
    """测试插件启用/禁用"""
    from memory.plugins.manager import MemoryPluginManager
    from memory.plugins.user_memory_plugin import UserMemoryPlugin

    manager = MemoryPluginManager("data/test.db")
    manager.register(UserMemoryPlugin)

    # 初始状态: 禁用
    plugin = manager.get("user_memory")
    assert plugin.state.value == "disabled"

    # 启用
    await manager.enable_plugin("user_memory")
    assert plugin.state.value == "enabled"

    # 禁用
    await manager.disable_plugin("user_memory")
    assert plugin.state.value == "disabled"
```

---

## 10. 总结

### 10.1 核心变更

| 项目 | 变更前 | 变更后 |
|------|--------|--------|
| 短期记忆 | langgraph dev 默认使用内存 | 强制使用 SQLite (AsyncSqliteSaver) |
| 长期记忆 | 可能使用文件/内存 | 强制使用 SQLite (PersistentStore) |
| 架构 | 单体模块 | 插件式可插拔架构 |
| 配置 | 硬编码 | langgraph.json + config.py |

### 10.2 关键技术点

1. **AsyncSqliteSaver**: LangGraph 官方的 SQLite 检查点实现
2. **BaseStore 接口**: 实现标准 Store 接口，确保兼容性
3. **插件管理器**: 支持运行时启用/禁用插件
4. **单一数据库**: 所有数据存储在 `agent_memory.db`

老板，以上是完整的技术实现细节。请问您是否需要我开始实现这个插件式记忆系统？
