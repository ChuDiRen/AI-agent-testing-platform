import os
import sqlite3
import sys
import urllib.request
from pathlib import Path

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import load_chat_model as init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase


def setup_database(db_path):
    db_url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_tables():
        if not db_path.exists():
            return []
        try:
            with sqlite3.connect(db_path) as conn:
                return conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        except Exception:
            return []

    if get_tables():
        return

    try:
        print(f"[Chinook] 正在下载数据库到: {db_path}")
        urllib.request.urlretrieve(db_url, db_path)
        if not get_tables():
            raise SystemExit(f"数据库下载失败，请手动下载: {db_url}")
        print(f"[Chinook] 下载完成: {db_path}")
    except Exception as e:
        raise SystemExit(f"数据库下载失败: {e}\n手动下载: {db_url}")


_model_cache = None
_db_cache = None
_toolkit_cache = None
_tools_cache = None
_agent_hitl_cache = None
_agent_cache = None
_checkpointer_cache = None
_store_cache = None

MEMORY_DB_PATH = Path(__file__).parent.parent.resolve() / "data" / "agent_memory.db"
CHECKPOINT_DB_PATH = Path(__file__).parent.parent.resolve() / "data" / "checkpoint.db"
STORE_DB_PATH = Path(__file__).parent.parent.resolve() / "data" / "store.db"


def _get_checkpointer():
    global _checkpointer_cache
    if _checkpointer_cache is None:
        CHECKPOINT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(CHECKPOINT_DB_PATH), check_same_thread=False)
        _checkpointer_cache = SqliteSaver(conn)
        _checkpointer_cache.setup()
        print(f"[成功] SQLite短期记忆已初始化: {CHECKPOINT_DB_PATH}")
    return _checkpointer_cache


def _get_store():
    global _store_cache
    if _store_cache is None:
        STORE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(STORE_DB_PATH), check_same_thread=False)
        _store_cache = SqliteStore(conn)
        _store_cache.setup()
        print(f"[成功] SQLite长期记忆存储已初始化: {STORE_DB_PATH}")
    return _store_cache


async def _ensure_model():
    global _model_cache
    if _model_cache is None:
        print("[模型] 延迟初始化 LLM 模型...")
        os.environ["SILICONFLOW_API_KEY"] = "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
        _model_cache = init_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")
        print("[模型] LLM 模型已初始化")
    return _model_cache


async def _ensure_database():
    global _db_cache, _toolkit_cache, _tools_cache
    if _db_cache is None:
        print("[数据库] 延迟初始化数据库连接...")
        db_path = Path(__file__).parent.parent.resolve() / "data" / "Chinook.db"
        setup_database(db_path)
        _db_cache = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        print("[数据库] Chinook示例数据库初始化中...")
        
        model = await _ensure_model()
        _toolkit_cache = SQLDatabaseToolkit(db=_db_cache, llm=model)
        _tools_cache = _toolkit_cache.get_tools()
        print(f"[工具] SQL 工具包已加载，包含 {len(_tools_cache)} 个工具")
    return _db_cache, _toolkit_cache, _tools_cache


async def _get_all_tools():
    _, _, sql_tools = await _ensure_database()
    all_tools = sql_tools
    print(f"[总计] 基础工具数量: {len(all_tools)} (SQL工具)")
    print("[优化] 图表工具已禁用，避免启动时的昂贵初始化")
    return all_tools


system_prompt = """
你是一个专门用于与SQL数据库交互的智能代理。
给定一个输入问题，创建一个语法正确的SQLite查询来运行，
然后查看查询结果并返回答案。

**【重要】必须严格按顺序执行以下4个步骤，一步都不能跳过**：

**【关键】每次调用工具前，必须先输出一句简短的步骤说明，格式如下**：
- 步骤1: 查询数据库表列表
- 步骤2: 获取表结构信息
- 步骤3: 执行 SQL 查询
- 步骤4: 分析结果并回答

步骤1（必须执行）：调用 sql_db_list_tables 工具，查看数据库中的所有表
- 这是第一步，必须先执行
- **在调用工具前，先输出**: "步骤1: 查询数据库表列表"

步骤2（必须执行）：调用 sql_db_schema 工具，查询相关表的结构
- 必须在步骤1之后执行
- **在调用工具前，先输出**: "步骤2: 获取表结构信息"

步骤3（必须执行）：调用 sql_db_query 工具，执行 SQL 查询
- 必须在步骤2之后执行
- 执行 SQL 查询
- **在调用工具前，先输出**: "步骤3: 执行 SQL 查询"

步骤4（必须执行）：分析查询结果并回答用户问题
- 必须在步骤3之后执行
- 基于查询结果提供清晰、准确的答案
- **在调用工具前，先输出**: "步骤4: 分析结果并回答"

【警告】如果跳过任何步骤或未输出步骤说明，将被视为任务失败。必须完整执行所有4个步骤。

**【严格】输出格式要求**：

1. 禁止使用代码块标记包裹普通文本
   ❌ 错误示例：```现在我来分析结果```
   ✅ 正确示例：现在我来分析结果

2. 只在展示代码时使用代码块
   ✅ 正确：展示 SQL 查询时使用 ```sql ... ```
   ❌ 错误：描述性文字使用 ``` ... ```

3. 输出风格
   - 必须输出简短的步骤说明
   - 简洁、直接、专业

【重要】普通文本绝对不能用 ``` 包裹！
"""


async def _get_agent():
    global _agent_cache
    if _agent_cache is None:
        print("[优化] 使用懒加载模式创建agent...")
        all_tools = await _get_all_tools()
        model = await _ensure_model()
        
        _agent_cache = create_agent(
            model,
            all_tools,
            system_prompt=system_prompt,
            checkpointer=_get_checkpointer(),
            store=_get_store(),
        )
        print("[成功] SQL Agent 已初始化（优化版本）")
    return _agent_cache


async def _get_agent_hitl():
    global _agent_hitl_cache
    if _agent_hitl_cache is None:
        print("[优化] 使用懒加载模式创建HITL agent...")
        all_tools = await _get_all_tools()
        model = await _ensure_model()
        
        _agent_hitl_cache = create_agent(
            model,
            all_tools,
            system_prompt=system_prompt,
            checkpointer=_get_checkpointer(),
            store=_get_store(),
            middleware=[
                HumanInTheLoopMiddleware(
                    interrupt_on={"sql_db_query": True},
                    description_prefix="SQL 调用等待审核",
                )
            ],
        )
        print("[成功] SQL Agent (HITL) 已初始化（优化版本）")
    return _agent_hitl_cache


async def agent_hitl():
    return await _get_agent_hitl()


async def agent():
    return await _get_agent()


if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent_instance = await agent_hitl()
        query = "查询每个客户的订单数量"
        print(f"\n🧪 测试查询: {query}")
        print("-" * 50)
        
        config = {"configurable": {"thread_id": "test-thread-1"}}
        
        for event in agent_instance.stream(
            {"messages": [HumanMessage(content=query)]},
            config,
            stream_mode="values",
        ):
            event["messages"][-1].pretty_print()
    
    asyncio.run(main())
