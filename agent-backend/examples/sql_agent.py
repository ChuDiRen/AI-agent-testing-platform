import os
import os
import sqlite3
import sys
import urllib.request
from pathlib import Path

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.sqlite import SqliteSaver  # SQLite短期记忆
from langgraph.store.sqlite import SqliteStore  # SQLite长期记忆

# 添加当前目录到路径,以便导入自定义工具
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import init_chat_model  # 使用自定义的init_chat_model(支持硅基流动)
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_mcp_adapters.client import MultiServerMCPClient


def setup_database(db_path: Path) -> None:
    """自动下载并设置Chinook数据库"""
    db_url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"

    # 确保 data 目录存在（必须在连接数据库前创建）
    db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_tables():
        """验证数据库并返回表列表"""
        if not db_path.exists():
            return []
        try:
            with sqlite3.connect(db_path) as conn:
                return conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        except Exception:
            return []

    # 检查现有数据库
    if get_tables():
        return

    # 下载数据库
    try:
        print(f"[Chinook] 正在下载数据库到: {db_path}")
        urllib.request.urlretrieve(db_url, db_path)
        if not get_tables():
            raise SystemExit(f"数据库下载失败，请手动下载: {db_url}")
        print(f"[Chinook] 下载完成: {db_path}")
    except Exception as e:
        raise SystemExit(f"数据库下载失败: {e}\n手动下载: {db_url}")


# 初始化
os.environ["SILICONFLOW_API_KEY"] = "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
model = init_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")

# 设置数据库 - 使用 resolve() 规范化路径
db_path = Path(__file__).parent.parent.resolve() / "data" / "Chinook.db"
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

**【重要】必须严格按顺序执行以下5个步骤，一步都不能跳过**：

**【关键】每次调用工具前，必须先输出一句简短的步骤说明，格式如下**：
- 步骤1: 查询数据库表列表
- 步骤2: 获取表结构信息
- 步骤3: 执行 SQL 前的检查
- 步骤4: 执行 SQL 查询
- 步骤5: 生成数据可视化图表

步骤1（必须执行）：调用 sql_db_list_tables 工具，查看数据库中的所有表
- 这是第一步，必须先执行
- 即使你认为知道有哪些表，也必须执行此步骤
- **在调用工具前，先输出**: "步骤1: 查询数据库表列表"

步骤2（必须执行）：调用 sql_db_schema 工具，查询相关表的结构
- 必须在步骤1之后执行
- 即使你认为知道表结构，也必须执行此步骤
- **在调用工具前，先输出**: "步骤2: 获取表结构信息"

步骤3（必须执行）：调用 sql_db_query_checker 工具，检查 SQL 查询的正确性
- 必须在步骤2之后执行
- 用于验证 SQL 语法和逻辑错误
- **在调用工具前，先输出**: "步骤3: 执行 SQL 前的检查"

步骤4（必须执行）：调用 sql_db_query 工具，执行 SQL 查询
- 必须在步骤3之后执行
- 执行经过检查的 SQL 查询
- **在调用工具前，先输出**: "步骤4: 执行 SQL 查询"

步骤5（必须执行）：使用图表工具可视化数据
- 必须在步骤4之后执行
- 使用 generate_column_chart、generate_bar_chart 等工具
- 这是最后一步，必须执行
- **在调用工具前，先输出**: "步骤5: 生成数据可视化图表"
- **重要**：生成图表后，必须在最终回答中包含图表链接，格式为：![图表](图表URL)

【警告】如果跳过任何步骤或未输出步骤说明，将被视为任务失败。必须完整执行所有5个步骤。

