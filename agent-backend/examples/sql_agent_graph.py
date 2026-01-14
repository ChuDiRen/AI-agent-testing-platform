"""
SQL Agent Graph - 基于 StateGraph 的 SQL Agent

使用延迟初始化优化启动性能
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_chat_model  # 使用自定义的load_chat_model（支持硅基流动）
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode


async def setup_database(db_path: Path) -> None:
    """自动下载并设置 Chinook数据库 - 纯异步"""
    db_url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"

    # 确保 data 目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)

    async def get_tables():
        """验证数据库并返回表列表 - 异步"""
        if not db_path.exists():
            return []
        try:
            import aiosqlite
            async with aiosqlite.connect(db_path) as conn:
                cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                return await cursor.fetchall()
        except Exception:
            return []

    # 检查现有数据库
    if db_path.exists():
        tables = await get_tables()
        if tables:
            print(f"[Chinook] 数据库已存在: {db_path}")
            return

    # 下载数据库（异步）
    try:
        print(f"[Chinook] 正在下载数据库到: {db_path}")

        import aiohttp
        import aiofiles

        async with aiohttp.ClientSession() as session:
            async with session.get(db_url) as response:
                if response.status == 200:
                    async with aiofiles.open(db_path, 'wb') as f:
                        await f.write(await response.read())

                    if not await get_tables():
                        raise SystemExit(f"数据库下载失败，请手动下载: {db_url}")

                    print(f"[Chinook] 下载完成: {db_path}")
                else:
                    raise SystemExit(f"数据库下载失败: HTTP {response.status}")
    except Exception as e:
        raise SystemExit(f"数据库下载失败: {e}\n手动下载: {db_url}")


# ============== 延迟初始化配置 ==============
# 不在模块加载时初始化，而是在首次调用时初始化

db_path = Path(__file__).parent.parent.resolve() / "data" / "Chinook.db"

_llm_cache = None
_db_initialized = False
_db_cache = None
_toolkit_cache = None
_tools_cache = None
_graph_cache = None
_graph_with_interrupt_cache = None


def _get_llm():
    """获取 LLM 模型（带缓存）"""
    global _llm_cache
    if _llm_cache is None:
        os.environ["SILICONFLOW_API_KEY"] = "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
        _llm_cache = load_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")
    return _llm_cache


async def _ensure_database():
    """确保数据库已初始化（异步）"""
    global _db_initialized
    if not _db_initialized:
        await setup_database(db_path)
        _db_initialized = True
    return db_path


async def get_db_instance():
    """获取数据库实例（异步）"""
    global _db_cache
    if _db_cache is None:
        await _ensure_database()
        _db_cache = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    return _db_cache


async def get_toolkit():
    """获取工具包（异步）"""
    global _toolkit_cache
    if _toolkit_cache is None:
        db = await get_db_instance()
        _toolkit_cache = SQLDatabaseToolkit(db=db, llm=_get_llm())
    return _toolkit_cache


async def _get_tools():
    """获取工具列表（异步）"""
    global _tools_cache
    if _tools_cache is None:
        toolkit = await get_toolkit()
        _tools_cache = toolkit.get_tools()
    return _tools_cache


def list_tables(state: MessagesState):
    """示例：创建一个预定义的工具调用"""
    tool_call = {"name": "sql_db_list_tables", "args": {}, "id": "abc123", "type": "tool_call"}
    tool_call_message = AIMessage(content="步骤1: 查询数据库中的所有表", tool_calls=[tool_call])

    # 使用缓存的工具
    tools = _tools_cache or []
    if not tools:
        # 如果缓存为空，尝试同步获取
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 在运行的事件循环中，使用 run_coroutine_threadsafe
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(_get_tools(), loop)
                tools = future.result(timeout=30)
            else:
                tools = asyncio.run(_get_tools())
        except Exception:
            tools = asyncio.run(_get_tools())
    
    list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
    tool_message = list_tables_tool.invoke(tool_call)
    response = AIMessage(f"可用的表: {tool_message.content}")

    return {"messages": [tool_call_message, tool_message, response]}


def call_get_schema(state: MessagesState):
    """示例：强制模型创建工具调用"""
    tools = _tools_cache or []
    if not tools:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(_get_tools(), loop)
                tools = future.result(timeout=30)
            else:
                tools = asyncio.run(_get_tools())
        except Exception:
            tools = asyncio.run(_get_tools())
    
    get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")

    llm_with_tools = _get_llm().bind_tools([get_schema_tool])
    response = llm_with_tools.invoke(state["messages"])
    # 为响应添加描述性文本
    if response.content == "":
        response.content = "步骤2: 获取相关表的结构信息"
    return {"messages": [response]}


generate_query_system_prompt = """
你是一个专门用于与SQL数据库交互的智能代理。
给定一个输入问题，创建一个语法正确的sqlite查询来运行，
然后查看查询结果并返回答案。除非用户指定了希望获取的具体示例数量，
否则始终将查询结果限制在最多5条。

