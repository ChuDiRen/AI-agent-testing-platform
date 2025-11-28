"""
SQL验证代理

验证SQL的正确性和安全性
"""

from typing import Any, Dict, List

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel

from ..config import get_model
from ..prompts import load_prompt
from ..tools.validation_tools import VALIDATION_TOOLS


def create_sql_validator_agent(
    model: BaseChatModel = None,
    tools: List = None
) -> Any:
    """创建SQL验证代理
    
    Args:
        model: LLM模型
        tools: 工具列表
        
    Returns:
        配置好的React代理
    """
    if model is None:
        model = get_model()
    
    if tools is None:
        tools = VALIDATION_TOOLS
    
    prompt = load_prompt("sql_validator")
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        name="validator_expert",
        prompt=prompt
    )
    
    return agent


async def validate_sql(
    agent,
    sql: str,
    schema_tables: List[str] = None,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """验证SQL语句
    
    Args:
        agent: 验证代理
        sql: SQL语句
        schema_tables: 已知表名列表
        config: 运行配置
        
    Returns:
        验证结果
    """
    tables_str = ", ".join(schema_tables) if schema_tables else "未提供"
    
    messages = [
        {
            "role": "user",
            "content": f"""请验证以下SQL语句:

```sql
{sql}
```

已知表名: {tables_str}

请检查:
1. SQL语法是否正确
2. 是否存在安全风险
3. 是否有性能问题

如果有问题，请提供修复建议。
"""
        }
    ]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result


def quick_validate(sql: str, schema_tables: List[str] = None) -> Dict[str, Any]:
    """快速验证SQL（不使用LLM）
    
    Args:
        sql: SQL语句
        schema_tables: 已知表名列表
        
    Returns:
        验证结果
    """
    from ..tools.validation_tools import validate_sql as validate_tool
    
    return validate_tool.invoke({
        "sql": sql,
        "schema_tables": schema_tables or []
    })
