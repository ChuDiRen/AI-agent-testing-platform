import asyncio
import os
import sqlite3
import urllib.request
from contextlib import suppress
from pathlib import Path

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.types import Command


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
model = init_chat_model("deepseek:deepseek-chat")

# 设置数据库
db_path = Path(__file__).parent / "Chinook.db"
setup_database(db_path)

# 连接数据库
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

# 加载 MCP 图表工具
chart_tools = asyncio.run(
    MultiServerMCPClient(
        {
            "mcp-server-chart": {
                "command": "npx",
                "args": ["-y", "@antv/mcp-server-chart"],
                "transport": "stdio",
            }
        }
    ).get_tools()
)
# 合并 SQL 工具和图表工具
tools = tools + chart_tools

# 配置 SQLite Checkpointer 用于持久化对话状态
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# 使用 SQLite 数据库存储 checkpoint（对话状态、中断等）
checkpoint_db_path = Path(__file__).parent / "checkpoints.db"

system_prompt = """
你是一个专门用于与SQL数据库交互的智能代理。
给定一个输入问题，创建一个语法正确的{dialect}查询来运行，
然后查看查询结果并返回答案。除非用户指定了希望获取的具体示例数量，
否则始终将查询结果限制在最多{top_k}条。

你可以按相关列对结果进行排序，以返回数据库中最有趣的示例。
永远不要查询特定表的所有列，只查询问题中相关的列。

在执行查询之前，你必须仔细检查你的查询。如果在执行查询时遇到错误，
请重写查询并重试。

不要对数据库执行任何DML语句（INSERT、UPDATE、DELETE、DROP等）。

首先，你应该始终查看数据库中的表，以了解可以查询什么。不要跳过此步骤。

然后，你应该查询最相关表的架构。
根据生成的数据特点，你一定要使用图表工具来可视化数据。
""".format(
    dialect=db.dialect,
    top_k=5,
)

# 创建 Agent（无持久化，用于简单测试）
agent_old = create_agent(
    model,
    tools,
    system_prompt=system_prompt,
)


async def run_old():
    question = "哪个音乐类型的曲目平均时长最长？"

    async for step in agent_old.astream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="values",
    ):
        step["messages"][-1].pretty_print()


async def run_new():
    """运行带持久化和人工审核的 Agent"""
    question = "哪个音乐类型的曲目平均时长最长？"

    config = {"configurable": {"thread_id": "1"}}

    # 使用 AsyncSqliteSaver 作为 checkpointer
    async with AsyncSqliteSaver.from_conn_string(str(checkpoint_db_path)) as checkpointer:
        # 创建 Agent（带 SQLite 持久化和人工审核中断）
        agent_new = create_agent(
            model,
            tools,
            system_prompt=system_prompt,
            checkpointer=checkpointer,  # 启用 SQLite 持久化
            middleware=[
                HumanInTheLoopMiddleware(
                    interrupt_on={"sql_db_query": True},
                    description_prefix="Tool execution pending approval",
                ),
            ],
        )

        # 第一次执行，直到遇到中断
        interrupted = False
        async for step in agent_new.astream(
                {"messages": [{"role": "user", "content": question}]},
                config,
                stream_mode="values",
        ):
            if "messages" in step:
                step["messages"][-1].pretty_print()
            elif "__interrupt__" in step:
                print("检测到中断:")
                interrupt = step["__interrupt__"][0]
                for request in interrupt.value["action_requests"]:
                    print(f"  - {request['description']}")
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
            async for step in agent_new.astream(
                    Command(resume={"decisions": [{"type": "approve"}]}),
                    config,
                    stream_mode="values",
            ):
                if "messages" in step:
                    step["messages"][-1].pretty_print()
                elif "__interrupt__" in step:
                    print("再次检测到中断:")
                    interrupt = step["__interrupt__"][0]
                    for request in interrupt.value["action_requests"]:
                        print(f"  - {request['description']}")
                    interrupted = True  # 设置中断标志，继续循环
                    break
                else:
                    pass

        print("\n✅ 所有任务执行完成！")


if __name__ == '__main__':
    asyncio.run(run_new())
    # asyncio.run(run_new())
