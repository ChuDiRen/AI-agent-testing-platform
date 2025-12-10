"""
Schema 分析代理

分析用户查询和数据库模式
集成长期记忆的 Schema 缓存功能
"""

from functools import partial
from typing import Any, Dict, List, Optional
from typing_extensions import Annotated

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool, InjectedToolArg
from langgraph.store.base import BaseStore

from ..config import get_model
from ..prompts import load_prompt
from ..tools.schema_tools import SCHEMA_TOOLS
from ..database.db_manager import get_database_manager


def _create_bound_schema_tools(connection_id: int) -> List:
    """创建绑定了 connection_id 的 schema 工具（带长期记忆支持）"""
    from ..memory import get_memory_manager
    
    manager = get_database_manager(connection_id)
    
    @tool
    def get_tables() -> List[str]:
        """获取数据库中所有表的列表"""
        return manager.get_tables()
    
    @tool
    def get_table_schema(table_name: str) -> Dict[str, Any]:
        """获取指定表的详细结构"""
        table_info = manager.get_table_info(table_name)
        return table_info.to_dict()
    
    @tool
    def get_database_schema() -> Dict[str, Any]:
        """获取完整的数据库 Schema（优先使用缓存）
        
        首先检查长期记忆中是否有缓存的 Schema，
        如果有且未过期则直接返回缓存数据，
        否则从数据库获取并缓存。
        """
        from datetime import datetime, timedelta
        
        # 获取记忆管理器
        memory_manager = get_memory_manager()
        store = memory_manager.store
        
        # 1. 尝试从长期记忆获取缓存
        namespace = ("schema_cache", str(connection_id))
        cached = store.get(namespace, "schema")
        
        if cached is not None:
            cached_at = cached.value.get("cached_at")
            ttl_hours = cached.value.get("ttl_hours", 24)
            
            if cached_at:
                cached_time = datetime.fromisoformat(cached_at)
                if datetime.now() - cached_time < timedelta(hours=ttl_hours):
                    # 缓存有效，直接返回
                    print(f"[Schema Cache] 命中缓存，缓存时间: {cached_at}")
                    return {
                        "data": cached.value.get("data"),
                        "from_cache": True,
                        "cached_at": cached_at
                    }
        
        # 2. 缓存不存在或已过期，从数据库获取
        print(f"[Schema Cache] 缓存未命中，从数据库获取...")
        schema = manager.get_schema()
        schema_dict = schema.to_dict()
        
        # 3. 保存到长期记忆
        store.put(namespace, "schema", {
            "data": schema_dict,
            "cached_at": datetime.now().isoformat(),
            "ttl_hours": 24
        })
        print(f"[Schema Cache] 已缓存到长期记忆")
        
        return {
            "data": schema_dict,
            "from_cache": False,
            "cached_at": datetime.now().isoformat()
        }
    
    @tool
    def get_sample_data(table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取表的样本数据"""
        sql = f"SELECT * FROM {table_name} LIMIT :limit"
        result = manager.execute_query(sql, {"limit": limit})
        if result.success:
            return result.data
        return []
    
    @tool
    def invalidate_schema_cache() -> str:
        """使 Schema 缓存失效
        
        当数据库结构发生变化时调用此工具清除缓存。
        """
        memory_manager = get_memory_manager()
        store = memory_manager.store
        namespace = ("schema_cache", str(connection_id))
        store.delete(namespace, "schema")
        return f"数据库 {connection_id} 的 Schema 缓存已清除"
    
    @tool
    def get_related_tables(table_name: str) -> List[str]:
        """获取与指定表相关的所有表"""
        schema = manager.get_schema()
        return schema.get_related_tables(table_name)
    
    return [
        get_tables, 
        get_table_schema, 
        get_database_schema, 
        get_sample_data,
        invalidate_schema_cache,
        get_related_tables
    ]


def create_schema_agent(
    model: BaseChatModel = None,
    tools: List = None,
    connection_id: int = None
) -> Any:
    """创建 Schema 分析代理
    
    Args:
        model: LLM 模型，如果为 None 则使用默认配置
        tools: 工具列表，如果为 None 则使用默认 Schema 工具
        connection_id: 数据库连接 ID，如果提供则绑定到工具
        
    Returns:
        配置好的 React 代理
    """
    if model is None:
        model = get_model()
    
    if tools is None:
        if connection_id is not None:
            # 使用绑定了 connection_id 的工具（带长期记忆支持）
            tools = _create_bound_schema_tools(connection_id)
        else:
            tools = SCHEMA_TOOLS
    
    # 加载提示词
    prompt = load_prompt("schema_agent")
    
    # 创建代理
    agent = create_react_agent(
        model=model,
        tools=tools,
        name="schema_expert",
        prompt=prompt
    )
    
    return agent


async def analyze_query(
    agent,
    user_query: str,
    connection_id: int,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """分析用户查询
    
    Args:
        agent: Schema 代理
        user_query: 用户查询
        connection_id: 数据库连接 ID
        config: 运行配置（包含 thread_id, user_id 等）
        
    Returns:
        分析结果
    """
    messages = [
        {
            "role": "user",
            "content": f"""请分析以下查询并提取相关的数据库 Schema 信息:

查询: {user_query}
数据库连接 ID: {connection_id}

请使用工具获取相关的表结构和列信息，然后返回:
1. 查询意图
2. 相关的表
3. 相关的列
4. 可能的 JOIN 条件
5. 可能的过滤条件

注意：优先使用 get_database_schema 工具获取缓存的 Schema 信息。
"""
        }
    ]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result


async def analyze_query_with_memory(
    agent,
    user_query: str,
    connection_id: int,
    thread_id: str,
    user_id: str = "default"
) -> Dict[str, Any]:
    """分析用户查询（带记忆支持）
    
    Args:
        agent: Schema 代理
        user_query: 用户查询
        connection_id: 数据库连接 ID
        thread_id: 会话线程 ID（短期记忆）
        user_id: 用户 ID（长期记忆）
        
    Returns:
        分析结果
    """
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    return await analyze_query(agent, user_query, connection_id, config)
