import asyncio
import os
import sqlite3
import urllib.request
from contextlib import suppress
from pathlib import Path
from typing import Literal

from langchain.chat_models import init_chat_model

from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode


def setup_database(db_path: Path) -> None:
    """自动下载并设置Chinook数据库"""
    db_url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"

    def get_tables():
        """验证数据库并返回表列表"""
        with suppress(Exception):
            with sqlite3.connect(db_path) as conn:
                return conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

    # 检查现有数据库
    if get_tables():
        return

    # 下载数据库
    try:
        urllib.request.urlretrieve(db_url, db_path)
        if not get_tables():
            raise SystemExit(f"数据库下载失败，请手动下载: {db_url}")
    except Exception as e:
        raise SystemExit(f"数据库下载失败: {e}\n手动下载: {db_url}")


# 初始化
os.environ["DEEPSEEK_API_KEY"] = "sk-f79fae69b11a4fce88e04805bd6314b7"
llm = init_chat_model("deepseek:deepseek-chat")

# 设置数据库
db_path = Path(__file__).parent / "Chinook.db"
setup_database(db_path)

# 连接数据库
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()
for tool in tools:
    print(f"{tool.name}: {tool.description}\n")

get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
get_schema_node = ToolNode([get_schema_tool], name="get_schema")

run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
run_query_node = ToolNode([run_query_tool], name="run_query")


# 示例：创建一个预定义的工具调用
def list_tables(state: MessagesState):
    tool_call = {
        "name": "sql_db_list_tables",
        "args": {},
        "id": "abc123",
        "type": "tool_call",
    }
    tool_call_message = AIMessage(content="", tool_calls=[tool_call])

    list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
    tool_message = list_tables_tool.invoke(tool_call)
    response = AIMessage(f"可用的表: {tool_message.content}")

    return {"messages": [tool_call_message, tool_message, response]}


# 示例：强制模型创建工具调用
def call_get_schema(state: MessagesState):
    # 注意：LangChain强制所有模型接受 `tool_choice="any"`
    # 以及 `tool_choice=<工具名称字符串>`。
    llm_with_tools = llm.bind_tools([get_schema_tool], tool_choice="any")
    response = llm_with_tools.invoke(state["messages"])

    return {"messages": [response]}


generate_query_system_prompt = """
你是一个专门用于与SQL数据库交互的智能代理。
给定一个输入问题，创建一个语法正确的{dialect}查询来运行，
然后查看查询结果并返回答案。除非用户指定了希望获取的具体示例数量，
否则始终将查询结果限制在最多{top_k}条。

你可以按相关列对结果进行排序，以返回数据库中最有趣的示例。
永远不要查询特定表的所有列，只查询问题中相关的列。

不要对数据库执行任何DML语句（INSERT、UPDATE、DELETE、DROP等）。
""".format(
    dialect=db.dialect,
    top_k=5,
)


def generate_query(state: MessagesState):
    system_message = {
        "role": "system",
        "content": generate_query_system_prompt,
    }
    # 我们在这里不强制工具调用，以允许模型在获得解决方案时自然响应。
    llm_with_tools = llm.bind_tools([run_query_tool])
    response = llm_with_tools.invoke([system_message] + state["messages"])

    return {"messages": [response]}


check_query_system_prompt = """
你是一位非常注重细节的SQL专家。
仔细检查{dialect}查询中的常见错误，包括：
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
""".format(dialect=db.dialect)


def check_query(state: MessagesState):
    system_message = {
        "role": "system",
        "content": check_query_system_prompt,
    }

    # 生成一个人工用户消息来检查
    tool_call = state["messages"][-1].tool_calls[0]
    user_message = {"role": "user", "content": tool_call["args"]["query"]}
    llm_with_tools = llm.bind_tools([run_query_tool], tool_choice="any")
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
builder.add_conditional_edges(
    "generate_query",
    should_continue,
)
builder.add_edge("check_query", "run_query")
builder.add_edge("run_query", "generate_query")

agent_old = builder.compile()

from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.types import interrupt, Command


@tool(
    run_query_tool.name,
    description=run_query_tool.description,
    args_schema=run_query_tool.args_schema
)
def run_query_tool_with_interrupt(config: RunnableConfig, **tool_input):
    request = {
        "action": run_query_tool.name,
        "args": tool_input,
        "description": "Please review the tool call"
    }
    response = interrupt([request])
    # interrupt() 返回的是列表，取第一个元素
    decision = response[0] if isinstance(response, list) else response
    
    # approve the tool call
    if decision["type"] == "accept":
        tool_response = run_query_tool.invoke(tool_input, config)
    # update tool call args
    elif decision["type"] == "edit":
        tool_input = decision["args"]["args"]
        tool_response = run_query_tool.invoke(tool_input, config)
    # respond to the LLM with user feedback
    elif decision["type"] == "response":
        user_feedback = decision["args"]
        tool_response = user_feedback
    else:
        raise ValueError(f"Unsupported interrupt response type: {decision['type']}")

    return tool_response


from langgraph.checkpoint.memory import InMemorySaver


def should_continue(state: MessagesState) -> Literal[END, "run_query"]:
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END
    else:
        return "run_query"


# 创建带中断功能的工具节点
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
builder.add_conditional_edges(
    "generate_query",
    should_continue,
)
builder.add_edge("run_query", "generate_query")

checkpointer = InMemorySaver()
agent_new = builder.compile(checkpointer=checkpointer)


async def run_old():
    from IPython.display import Image, display

    display(Image(agent_old.get_graph().draw_mermaid_png()))
    question = "哪个音乐类型的曲目平均时长最长？"

    for step in agent_old.stream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="values",
    ):
        step["messages"][-1].pretty_print()


async def run_new():
    question = "哪个音乐类型的曲目平均时长最长？"

    config = {"configurable": {"thread_id": "1"}}

    # 第一次执行，直到遇到中断
    interrupted = False
    for step in agent_new.stream(
            {"messages": [{"role": "user", "content": question}]},
            config,
            stream_mode="values",
    ):
        if "messages" in step:
            step["messages"][-1].pretty_print()
        elif "__interrupt__" in step:
            print("检测到中断:")
            interrupt = step["__interrupt__"][0]
            # interrupt.value 本身就是请求列表
            for request in interrupt.value:
                print(f"  - {request['description']}")
                print(f"  - 工具: {request['action']}")
                print(f"  - 参数: {request['args']}")
            interrupted = True
            break
        else:
            pass

    # 循环处理所有中断，每次中断都等待3秒后自动恢复
    while interrupted:
        print("\n等待3秒后自动恢复执行...")
        await asyncio.sleep(3)
        print("恢复执行中...\n")

        interrupted = False  # 重置中断标志

        # 恢复执行
        for step in agent_new.stream(
                Command(resume=[{"type": "accept"}]),
                config,
                stream_mode="values",
        ):
            if "messages" in step:
                step["messages"][-1].pretty_print()
            elif "__interrupt__" in step:
                print("再次检测到中断:")
                interrupt = step["__interrupt__"][0]
                # interrupt.value 本身就是请求列表
                for request in interrupt.value:
                    print(f"  - {request['description']}")
                    print(f"  - 工具: {request['action']}")
                    print(f"  - 参数: {request['args']}")
                interrupted = True  # 设置中断标志，继续循环
                break
            else:
                pass

    print("\n✅ 所有任务执行完成！")


if __name__ == '__main__':
    asyncio.run(run_old())
    # asyncio.run(run_new())
