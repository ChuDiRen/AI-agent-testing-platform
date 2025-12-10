"""
Schema分析代理

分析用户查询和数据库模式
"""

from functools import partial
from typing import Any, Dict, List

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool

from ..config import get_model
from ..prompts import load_prompt
from ..tools.schema_tools import SCHEMA_TOOLS
from ..database.db_manager import get_database_manager


def _create_bound_schema_tools(connection_id: int) -> List:
    """创建绑定了 connection_id 的 schema 工具"""
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
        """获取完整的数据库Schema"""
        schema = manager.get_schema()
        return schema.to_dict()
    
    @tool
    def get_sample_data(table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取表的样本数据"""
        sql = f"SELECT * FROM {table_name} LIMIT :limit"
        result = manager.execute_query(sql, {"limit": limit})
        if result.success:
            return result.data
        return []
    
    return [get_tables, get_table_schema, get_database_schema, get_sample_data]


def create_schema_agent(
    model: BaseChatModel = None,
    tools: List = None,
    connection_id: int = None
) -> Any:
    """创建Schema分析代理
    
    Args:
        model: LLM模型，如果为None则使用默认配置
        tools: 工具列表，如果为None则使用默认Schema工具
        connection_id: 数据库连接ID，如果提供则绑定到工具
        
    Returns:
        配置好的React代理
    """
    if model is None:
        model = get_model()
    
    if tools is None:
        if connection_id is not None:
            # 使用绑定了 connection_id 的工具
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
        agent: Schema代理
        user_query: 用户查询
        connection_id: 数据库连接ID
        config: 运行配置
        
    Returns:
        分析结果
    """
    messages = [
        {
            "role": "user",
            "content": f"""请分析以下查询并提取相关的数据库Schema信息:

查询: {user_query}
数据库连接ID: {connection_id}

请使用工具获取相关的表结构和列信息，然后返回:
1. 查询意图
2. 相关的表
3. 相关的列
4. 可能的JOIN条件
5. 可能的过滤条件
"""
        }
    ]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result
