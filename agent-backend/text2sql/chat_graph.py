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


# ===== 初始化数据库 =====
def _ensure_database_initialized():
    """确保数据库已初始化 (同步包装)"""
    try:
        from text2sql.database import setup_chinook, register_connection, DatabaseConfig
        # 同步调用数据库设置
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 如果事件循环已在运行，使用线程调用
        import threading
        result_holder = []
        
        def sync_setup():
            db_path = asyncio.run(setup_chinook())
            register_connection(0, DatabaseConfig(db_type="sqlite", database=str(db_path)))
            result_holder.append(db_path)
        
        # 检查是否在事件循环中
        try:
            asyncio.get_running_loop()
            # 在事件循环中，使用线程
            thread = threading.Thread(target=sync_setup)
            thread.start()
            thread.join(timeout=30)
        except RuntimeError:
            # 不在事件循环中，直接调用
            sync_setup()
            
    except Exception as e:
        print(f"[警告] 数据库初始化失败: {e}")





async def create_text2sql_graph(
    connection_id: int = 0,
    model_config: Optional[LLMConfig] = None,
    max_retries: int = 3,
    dialect: str = "mysql",
    checkpointer=None,
    store=None,
    use_persistent_memory: bool = False
):
    """创建 Text-to-SQL 图工作流 - 异步

    Args:
        connection_id: 数据库连接 ID
        model_config: LLM 配置
        max_retries: 最大重试次数
        dialect: 数据库方言
        checkpointer: 短期记忆（可选，优先使用）
        store: 长期记忆（可选，优先使用）
        use_persistent_memory: 是否使用持久化记忆（当 checkpointer/store 未提供时）

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

    if use_persistent_memory and (checkpointer is None or store is None):
        from memory import get_checkpointer, get_store
        checkpointer = checkpointer or await get_checkpointer()
        store = store or await get_store()

    return supervisor.compile(checkpointer=checkpointer, store=store)


def get_app(config: dict = None):
    """
    图工厂函数 - 供 LangGraph API 使用

    返回已编译的图对象，LangGraph API 服务器将负责注入 checkpointer 和 store
    (通过 langgraph.json 配置)。

    Args:
        config: RunnableConfig

    Returns:
        已编译的 LangGraph (checkpointer/store 由 LangGraph API 服务器在编译时注入)
    """
    # 确保数据库已初始化
    _ensure_database_initialized()
    
    connection_id = 0
    dialect = "sqlite"
    max_retries = 3

    if config and "configurable" in config:
        connection_id = config["configurable"].get("connection_id", 0)
        dialect = config["configurable"].get("dialect", "sqlite")
        max_retries = config["configurable"].get("max_retries", 3)

    model = get_model()

    # 构建 StateGraph 并编译
    graph = build_supervisor_with_config(
        model=model,
        connection_id=connection_id,
        max_retries=max_retries,
        dialect=dialect
    )
    
    # 编译但不提供 checkpointer/store，由 LangGraph API 在运行时注入
    return graph.compile()


# ============== 便捷运行函数 ==============

async def run_text2sql(
    query: str,
    connection_id: int = 0,
    dialect: str = "sqlite",
    thread_id: str = "default",
    user_id: str = "default"
) -> dict:
    """便捷运行函数（带持久化记忆）- 纯异步

    Args:
        query: 自然语言查询
        connection_id: 数据库连接 ID
        dialect: 数据库方言
        thread_id: 会话 ID
        user_id: 用户 ID

    Returns:
        查询结果
    """
    from langchain_core.messages import HumanMessage
    from text2sql.database import setup_chinook, register_connection, DatabaseConfig

    # 确保数据库已初始化
    try:
        db_path = await setup_chinook()
        register_connection(0, DatabaseConfig(db_type="sqlite", database=str(db_path)))
    except Exception:
        pass

    # 使用持久化记忆创建图（异步）
    app = await create_text2sql_graph(
        connection_id=connection_id,
        dialect=dialect,
        use_persistent_memory=True
    )

    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }

    result = await app.ainvoke(
        {"messages": [HumanMessage(content=query)]},
        config
    )

    final_message = result.get("messages", [])[-1] if result.get("messages") else None

    return {
        "success": True,
        "content": final_message.content if final_message else "",
        "messages": result.get("messages", []),
    }
