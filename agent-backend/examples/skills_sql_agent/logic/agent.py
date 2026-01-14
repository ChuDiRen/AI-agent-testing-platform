"""
Agent逻辑模块
包含agent的创建、工具定义和核心逻辑
"""

import asyncio
import os
from pathlib import Path
from typing import TypedDict

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver  # SQLite短期记忆（异步版本）
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.tools import tool

# 全局变量用于动态技能生成
_current_db_path = None

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from skills import get_skill_by_name, get_available_skills
from data.database import DatabaseManager

class Skill(TypedDict):
    """技能定义：可通过 progressive disclosure 逐步披露给 agent 的技能"""
    name: str
    description: str
    content: str

@tool
def load_skill(skill_name: str) -> str:
    """Load the full content of a skill into the agent's context. Use this when you need detailed information about how to handle a specific type of request. This will provide you with comprehensive instructions, policies, and guidelines for the skill area.
    
    Args:
        skill_name: The name of the skill to load (e.g., "sales_analytics", "inventory_management")
    """
    skill = get_skill_by_name(skill_name)
    if skill:
        return f"Loaded skill: {skill_name}\n\n{skill['content']}"
    
    available = ", ".join(get_available_skills())
    return f"Skill '{skill_name}' not found. Available skills: {available}"

class AgentManager:
    """Agent管理器"""
    
    def __init__(self, db_path: Path, memory_db_path: Path):
        self.db_path = db_path
        self.memory_db_path = memory_db_path
        self.db_manager = DatabaseManager(db_path)
    
    async def create_skills_agent(self):
        """创建具有 skill 支持的 agent"""
        print("[初始化] 开始创建 Skills SQL Agent...")

        os.environ["SILICONFLOW_API_KEY"] = "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
        print("[配置] API 密钥已设置")

        # 导入模型初始化函数
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from utils import load_chat_model

        llm = load_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")
        print("[模型] LLM 模型已初始化")

        print(f"[数据库] 设置数据库路径: {self.db_path}")
        # 异步调用 setup_database
        await self.db_manager.setup_database()
        print("[数据库] 示例数据库已创建")

        db = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        sql_tools = toolkit.get_tools()
        print(f"[工具] SQL 工具包已加载，包含 {len(sql_tools)} 个工具")

        skills_tools = [load_skill]
        print(f"[技能] 技能工具已准备，包含 {len(skills_tools)} 个技能工具")

        all_tools = sql_tools + skills_tools
        print(f"[总计] 总工具数量: {len(all_tools)} (SQL工具 + 技能工具)")

        # 获取技能描述
        from skills import get_all_skills
        skills = get_all_skills()
        skills_descriptions = "\n".join([
            f"- **{skill['name']}**: {skill['description']}"
            for skill in skills
        ])
        print(f"[技能] 已配置 {len(skills)} 个专业技能")

        system_prompt = f"""你是一个具有专业领域技能的 SQL 查询助手。

## 可用技能

你可以访问以下专业领域的技能（通过 load_skill 工具按需加载）:

{skills_descriptions}

## Progressive Disclosure 工作流程

当用户提出问题时：
1. 识别问题涉及的技能领域
2. **仅在需要时**调用 `load_skill` 工具加载相关技能
3. **重要**：技能加载后，使用技能中提供的表结构和业务规则来构建查询
4. 不要在加载技能后再次调用 sql_db_list_tables 或 sql_db_schema，因为技能已包含所需的表结构
5. 直接使用 sql_db_query 执行查询

## Progressive Disclosure 原则

- **不要一次性加载所有技能**：只在需要时加载相关技能
- **技能包含专业知识**：每个技能都有详细的业务规则、表结构和示例查询
- **减少上下文使用**：按需加载可以显著减少 token 消耗
- **避免重复查询表结构**：技能已包含表结构，无需再次查询

## SQL 查询规则

给定一个输入问题，创建一个语法正确的 {db.dialect} 查询来运行，
然后查看查询结果并返回答案。除非用户指定了希望获取的具体示例数量，
否则始终将查询结果限制在最多 10 条。

你可以按相关列对结果进行排序，以返回数据库中最有趣的示例。
永远不要查询特定表的所有列，只查询问题中相关的列。

不要对数据库执行任何 DML 语句（INSERT、UPDATE、DELETE、DROP 等）。
"""

        # 设置记忆存储（纯异步）
        self.memory_db_path.parent.mkdir(parents=True, exist_ok=True)

        # 删除可能存在的锁定文件
        lock_file = self.memory_db_path.parent / f"{self.memory_db_path.name}-wal"
        shm_file = self.memory_db_path.parent / f"{self.memory_db_path.name}-shm"
        if lock_file.exists():
            lock_file.unlink()
        if shm_file.exists():
            shm_file.unlink()

        try:
            from memory.plugins.store_plugin import StorePlugin
            store = StorePlugin(str(self.memory_db_path))
            await store.enable()
            print("[存储] 记忆存储已设置（异步版本）")
        except Exception as e:
            print(f"[警告] 记忆存储设置失败: {e}")
            print("[信息] 将使用内存存储")
            store = None

        agent = create_agent(
            llm,
            all_tools,
            system_prompt=system_prompt,
            store=store,
        )

        print("[成功] Skills SQL Agent 创建完成!")
        print("[提示] Agent 已准备就绪，可以处理 SQL 查询问题")
        print("[功能] 支持按需加载专业技能进行数据分析")

        return agent