你可以按相关列对结果进行排序，以返回数据库中最有趣的示例。
永远不要查询特定表的所有列，只查询问题中相关的列。

不要对数据库执行任何DML语句（INSERT、UPDATE、DELETE、DROP等）。

**【严格】输出格式要求**：
- 禁止使用 ``` 包裹普通文本
- 只在展示 SQL 代码时使用代码块
- 避免"现在我..."等过程描述
- 直接、简洁、专业
- **生成图表后，必须在回答中使用 ![图表](URL) 展示图表**
"""


def generate_query(state: MessagesState):
    system_message = {"role": "system", "content": generate_query_system_prompt}

    tools = _tools_cache or []
    if not tools:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(_get_tools(), loop)
                tools = future.result(timeout=30)
            else:
                tools = asyncio.run(_get_tools())
        except Exception:
            tools = asyncio.run(_get_tools())
    
    run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")

    llm_with_tools = _get_llm().bind_tools([run_query_tool])
    response = llm_with_tools.invoke([system_message] + state["messages"])
    # 为响应添加描述性文本(如果没有内容)
    if response.content == "" and response.tool_calls:
        response.content = "步骤3: 生成并准备执行 SQL 查询"
    return {"messages": [response]}


check_query_system_prompt = """
你是一位非常注重细节的SQL专家。
仔细检查sqlite查询中的常见错误，包括：
- 在NULL值中使用NOT IN
- 应该使用UNION ALL时却使用了UNION
- 对独占范围使用BETWEEN
- 谓词中的数据类型不匹配
- 正确引用标识符
- 为函数使用正确数量的参数
- 转换为正确的数据类型
- 在连接中使用正确的列

如果存在上述任何错误，请重写查询。如果没有错误，
只需重现原始查询。

在运行此检查后，你将调用适当的工具来执行查询。
"""


def check_query(state: MessagesState):
    system_message = {"role": "system", "content": check_query_system_prompt}
    tool_call = state["messages"][-1].tool_calls[0]
    user_message = {"role": "user", "content": tool_call["args"]["query"]}

    tools = _tools_cache or []
    if not tools:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(_get_tools(), loop)
                tools = future.result(timeout=30)
            else:
                tools = asyncio.run(_get_tools())
        except Exception:
            tools = asyncio.run(_get_tools())
    
    run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")

    llm_with_tools = _get_llm().bind_tools([run_query_tool])
    response = llm_with_tools.invoke([system_message, user_message])
    response.id = state["messages"][-1].id
    return {"messages": [response]}


def should_continue(state: MessagesState) -> Literal[END, "check_query"]:
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END
    else:
        return "check_query"


async def _build_graph():
    """构建图（异步）"""
    global _tools_cache
    
    # 预加载工具到缓存
    tools = await _get_tools()
    _tools_cache = tools

    get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
    get_schema_node = ToolNode([get_schema_tool], name="get_schema")

    run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
    run_query_node = ToolNode([run_query_tool], name="run_query")

    builder = StateGraph(MessagesState)
    builder.add_node(list_tables)
    builder.add_node(call_get_schema)
    builder.add_node(get_schema_node, "get_schema")
    builder.add_node(generate_query)
    builder.add_node(check_query)
    builder.add_node(run_query_node, "run_query")

    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    builder.add_conditional_edges("generate_query", should_continue)
    builder.add_edge("check_query", "run_query")
    builder.add_edge("run_query", "generate_query")

    return builder.compile()


async def get_graph():
    """获取图实例（异步）"""
    global _graph_cache
    if _graph_cache is None:
        _graph_cache = await _build_graph()
    return _graph_cache


from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.types import interrupt, Command


async def _get_run_query_tool():
    """获取 run_query_tool（异步）"""
    tools = await _get_tools()
    return next(tool for tool in tools if tool.name == "sql_db_query")


@tool
async def run_query_tool_with_interrupt(config: RunnableConfig, query: str):
    """带中断功能的查询工具（异步）"""
    run_query_tool = await _get_run_query_tool()

    request = {"action": run_query_tool.name, "args": {"query": query}, "description": "Please review the tool call"}
    response = interrupt([request])
    decision = response[0] if isinstance(response, list) else response

    if decision["type"] == "accept":
        tool_response = run_query_tool.invoke({"query": query}, config)
    elif decision["type"] == "edit":
        query = decision["args"]["args"]["query"]
        tool_response = run_query_tool.invoke({"query": query}, config)
    elif decision["type"] == "response":
        user_feedback = decision["args"]
        tool_response = user_feedback
    else:
        raise ValueError(f"Unsupported interrupt response type: {decision['type']}")

    return tool_response


def should_continue_interrupt(state: MessagesState) -> Literal[END, "run_query"]:
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END
    else:
        return "run_query"


async def _build_graph_with_interrupt():
    """构建带中断功能的图（异步优化版本）"""
    global _tools_cache
    
    # 使用懒加载模式，避免启动时的昂贵初始化
    print("[优化] 使用懒加载模式构建图...")
    
    # 延迟工具初始化
    async def _lazy_get_tools():
        global _tools_cache
        if _tools_cache is None:
            print("[工具] 延迟初始化工具...")
            _tools_cache = await _get_tools()
            print(f"[工具] 工具初始化完成，共 {len(_tools_cache)} 个工具")
        return _tools_cache
    
    # 动态获取工具
    tools = await _lazy_get_tools()
    
    get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
    get_schema_node = ToolNode([get_schema_tool], name="get_schema")
    
    run_query_node_with_interrupt = ToolNode([run_query_tool_with_interrupt], name="run_query")

    builder = StateGraph(MessagesState)
    builder.add_node(list_tables)
    builder.add_node(call_get_schema)
    builder.add_node(get_schema_node, "get_schema")
    builder.add_node(generate_query)
    builder.add_node(run_query_node_with_interrupt, "run_query")

    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    builder.add_conditional_edges("generate_query", should_continue_interrupt)
    builder.add_edge("run_query", "generate_query")

    print("[成功] 图构建完成（懒加载模式）!")
    return builder.compile()


async def get_graph_with_interrupt():
    """获取带中断功能的图实例（异步）"""
    global _graph_with_interrupt_cache
    if _graph_with_interrupt_cache is None:
        _graph_with_interrupt_cache = await _build_graph_with_interrupt()
    return _graph_with_interrupt_cache


async def run_old():
    """运行旧版 Agent"""
    from IPython.display import Image, display
    agent = await get_graph()
    display(Image(agent.get_graph().draw_mermaid_png()))
    question = "哪个音乐类型的曲目平均时长最长？"

    for step in agent.stream({"messages": [HumanMessage(content=question)]}, stream_mode="values"):
        step["messages"][-1].pretty_print()


async def run_new():
    """运行带持久化和人工审核的 Agent"""
    question = "哪个音乐类型的曲目平均时长最长？"
    config = {"configurable": {"thread_id": "1"}}

    agent_new_instance = await get_graph_with_interrupt()

    interrupted = False
    for step in agent_new_instance.stream({"messages": [HumanMessage(content=question)]}, config, stream_mode="values"):
        if "messages" in step:
            step["messages"][-1].pretty_print()
        elif "__interrupt__" in step:
            print("检测到中断:")
            interrupt_data = step["__interrupt__"][0]
            for request in interrupt_data.value:
                print(f"  - {request['description']}")
                print(f"  - 工具: {request['action']}")
                print(f"  - 参数: {request['args']}")
            interrupted = True
            break
        else:
            pass

    while interrupted:
        print("\n等待3秒后自动恢复执行...")
        await asyncio.sleep(3)
        print("恢复执行中...\n")

        interrupted = False

        for step in agent_new_instance.stream(Command(resume=[{"type": "accept"}]), config, stream_mode="values"):
            if "messages" in step:
                step["messages"][-1].pretty_print()
            elif "__interrupt__" in step:
                print("再次检测到中断:")
                interrupt_data = step["__interrupt__"][0]
                for request in interrupt_data.value:
                    print(f"  - {request['description']}")
                    print(f"  - 工具: {request['action']}")
                    print(f"  - 参数: {request['args']}")
                interrupted = True
                break
            else:
                pass

    print("\n✅ 所有任务执行完成!")


if __name__ == '__main__':
    asyncio.run(run_old())
    # asyncio.run(run_new())
