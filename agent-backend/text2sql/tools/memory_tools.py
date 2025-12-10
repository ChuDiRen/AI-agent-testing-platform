"""
记忆工具

提供 Agent 访问长期记忆的工具
参考: https://docs.langchain.com/oss/python/langchain/long-term-memory

在 Tool 中通过 InjectedStore 访问 Store
"""

from typing import Any, Dict, List, Optional
from typing_extensions import Annotated

from langchain_core.tools import tool, InjectedToolArg
from langgraph.store.base import BaseStore

from ..memory.manager import get_memory_manager, MemoryManager


# ==================== Schema 缓存工具 ====================

@tool
def get_cached_schema(
    connection_id: int,
    store: Annotated[BaseStore, InjectedToolArg]
) -> Optional[Dict[str, Any]]:
    """从长期记忆中获取缓存的数据库 Schema
    
    如果 Schema 已缓存且未过期，直接返回缓存数据，
    避免重复查询数据库结构。
    
    Args:
        connection_id: 数据库连接 ID
        store: 注入的 Store 实例
        
    Returns:
        缓存的 Schema 信息，如果不存在或过期返回 None
    """
    namespace = ("schema_cache", str(connection_id))
    item = store.get(namespace, "schema")
    
    if item is None:
        return None
    
    # 检查是否过期
    from datetime import datetime, timedelta
    cached_at = item.value.get("cached_at")
    ttl_hours = item.value.get("ttl_hours", 24)
    
    if cached_at:
        cached_time = datetime.fromisoformat(cached_at)
        if datetime.now() - cached_time > timedelta(hours=ttl_hours):
            return None
    
    return item.value.get("data")


@tool
def cache_schema(
    connection_id: int,
    schema_info: Dict[str, Any],
    store: Annotated[BaseStore, InjectedToolArg],
    ttl_hours: int = 24
) -> str:
    """将数据库 Schema 缓存到长期记忆
    
    缓存 Schema 信息以避免重复查询数据库结构。
    
    Args:
        connection_id: 数据库连接 ID
        schema_info: Schema 信息
        store: 注入的 Store 实例
        ttl_hours: 缓存有效期（小时）
        
    Returns:
        操作结果消息
    """
    from datetime import datetime
    
    namespace = ("schema_cache", str(connection_id))
    store.put(namespace, "schema", {
        "data": schema_info,
        "cached_at": datetime.now().isoformat(),
        "ttl_hours": ttl_hours
    })
    
    return f"Schema 已缓存，有效期 {ttl_hours} 小时"


# ==================== 查询模式工具 ====================

@tool
def get_similar_query_patterns(
    user_id: str,
    current_query: str,
    store: Annotated[BaseStore, InjectedToolArg],
    limit: int = 5
) -> List[Dict[str, Any]]:
    """从长期记忆中获取相似的历史查询模式
    
    查找用户之前成功执行的相似查询，可以作为参考。
    
    Args:
        user_id: 用户 ID
        current_query: 当前自然语言查询
        store: 注入的 Store 实例
        limit: 最大返回数量
        
    Returns:
        相似查询模式列表，包含历史 SQL 和执行信息
    """
    namespace = ("query_patterns", user_id)
    items = store.search(namespace, query=current_query, limit=limit)
    
    return [
        {
            "pattern_id": item.key,
            "natural_query": item.value.get("natural_query"),
            "sql": item.value.get("sql"),
            "success": item.value.get("success"),
            "use_count": item.value.get("use_count", 0)
        }
        for item in items
    ]


@tool
def save_query_pattern(
    user_id: str,
    natural_query: str,
    sql: str,
    store: Annotated[BaseStore, InjectedToolArg],
    schema_context: Optional[Dict[str, Any]] = None,
    success: bool = True,
    execution_time_ms: float = 0
) -> str:
    """保存成功的查询模式到长期记忆
    
    当 SQL 执行成功后，保存查询模式供未来参考。
    
    Args:
        user_id: 用户 ID
        natural_query: 自然语言查询
        sql: 生成的 SQL
        store: 注入的 Store 实例
        schema_context: Schema 上下文
        success: 是否执行成功
        execution_time_ms: 执行时间
        
    Returns:
        操作结果消息
    """
    import hashlib
    from datetime import datetime
    
    # 生成模式 ID
    pattern_id = hashlib.md5(
        f"{user_id}:{natural_query}".encode()
    ).hexdigest()[:12]
    
    namespace = ("query_patterns", user_id)
    store.put(namespace, pattern_id, {
        "natural_query": natural_query,
        "sql": sql,
        "schema_context": schema_context or {},
        "success": success,
        "execution_time_ms": execution_time_ms,
        "created_at": datetime.now().isoformat(),
        "use_count": 1
    })
    
    return f"查询模式已保存，ID: {pattern_id}"


