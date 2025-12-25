"""
Text-to-SQL 图工作流

基于 LangGraph 的 Text-to-SQL 工作流
"""

import sys
import os
from typing import Any, Dict, Optional

# 确保 text2sql 包可以被导入
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from text2sql.config import get_model, LLMConfig
from text2sql.agents.supervisor_agent import build_supervisor_with_config


def create_text2sql_graph(
    connection_id: int = 0,
    model_config: Optional[LLMConfig] = None,
    max_retries: int = 3,
    dialect: str = "mysql",
    checkpointer=None,
    store=None
):
    """创建 Text-to-SQL 图工作流
    
    Args:
        connection_id: 数据库连接 ID
        model_config: LLM 配置
        max_retries: 最大重试次数
        dialect: 数据库方言
        checkpointer: 短期记忆（可选）
        store: 长期记忆（可选）
        
    Returns:
        编译好的图
    """
    model = get_model(model_config)
    
    supervisor = build_supervisor_with_config(
        model=model,
        connection_id=connection_id,
        max_retries=max_retries,
        dialect=dialect
    )
    
    return supervisor.compile(checkpointer=checkpointer, store=store)


def graph(config: dict = None):
    """
    图工厂函数 - 供 LangGraph API 使用
    
    Args:
        config: RunnableConfig
        
    Returns:
        编译好的图（不含 checkpointer/store，由 LangGraph API 注入）
    """
    from text2sql.database import setup_chinook, register_connection, DatabaseConfig
    
    # 确保数据库已初始化
    try:
        db_path = setup_chinook()
        register_connection(0, DatabaseConfig(db_type="sqlite", database=str(db_path)))
    except Exception:
        pass
    
    connection_id = 0
    dialect = "sqlite"
    
    if config and "configurable" in config:
        connection_id = config["configurable"].get("connection_id", 0)
        dialect = config["configurable"].get("dialect", "sqlite")
    
    return create_text2sql_graph(
        connection_id=connection_id,
        dialect=dialect
    )


# ============== LangGraph API 工厂函数 ==============

def get_app(config: dict = None):
    """
    图工厂函数 - 供 LangGraph API 使用 (无 checkpointer)
    
    Args:
        config: RunnableConfig
        
    Returns:
        编译好的图（checkpointer 由 LangGraph API 注入）
    """
    return graph(config)
