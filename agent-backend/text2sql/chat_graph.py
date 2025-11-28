"""
主图工作流

基于LangGraph的Text-to-SQL图工作流
"""

from typing import Any, AsyncIterator, Dict, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.memory import InMemoryStore

from .state import SQLMessageState, WorkflowStage
from .config import get_model, get_config, LLMConfig
from .memory.manager import get_memory_manager
from .context.manager import ContextManager
from .agents.supervisor_agent import build_supervisor_with_config


def create_text2sql_graph(
    connection_id: int = 0,
    model_config: Optional[LLMConfig] = None,
    max_retries: int = 3,
    dialect: str = "mysql"
):
    """创建Text-to-SQL图工作流
    
    Args:
        connection_id: 数据库连接ID
        model_config: LLM配置
        max_retries: 最大重试次数
        dialect: 数据库方言
        
    Returns:
        编译好的图
    """
    # 获取模型
    model = get_model(model_config)
    
    # 获取记忆管理器
    memory_manager = get_memory_manager()
    
    # 构建Supervisor
    supervisor = build_supervisor_with_config(
        model=model,
        connection_id=connection_id,
        max_retries=max_retries,
        dialect=dialect
    )
    
    # 编译图
    app = supervisor.compile(
        checkpointer=memory_manager.checkpointer,
        store=memory_manager.store
    )
    
    return app


def create_simple_graph(
    connection_id: int = 0,
    db_path: str = "data/agent_memory.db"
):
    """创建简化的Text-to-SQL图（无Supervisor）
    
    Args:
        connection_id: 数据库连接ID
        db_path: 记忆数据库路径
        
    Returns:
        编译好的图
    """
    from .agents.schema_agent import create_schema_agent
    from .agents.sql_generator_agent import create_sql_generator_agent
    from .agents.sql_validator_agent import quick_validate
    from .agents.sql_executor_agent import direct_execute
    
    model = get_model()
    
    # 定义节点函数
    async def analyze_schema(state: SQLMessageState) -> Dict[str, Any]:
        """分析Schema"""
        agent = create_schema_agent(model)
        
        # 获取最后一条用户消息
        user_message = ""
        for msg in reversed(state["messages"]):
            if msg.get("role") == "user" or hasattr(msg, "type") and msg.type == "human":
                user_message = msg.get("content", "") if isinstance(msg, dict) else msg.content
                break
        
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": f"分析查询: {user_message}"}]
        })
        
        return {
            "current_stage": "schema_analysis",
            "query_analysis": {"intent": user_message}
        }
    
    async def generate_sql(state: SQLMessageState) -> Dict[str, Any]:
        """生成SQL"""
        agent = create_sql_generator_agent(model)
        
        query = state.get("query_analysis", {}).get("intent", "")
        
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": f"根据查询生成SQL: {query}"}]
        })
        
        # 从结果中提取SQL
        sql = ""
        if result.get("messages"):
            last_msg = result["messages"][-1]
            sql = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        
        return {
            "current_stage": "sql_generation",
            "generated_sql": sql
        }
    
    def validate_sql_node(state: SQLMessageState) -> Dict[str, Any]:
        """验证SQL"""
        sql = state.get("generated_sql", "")
        
        result = quick_validate(sql)
        
        return {
            "current_stage": "sql_validation",
            "validation_result": result
        }
    
    def execute_sql_node(state: SQLMessageState) -> Dict[str, Any]:
        """执行SQL"""
        sql = state.get("generated_sql", "")
        connection_id = state.get("connection_id", 0)
        pagination = state.get("pagination", {})
        
        result = direct_execute(
            connection_id=connection_id,
            sql=sql,
            page=pagination.get("page", 1),
            page_size=pagination.get("page_size", 100)
        )
        
        return {
            "current_stage": "sql_execution",
            "execution_result": result
        }
    
    def should_execute(state: SQLMessageState) -> str:
        """决定是否执行SQL"""
        validation = state.get("validation_result", {})
        
        if validation.get("is_valid", False):
            return "execute"
        else:
            return "error"
    
    # 构建图
    builder = StateGraph(SQLMessageState)
    
    # 添加节点
    builder.add_node("analyze_schema", analyze_schema)
    builder.add_node("generate_sql", generate_sql)
    builder.add_node("validate_sql", validate_sql_node)
    builder.add_node("execute_sql", execute_sql_node)
    
    # 添加边
    builder.add_edge(START, "analyze_schema")
    builder.add_edge("analyze_schema", "generate_sql")
    builder.add_edge("generate_sql", "validate_sql")
    builder.add_conditional_edges(
        "validate_sql",
        should_execute,
        {
            "execute": "execute_sql",
            "error": END
        }
    )
    builder.add_edge("execute_sql", END)
    
    # 编译
    checkpointer = SqliteSaver.from_conn_string(db_path)
    store = InMemoryStore()
    
    graph = builder.compile(
        checkpointer=checkpointer,
        store=store
    )
    
    return graph


async def process_sql_query(
    query: str,
    connection_id: int = 0,
    thread_id: str = "default",
    user_id: str = "default",
    pagination: Optional[Dict[str, int]] = None,
    stream: bool = False
):
    """处理SQL查询的主入口函数
    
    Args:
        query: 用户查询
        connection_id: 数据库连接ID
        thread_id: 会话线程ID
        user_id: 用户ID
        pagination: 分页配置
        stream: 是否流式输出
        
    Returns:
        查询结果或流式迭代器
    """
    # 创建图
    app = create_simple_graph(connection_id)
    
    # 构建配置
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    # 构建输入
    input_state = {
        "messages": [{"role": "user", "content": query}],
        "connection_id": connection_id,
        "pagination": pagination or {"page": 1, "page_size": 100}
    }
    
    if stream:
        return app.astream(input_state, config, stream_mode="messages")
    else:
        return await app.ainvoke(input_state, config)


async def stream_sql_query(
    query: str,
    connection_id: int = 0,
    thread_id: str = "default",
    user_id: str = "default"
) -> AsyncIterator:
    """流式处理SQL查询
    
    Args:
        query: 用户查询
        connection_id: 数据库连接ID
        thread_id: 会话线程ID
        user_id: 用户ID
        
    Yields:
        流式事件
    """
    app = create_simple_graph(connection_id)
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    input_state = {
        "messages": [{"role": "user", "content": query}],
        "connection_id": connection_id
    }
    
    async for chunk in app.astream(input_state, config, stream_mode="messages"):
        yield chunk


# 导出图实例（用于langgraph.json）
app = None
stream_app = None


def get_app(connection_id: int = 0):
    """获取应用实例"""
    global app
    if app is None:
        app = create_simple_graph(connection_id)
    return app


def get_stream_app(connection_id: int = 0):
    """获取流式应用实例"""
    global stream_app
    if stream_app is None:
        stream_app = create_simple_graph(connection_id)
    return stream_app