# ==================== 用户偏好工具 ====================

@tool
def get_user_preference(
    user_id: str,
    key: str,
    store: Annotated[BaseStore, InjectedToolArg],
    default: Any = None
) -> Any:
    """获取用户偏好设置
    
    Args:
        user_id: 用户 ID
        key: 偏好键（如 "default_limit", "preferred_chart_type"）
        store: 注入的 Store 实例
        default: 默认值
        
    Returns:
        用户偏好值
    """
    namespace = ("user_preferences", user_id)
    item = store.get(namespace, key)
    
    if item is None:
        return default
    
    return item.value.get("value", default)


@tool
def save_user_preference(
    user_id: str,
    key: str,
    value: Any,
    store: Annotated[BaseStore, InjectedToolArg]
) -> str:
    """保存用户偏好设置
    
    Args:
        user_id: 用户 ID
        key: 偏好键
        value: 偏好值
        store: 注入的 Store 实例
        
    Returns:
        操作结果消息
    """
    from datetime import datetime
    
    namespace = ("user_preferences", user_id)
    store.put(namespace, key, {
        "value": value,
        "updated_at": datetime.now().isoformat()
    })
    
    return f"用户偏好 '{key}' 已保存"


@tool
def get_all_user_preferences(
    user_id: str,
    store: Annotated[BaseStore, InjectedToolArg]
) -> Dict[str, Any]:
    """获取用户的所有偏好设置
    
    Args:
        user_id: 用户 ID
        store: 注入的 Store 实例
        
    Returns:
        所有偏好设置的字典
    """
    namespace = ("user_preferences", user_id)
    items = store.search(namespace, limit=100)
    
    return {
        item.key: item.value.get("value")
        for item in items
    }


# ==================== 成功查询历史工具 ====================

@tool
def get_successful_queries(
    connection_id: int,
    store: Annotated[BaseStore, InjectedToolArg],
    limit: int = 10
) -> List[Dict[str, Any]]:
    """获取数据库的成功查询历史
    
    用于学习和参考之前成功执行的查询。
    
    Args:
        connection_id: 数据库连接 ID
        store: 注入的 Store 实例
        limit: 最大返回数量
        
    Returns:
        成功查询历史列表
    """
    namespace = ("successful_queries", str(connection_id))
    items = store.search(namespace, limit=limit)
    
    return [item.value for item in items]


@tool
def save_successful_query(
    connection_id: int,
    natural_query: str,
    sql: str,
    store: Annotated[BaseStore, InjectedToolArg],
    result_summary: Optional[Dict[str, Any]] = None
) -> str:
    """保存成功执行的查询到历史记录
    
    Args:
        connection_id: 数据库连接 ID
        natural_query: 自然语言查询
        sql: SQL 语句
        store: 注入的 Store 实例
        result_summary: 结果摘要
        
    Returns:
        操作结果消息
    """
    import hashlib
    from datetime import datetime
    
    query_id = hashlib.md5(
        f"{connection_id}:{sql}".encode()
    ).hexdigest()[:12]
    
    namespace = ("successful_queries", str(connection_id))
    store.put(namespace, query_id, {
        "natural_query": natural_query,
        "sql": sql,
        "result_summary": result_summary or {},
        "executed_at": datetime.now().isoformat()
    })
    
    return f"查询已保存到历史记录，ID: {query_id}"


# ==================== 工具列表 ====================

# Schema 缓存工具
SCHEMA_MEMORY_TOOLS = [
    get_cached_schema,
    cache_schema
]

# 查询模式工具
QUERY_PATTERN_TOOLS = [
    get_similar_query_patterns,
    save_query_pattern
]

# 用户偏好工具
USER_PREFERENCE_TOOLS = [
    get_user_preference,
    save_user_preference,
    get_all_user_preferences
]

# 查询历史工具
QUERY_HISTORY_TOOLS = [
    get_successful_queries,
    save_successful_query
]

# 所有记忆工具
MEMORY_TOOLS = (
    SCHEMA_MEMORY_TOOLS + 
    QUERY_PATTERN_TOOLS + 
    USER_PREFERENCE_TOOLS + 
    QUERY_HISTORY_TOOLS
)
