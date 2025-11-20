import os
import os
import sqlite3
import sys
import urllib.request
from pathlib import Path

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware

# 添加父目录到路径，以便导入自定义工具
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import init_chat_model  # 使用自定义的init_chat_model（支持硅基流动）
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_mcp_adapters.client import MultiServerMCPClient


def setup_database(db_path: Path) -> None:
    """自动下载并设置Chinook数据库"""
    db_url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"

    def get_tables():
        """验证数据库并返回表列表"""
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
os.environ["SILICONFLOW_API_KEY"] = "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
model = init_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")

# 设置数据库
db_path = Path(__file__).parent / "Chinook.db"
setup_database(db_path)

# 连接数据库
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

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

# 延迟加载MCP图表工具(避免模块加载时阻塞)
_chart_tools_cache = None
_agent_cache = None
_agent_hitl_cache = None

async def _get_chart_tools():
    """获取MCP图表工具(带缓存, 异步安全)"""
    global _chart_tools_cache
    if _chart_tools_cache is None:
        try:
            chart_tools = await MultiServerMCPClient(
                {
                    "mcp-server-chart": {
                        "command": "npx",
                        "args": ["-y", "@antv/mcp-server-chart"],
                        "transport": "stdio",
                    }
                }
            ).get_tools()
            _chart_tools_cache = chart_tools
            print(f"[成功] 加载了 {len(chart_tools)} 个图表工具")
        except Exception as e:
            print(f"[警告] MCP图表工具加载失败,仅使用SQL工具: {e}")
            _chart_tools_cache = []
    return _chart_tools_cache

async def _get_agent():
    """获取完整agent(带缓存, 首次调用时加载MCP工具)
    
    注意：checkpointer 和 store 由 langgraph.json 配置，LangGraph 服务器自动注入
    """
    global _agent_cache
    if _agent_cache is None:
        all_tools = tools + await _get_chart_tools()
        _agent_cache = create_agent(
            model,
            all_tools,
            system_prompt=system_prompt,
        )
    return _agent_cache

# 导出graph工厂函数(LangGraph API会调用此函数获取graph)
async def agent_old():
    """Agent工厂函数, 返回包含图表工具的agent"""
    return await _get_agent()


async def _get_agent_hitl():
    """获取带人工审核的agent
    
    注意：checkpointer 和 store 由 langgraph.json 配置，LangGraph 服务器自动注入
    """
    global _agent_hitl_cache
    if _agent_hitl_cache is None:
        all_tools = tools + await _get_chart_tools()
        _agent_hitl_cache = create_agent(
            model,
            all_tools,
            system_prompt=system_prompt,
            middleware=[
                HumanInTheLoopMiddleware(
                    interrupt_on={"sql_db_query": True},
                    description_prefix="SQL 调用等待审核",
                )
            ],
        )
    return _agent_hitl_cache


async def agent_hitl():
    return await _get_agent_hitl()
