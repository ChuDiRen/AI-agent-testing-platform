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