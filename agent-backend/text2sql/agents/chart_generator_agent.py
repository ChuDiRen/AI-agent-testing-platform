"""
图表生成代理

调用mcp-server-chart生成数据可视化图表
"""

from typing import Any, Dict, List

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel

from ..config import get_model
from ..prompts import load_prompt
from ..tools.chart_tools import CHART_TOOLS


def create_chart_generator_agent(
    model: BaseChatModel = None,
    tools: List = None
) -> Any:
    """创建图表生成代理
    
    Args:
        model: LLM模型
        tools: 工具列表
        
    Returns:
        配置好的React代理
    """
    if model is None:
        model = get_model()
    
    if tools is None:
        tools = CHART_TOOLS
    
    prompt = load_prompt("chart_generator")
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        name="chart_expert",
        prompt=prompt
    )
    
    return agent


async def generate_chart(
    agent,
    data: List[Dict[str, Any]],
    columns: List[str],
    user_request: str = "",
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """生成图表
    
    Args:
        agent: 图表代理
        data: 查询结果数据
        columns: 列名列表
        user_request: 用户的图表需求
        config: 运行配置
        
    Returns:
        图表生成结果
    """
    # 限制数据量
    sample_data = data[:100] if len(data) > 100 else data
    
    content = f"""请根据以下数据生成合适的图表:

数据列: {', '.join(columns)}
数据行数: {len(data)}
样本数据: {sample_data[:5]}

"""
    
    if user_request:
        content += f"用户要求: {user_request}\n"
    else:
        content += "请自动选择最合适的图表类型。\n"
    
    messages = [{"role": "user", "content": content}]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result


def quick_chart(
    data: List[Dict[str, Any]],
    columns: List[str],
    chart_type: str = None,
    title: str = "Chart"
) -> Dict[str, Any]:
    """快速生成图表（不使用LLM）
    
    Args:
        data: 数据
        columns: 列名
        chart_type: 图表类型
        title: 标题
        
    Returns:
        图表配置
    """
    from ..tools.chart_tools import generate_chart as gen_chart
    
    return gen_chart.invoke({
        "data": data,
        "columns": columns,
        "chart_type": chart_type,
        "title": title
    })