【图表展示要求】：
- 生成图表后，必须在回答中使用 Markdown 图片语法展示图表
- 格式：![图表描述](图表URL)
- 示例：![各音乐类型平均时长](https://mdn.alipayobjects.com/.../original)

**【严格】输出格式要求**：

1. 禁止使用代码块标记包裹普通文本
   ❌ 错误示例：```现在我用柱状图来可视化这个结果```
   ✅ 正确示例：现在我用柱状图来可视化这个结果

2. 只在展示代码时使用代码块
   ✅ 正确：展示 SQL 查询时使用 ```sql ... ```
   ❌ 错误：描述性文字使用 ``` ... ```

3. 输出风格
   - 必须输出简短的步骤说明（如"步骤1: 查询数据库表列表"）
   - 避免冗长的过程描述（如"现在我正在分析..."、"接下来我将要..."）
   - 简洁、直接、专业

【重要】普通文本绝对不能用 ``` 包裹！
""".format(
    dialect=db.dialect,
    top_k=5,
)

# 延迟加载MCP图表工具(避免模块加载时阻塞)
_chart_tools_cache = None
_agent_cache = None
_agent_hitl_cache = None
_checkpointer_cache = None  # SQLite短期记忆缓存
_store_cache = None  # 长期记忆存储缓存

# 统一的记忆数据库路径 - 使用 resolve() 规范化路径
MEMORY_DB_PATH = Path(__file__).parent.parent.resolve() / "data" / "agent_memory.db"

def _get_checkpointer():
    """获取SQLite短期记忆(带缓存)"""
    global _checkpointer_cache
    if _checkpointer_cache is None:
        # 确保 data 目录存在
        MEMORY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建 SQLite 连接并初始化 SqliteSaver
        conn = sqlite3.connect(str(MEMORY_DB_PATH), check_same_thread=False)
        _checkpointer_cache = SqliteSaver(conn)
        _checkpointer_cache.setup()  # 初始化表结构
        print(f"[成功] SQLite短期记忆已初始化: {MEMORY_DB_PATH}")
    return _checkpointer_cache

def _get_store():
    """获取SQLite长期记忆存储(带缓存)"""
    global _store_cache
    if _store_cache is None:
        # 确保 data 目录存在
        MEMORY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建 SQLite 连接并初始化 SqliteStore
        conn = sqlite3.connect(str(MEMORY_DB_PATH), check_same_thread=False)
        _store_cache = SqliteStore(conn)
        _store_cache.setup()  # 初始化表结构
        print(f"[成功] SQLite长期记忆存储已初始化: {MEMORY_DB_PATH}")
    return _store_cache

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
    
    配置短期记忆(checkpointer)和长期记忆(store)
    """
    global _agent_cache
    if _agent_cache is None:
        all_tools = tools + await _get_chart_tools()
        _agent_cache = create_agent(
            model,
            all_tools,
            system_prompt=system_prompt,
            checkpointer=_get_checkpointer(),  # SQLite短期记忆
            store=_get_store(),  # 长期记忆存储
        )
        print("[成功] SQL Agent 已初始化（含图表工具）")
    return _agent_cache


# 导出graph工厂函数(LangGraph API会调用此函数获取graph)
async def agent_old():
    """Agent工厂函数, 返回包含图表工具的agent"""
    return await _get_agent()


async def _get_agent_hitl():
    """获取带人工审核的agent
    
    配置短期记忆(checkpointer)和长期记忆(store)
    """
    global _agent_hitl_cache
    if _agent_hitl_cache is None:
        all_tools = tools + await _get_chart_tools()
        _agent_hitl_cache = create_agent(
            model,
            all_tools,
            system_prompt=system_prompt,
            checkpointer=_get_checkpointer(),  # SQLite短期记忆
            store=_get_store(),  # 长期记忆存储
            middleware=[
                HumanInTheLoopMiddleware(
                    interrupt_on={"sql_db_query": True},
                    description_prefix="SQL 调用等待审核",
                )
            ],
        )
        print("[成功] SQL Agent (HITL) 已初始化")
    return _agent_hitl_cache


async def agent_hitl():
    """Agent HITL 工厂函数"""
    return await _get_agent_hitl()
