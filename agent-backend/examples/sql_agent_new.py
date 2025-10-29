import os
import sqlite3
import urllib.request
from pathlib import Path
from contextlib import suppress
from typing import Literal
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_community.utilities import SQLDatabase
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.types import interrupt
from langgraph.checkpoint.memory import InMemorySaver


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

get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
get_schema_node = ToolNode([get_schema_tool], name="get_schema")

run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")


def list_tables(state: MessagesState):
    """列出所有数据库表"""
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


def call_get_schema(state: MessagesState):
    """强制模型调用获取表结构的工具"""
    llm_with_tools = llm.bind_tools([get_schema_tool], tool_choice="any")
    response = llm_with_tools.invoke(state["messages"])

    return {"messages": [response]}


generate_query_system_prompt = """
你是一个专门与SQL数据库交互的智能助手。
根据用户的问题，创建一个语法正确的 {dialect} 查询来执行，然后查看查询结果并返回答案。
除非用户指定了具体的结果数量，否则请将查询结果限制在最多 {top_k} 条。

你可以通过相关列对结果进行排序，以返回数据库中最有趣的示例。
永远不要查询表中的所有列，只查询问题所需的相关列。

禁止执行任何DML语句（INSERT、UPDATE、DELETE、DROP等）来修改数据库。
""".format(
    dialect=db.dialect,
    top_k=5,
)


def generate_query(state: MessagesState):
    """生成SQL查询"""
    system_message = {
        "role": "system",
        "content": generate_query_system_prompt,
    }
    # 不强制工具调用，允许模型在获得解决方案时自然响应
    llm_with_tools = llm.bind_tools([run_query_tool])
    response = llm_with_tools.invoke([system_message] + state["messages"])

    return {"messages": [response]}


check_query_system_prompt = """
你是一位细致入微的SQL专家。
请仔细检查这个 {dialect} 查询是否存在以下常见错误：
- 对NULL值使用NOT IN
- 应该使用UNION ALL却使用了UNION
- 对独占范围使用BETWEEN
- 谓词中的数据类型不匹配
- 标识符引号使用不当
- 函数参数数量错误
- 数据类型转换错误
- 连接使用了错误的列

如果存在上述任何错误，请重写查询。如果没有错误，只需重现原始查询。

检查完成后，你将调用相应的工具来执行查询。
""".format(dialect=db.dialect)


def check_query(state: MessagesState):
    """检查并优化SQL查询"""
    system_message = {
        "role": "system",
        "content": check_query_system_prompt,
    }

    # 生成用于检查的人工用户消息
    tool_call = state["messages"][-1].tool_calls[0]
    user_message = {"role": "user", "content": tool_call["args"]["query"]}
    llm_with_tools = llm.bind_tools([run_query_tool], tool_choice="any")
    response = llm_with_tools.invoke([system_message, user_message])
    response.id = state["messages"][-1].id

    return {"messages": [response]}


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
    # approve the tool call
    if response["type"] == "accept":
        tool_response = run_query_tool.invoke(tool_input, config)
    # update tool call args
    elif response["type"] == "edit":
        tool_input = response["args"]["args"]
        tool_response = run_query_tool.invoke(tool_input, config)
    # respond to the LLM with user feedback
    elif response["type"] == "response":
        user_feedback = response["args"]
        tool_response = user_feedback
    else:
        raise ValueError(f"Unsupported interrupt response type: {response['type']}")

    return tool_response


# 使用带人机交互的工具节点 # 关键修改：启用人机交互
run_query_node = ToolNode([run_query_tool_with_interrupt], name="run_query")


def should_continue(state: MessagesState) -> Literal[END, "check_query"]:  # 修改：路由到check_query而不是直接run_query
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END
    else:
        return "check_query"  # 先进行程序化检查


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

# 条件性编译：部署环境不使用checkpointer，本地测试使用 # 关键修改：兼容LangGraph API部署

graph = builder.compile()

# 本地测试环境，需要checkpointer支持人机交互
# checkpointer = InMemorySaver()
# graph = builder.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    """本地测试入口 - 支持人机交互"""
    pass

    # import json
    # from langgraph.types import Command
    #
    # config = {"configurable": {"thread_id": "1"}}
    # question = "哪个音乐类型的平均曲目时长最长？"
    #
    # print("=" * 80)
    # print("SQL Agent 双重检查模式 - 人机交互演示")
    # print("=" * 80)
    # print(f"问题: {question}\n")
    #
    # # 第一阶段：运行到中断点
    # interrupted = False
    # for step in graph.stream(  # 使用graph而不是agent
    #         {"messages": [{"role": "user", "content": question}]},
    #         config,
    #         stream_mode="values",
    # ):
    #     if "messages" in step:
    #         step["messages"][-1].pretty_print()
    #     elif "__interrupt__" in step:
    #         action = step["__interrupt__"][0]
    #         print("\n" + "=" * 80)
    #         print("⚠️  需要人工审核 SQL 查询")
    #         print("=" * 80)
    #         for request in action.value:
    #             print(json.dumps(request, indent=2, ensure_ascii=False))
    #         interrupted = True
    #         break
    #
    # # 第二阶段：人工决策
    # if interrupted:
    #     print("\n" + "=" * 80)
    #     print("请选择操作:")
    #     print("  1 - 接受查询 (accept)")
    #     print("  2 - 编辑查询 (edit)")
    #     print("  3 - 拒绝并反馈 (response)")
    #     print("=" * 80)
    #
    #     choice = input("请输入选项 (1/2/3，直接回车默认接受): ").strip()
    #
    #     if choice == "2":
    #         # 编辑模式
    #         print("\n当前查询:")
    #         print(action.value[0]["args"]["query"])
    #         new_query = input("\n请输入修改后的查询: ").strip()
    #         resume_value = {
    #             "type": "edit",
    #             "args": {"args": {"query": new_query}}
    #         }
    #     elif choice == "3":
    #         # 拒绝模式
    #         feedback = input("\n请输入反馈信息: ").strip()
    #         resume_value = {
    #             "type": "response",
    #             "args": feedback
    #         }
    #     else:
    #         # 默认接受
    #         resume_value = {"type": "accept"}
    #
    #     print("\n" + "=" * 80)
    #     print(f"执行决策: {resume_value['type']}")
    #     print("=" * 80 + "\n")
    #
    #     # 继续执行
    #     for step in graph.stream(  # 使用graph而不是agent
    #         Command(resume=resume_value),
    #         config,
    #         stream_mode="values",
    #     ):
    #         if "messages" in step:
    #             step["messages"][-1].pretty_print()
    #
    #     print("\n" + "=" * 80)
    #     print("✅ 执行完成")
    #     print("=" * 80)
