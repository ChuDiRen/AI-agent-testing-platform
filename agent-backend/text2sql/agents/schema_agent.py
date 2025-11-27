"""
Schema分析代理

分析用户查询和数据库模式
"""

from typing import Any, Dict, List

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel

from text2sql.config import get_model
from text2sql.prompts import load_prompt
from text2sql.tools.schema_tools import SCHEMA_TOOLS


def create_schema_agent(
    model: BaseChatModel = None,
    tools: List = None
) -> Any:
    """创建Schema分析代理
    
    Args:
        model: LLM模型，如果为None则使用默认配置
        tools: 工具列表，如果为None则使用默认Schema工具
        
    Returns:
        配置好的React代理
    """
    if model is None:
        model = get_model()
    
    if tools is None:
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
