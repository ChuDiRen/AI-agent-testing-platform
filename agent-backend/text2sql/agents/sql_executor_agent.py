"""
SQL执行代理

安全执行SQL并处理结果
"""

from typing import Any, Dict, List, Optional

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool

from text2sql.config import get_model
from text2sql.prompts import load_prompt
from text2sql.database.db_manager import get_database_manager


def create_executor_tools(connection_id: int) -> List:
    """创建执行器工具
    
    Args:
        connection_id: 数据库连接ID
        
    Returns:
        工具列表
    """
    
    @tool
    def execute_sql(sql: str) -> Dict[str, Any]:
        """执行SQL查询
        
        Args:
            sql: SQL语句
            
        Returns:
            执行结果
        """
        manager = get_database_manager(connection_id)
        result = manager.execute_query(sql)
        return result.to_dict()
    
    @tool
    def execute_sql_with_pagination(
        sql: str,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """执行带分页的SQL查询
        
        Args:
            sql: SQL语句
            page: 页码
            page_size: 每页大小
            
        Returns:
            分页执行结果
        """
        manager = get_database_manager(connection_id)
        result = manager.execute_query_with_pagination(sql, page, page_size)
        return result.to_dict()
    
    return [execute_sql, execute_sql_with_pagination]


def create_sql_executor_agent(
    model: BaseChatModel = None,
    connection_id: int = 0,
    timeout: int = 30,
    max_rows: int = 1000
) -> Any:
    """创建SQL执行代理
    
    Args:
        model: LLM模型
        connection_id: 数据库连接ID
        timeout: 超时时间
        max_rows: 最大返回行数
        
    Returns:
        配置好的React代理
    """
    if model is None:
        model = get_model()
    
    tools = create_executor_tools(connection_id)
    
    prompt = load_prompt(
        "sql_executor",
        timeout=timeout,
        max_rows=max_rows,
        page=1,
        page_size=100
    )
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        name="executor_expert",
        prompt=prompt
    )
    
    return agent


async def execute_query(
    agent,
    sql: str,
    pagination: Optional[Dict[str, int]] = None,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """执行SQL查询
    
    Args:
        agent: 执行代理
        sql: SQL语句
        pagination: 分页配置 {"page": 1, "page_size": 100}
        config: 运行配置
        
    Returns:
        执行结果
    """
    if pagination:
        content = f"""请执行以下SQL查询（带分页）:

```sql
{sql}
```

分页参数:
- 页码: {pagination.get('page', 1)}
- 每页大小: {pagination.get('page_size', 100)}
"""
    else:
        content = f"""请执行以下SQL查询:

```sql
{sql}
```
"""
    
    messages = [{"role": "user", "content": content}]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result


def direct_execute(
    connection_id: int,
    sql: str,
    page: int = 1,
    page_size: int = 100
) -> Dict[str, Any]:
    """直接执行SQL（不使用LLM）
    
    Args:
        connection_id: 数据库连接ID
        sql: SQL语句
        page: 页码
        page_size: 每页大小
        
    Returns:
        执行结果
    """
    manager = get_database_manager(connection_id)
    result = manager.execute_query_with_pagination(sql, page, page_size)
    return result.to_dict()
