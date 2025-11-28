"""
SQL生成代理

根据Schema信息生成高质量SQL语句
"""

from typing import Any, Dict, List

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel

from ..config import get_model
from ..prompts import load_prompt
from ..tools.sql_tools import SQL_TOOLS


def create_sql_generator_agent(
    model: BaseChatModel = None,
    tools: List = None,
    dialect: str = "mysql",
    top_k: int = 100
) -> Any:
    """创建SQL生成代理
    
    Args:
        model: LLM模型
        tools: 工具列表
        dialect: 数据库方言
        top_k: 默认LIMIT值
        
    Returns:
        配置好的React代理
    """
    if model is None:
        model = get_model()
    
    if tools is None:
        tools = SQL_TOOLS
    
    # 加载并格式化提示词
    prompt = load_prompt("sql_generator", dialect=dialect, top_k=top_k)
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        name="sql_expert",
        prompt=prompt
    )
    
    return agent


async def generate_sql(
    agent,
    query_analysis: Dict[str, Any],
    schema_info: Dict[str, Any],
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """生成SQL语句
    
    Args:
        agent: SQL生成代理
        query_analysis: 查询分析结果
        schema_info: Schema信息
        config: 运行配置
        
    Returns:
        生成结果（包含SQL）
    """
    # 构建Schema上下文
    schema_context = format_schema_for_prompt(schema_info)
    
    messages = [
        {
            "role": "user",
            "content": f"""根据以下信息生成SQL查询:

## 查询分析
{format_analysis(query_analysis)}

## 数据库Schema
{schema_context}

请生成正确的SQL语句，注意:
1. 只生成SELECT语句
2. 添加适当的LIMIT
3. 使用正确的列名和表名
4. 优化查询性能
"""
        }
    ]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result


def format_schema_for_prompt(schema_info: Dict[str, Any]) -> str:
    """格式化Schema信息为提示词"""
    lines = []
    
    for table in schema_info.get("tables", []):
        table_name = table.get("name", "unknown")
        lines.append(f"### 表: {table_name}")
        
        columns = schema_info.get("columns", {}).get(table_name, [])
        if columns:
            lines.append("列:")
            for col in columns:
                col_str = f"  - {col['name']}: {col['data_type']}"
                if col.get("primary_key"):
                    col_str += " [PK]"
                if col.get("foreign_key"):
                    col_str += f" [FK -> {col['foreign_key']}]"
                lines.append(col_str)
        lines.append("")
    
    # 添加关系信息
    relationships = schema_info.get("relationships", [])
    if relationships:
        lines.append("### 表关系")
        for rel in relationships:
            lines.append(
                f"  - {rel['from_table']}.{rel['from_column']} -> "
                f"{rel['to_table']}.{rel['to_column']}"
            )
    
    return "\n".join(lines)


def format_analysis(analysis: Dict[str, Any]) -> str:
    """格式化分析结果"""
    lines = []
    
    if analysis.get("intent"):
        lines.append(f"意图: {analysis['intent']}")
    
    if analysis.get("relevant_tables"):
        lines.append(f"相关表: {', '.join(analysis['relevant_tables'])}")
    
    if analysis.get("filters"):
        lines.append(f"过滤条件: {', '.join(analysis['filters'])}")
    
    if analysis.get("aggregations"):
        lines.append(f"聚合函数: {', '.join(analysis['aggregations'])}")
    
    if analysis.get("ordering"):
        lines.append(f"排序: {', '.join(analysis['ordering'])}")
    
    return "\n".join(lines)
