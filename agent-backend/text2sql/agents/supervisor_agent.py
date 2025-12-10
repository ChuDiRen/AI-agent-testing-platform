"""
监督代理

协调整个工作流程，路由任务给专门化代理
"""

from typing import Any, Dict, List

from langgraph_supervisor import create_supervisor
from langchain_core.language_models import BaseChatModel

from ..config import get_model
from ..prompts import load_prompt


def create_text2sql_supervisor(
    model: BaseChatModel = None,
    agents: List = None,
    max_retries: int = 3
) -> Any:
    """创建Text2SQL监督代理
    
    Args:
        model: LLM模型
        agents: 子代理列表
        max_retries: 最大重试次数
        
    Returns:
        配置好的Supervisor
    """
    if model is None:
        model = get_model()
    
    if agents is None:
        # 创建默认代理
        from .schema_agent import create_schema_agent
        from .sql_generator_agent import create_sql_generator_agent
        from .sql_validator_agent import create_sql_validator_agent
        from .sql_executor_agent import create_sql_executor_agent
        from .error_recovery_agent import create_error_recovery_agent
        from .chart_generator_agent import create_chart_generator_agent
        
        agents = [
            create_schema_agent(model),
            create_sql_generator_agent(model),
            create_sql_validator_agent(model),
            create_sql_executor_agent(model),
            create_error_recovery_agent(model),
            create_chart_generator_agent(model)
        ]
    
    prompt = load_prompt("supervisor", max_retries=max_retries)
    
    # 创建Supervisor
    supervisor = create_supervisor(
        agents=agents,
        model=model,
        prompt=prompt
    )
    
    return supervisor


def build_supervisor_with_config(
    model: BaseChatModel = None,
    connection_id: int = 0,
    max_retries: int = 3,
    dialect: str = "mysql"
) -> Any:
    """构建带配置的Supervisor
    
    Args:
        model: LLM模型
        connection_id: 数据库连接ID
        max_retries: 最大重试次数
        dialect: 数据库方言
        
    Returns:
        配置好的Supervisor
    """
    if model is None:
        model = get_model()
    
    # 导入代理创建函数
    from .schema_agent import create_schema_agent
    from .sql_generator_agent import create_sql_generator_agent
    from .sql_validator_agent import create_sql_validator_agent
    from .sql_executor_agent import create_sql_executor_agent
    from .error_recovery_agent import create_error_recovery_agent
    from .chart_generator_agent import create_chart_generator_agent
    
    # 创建各代理，传入 connection_id
    schema_agent = create_schema_agent(model, connection_id=connection_id)
    sql_generator = create_sql_generator_agent(model, dialect=dialect)
    sql_validator = create_sql_validator_agent(model)
    sql_executor = create_sql_executor_agent(model, connection_id=connection_id)
    error_recovery = create_error_recovery_agent(model, max_retries=max_retries)
    chart_generator = create_chart_generator_agent(model)
    
    agents = [
        schema_agent,
        sql_generator,
        sql_validator,
        sql_executor,
        error_recovery,
        chart_generator
    ]
    
    prompt = load_prompt("supervisor", max_retries=max_retries)
    
    supervisor = create_supervisor(
        agents=agents,
        model=model,
        prompt=prompt
    )
    
    return supervisor
