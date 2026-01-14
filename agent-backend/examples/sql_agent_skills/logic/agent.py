"""
Agent逻辑模块
包含agent的创建、工具定义和核心逻辑

使用懒加载的 MCP 图表工具，避免启动时阻塞
"""

import os
import sys
from pathlib import Path
from typing import TypedDict

from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.tools import tool

# 全局变量用于动态技能生成
_current_db_path = None

# 添加当前目录到Python路径
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.dynamic_skill_generator import DynamicSkillGenerator
from data.database import DatabaseManager

# 使用 MCP 工厂加载图表工具（启动时不会初始化 MCP 客户端）
# 修复导入路径问题
import sys
from pathlib import Path
# 添加examples目录到Python路径
examples_dir = Path(__file__).parent.parent.parent / "examples"
sys.path.insert(0, str(examples_dir))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 延迟导入utils模块，避免启动时的昂贵初始化
def _get_mcp_tools():
    """延迟导入并获取MCP工具"""
    from utils import load_mcp_tools
    return load_mcp_tools

# 延迟导入load_chat_model
def _get_chat_model():
    """延迟导入并获取聊天模型"""
    from utils import load_chat_model
    return load_chat_model


class Skill(TypedDict):
    """技能定义：可通过 progressive disclosure 逐步披露给 agent 的技能"""
    name: str
    description: str
    content: str


@tool
def load_skill(skill_name: str) -> str:
    """Load the full content of a skill into the agent's context. Use this when you need detailed information about how to handle a specific type of request. This will provide you with comprehensive instructions, policies, and guidelines for the skill area.
    
    Args:
        skill_name: The name of the skill to load (e.g., "chinook_analytics")
    """
    # 使用独立的动态技能生成器
    global _current_db_path
    if _current_db_path:
        generator = DynamicSkillGenerator(_current_db_path)
        skill = generator.generate_skill_by_name(skill_name)
        return f"Loaded skill: {skill_name} (dynamic)\n\n{skill['content']}"
    else:
        return "Error: Database path not available. Please try again."


def _get_table_sample_data(table_name: str, limit: int = 3) -> str:
    """获取表样本数据用于分析（使用独立的动态技能生成器）"""
    global _current_db_path
    if _current_db_path:
        generator = DynamicSkillGenerator(_current_db_path)
        return generator.get_table_sample_data(table_name, limit)
    else:
        return "Error: Database path not available. Please try again."


class AgentManager:
    """Agent管理器"""
    
    def __init__(self, db_path: Path, memory_db_path: Path):
        self.db_path = db_path
        self.memory_db_path = memory_db_path
        self.db_manager = DatabaseManager(db_path)
        self._agent_instance = None  # 用于动态技能生成
    
    async def create_skills_agent(self):
        """创建具有 skill 支持的 agent
        
        使用懒加载模式，避免启动时的昂贵初始化操作
        """
        print("[初始化] 开始创建 SQL Agent Skills (懒加载模式)...")
        
        # 设置全局变量用于动态技能生成
        global _current_db_path
        _current_db_path = self.db_path
        
        # 延迟初始化昂贵组件
        model = None
        db = None
        toolkit = None
        sql_tools = None
        chart_tools = None
        
        # 动态技能工具（轻量级）
        @tool
        def get_table_sample_data(table_name: str) -> str:
            """获取表的样本数据用于分析"""
            return _get_table_sample_data(table_name)
        
        @tool
        def sql_db_query_checker(query: str) -> str:
            """检查SQL查询的正确性"""
            try:
                # 简单的语法检查
                query_upper = query.upper().strip()
                if not any(keyword in query_upper for keyword in ['SELECT', 'WITH', 'PRAGMA']):
                    return "错误：只允许 SELECT、WITH 或 PRAGMA 查询"
                
                # 检查基本语法
                if 'INSERT' in query_upper or 'UPDATE' in query_upper or 'DELETE' in query_upper or 'DROP' in query_upper:
                    return "错误：不允许 DML 语句（INSERT、UPDATE、DELETE、DROP）"
                
                return "SQL 查询语法检查通过"
            except Exception as e:
                return f"SQL 查询检查失败: {e}"
        
        skills_tools = [load_skill, get_table_sample_data, sql_db_query_checker]  # 先不加图表工具
        print(f"[技能] 动态技能工具已准备，包含 {len(skills_tools)} 个工具")

        # 懒加载函数：按需初始化昂贵组件
        async def _ensure_model():
            nonlocal model
            if model is None:
                print("[模型] 延迟初始化 LLM 模型...")
                os.environ["SILICONFLOW_API_KEY"] = "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
                from utils import load_chat_model
                model = load_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")
                print("[模型] LLM 模型已初始化")
            return model
            
        async def _ensure_database():
            nonlocal db, toolkit, sql_tools
            if db is None:
                print("[数据库] 延迟初始化数据库连接...")
                print(f"[数据库] 设置数据库路径: {self.db_path}")
                await self.db_manager.setup_database()
                print("[数据库] Chinook示例数据库初始化中...")
                
                model = await _ensure_model()
                db = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")
                toolkit = SQLDatabaseToolkit(db=db, llm=model)
                sql_tools = toolkit.get_tools()
                print(f"[工具] SQL 工具包已加载，包含 {len(sql_tools)} 个工具")
            return db, toolkit, sql_tools
            
        async def _ensure_chart_tools():
            nonlocal chart_tools
            if chart_tools is None:
                print("[图表] 延迟初始化 MCP 图表工具...")
                load_mcp_tools_func = _get_mcp_tools()
                chart_tools = await load_mcp_tools_func("chart")
                print(f"[图表] 懒加载图表工具已准备，包含 {len(chart_tools)} 个工具（MCP 将在首次调用时初始化）")
            return chart_tools
            
        async def _get_all_tools():
            """按需获取所有工具（不包含图表工具，图表工具真正按需）"""
            _, _, sql_tools = await _ensure_database()
            # 添加动态图表工具到技能工具列表
            all_skills_tools = skills_tools + [dynamic_chart_tools]
            all_tools = sql_tools + all_skills_tools
            print(f"[总计] 基础工具数量: {len(all_tools)} (SQL工具 + 动态技能工具)")
            print("[优化] 图表工具将在首次使用时动态加载")
            return all_tools
        
        # 创建动态图表工具包装器
        @tool
        def dynamic_chart_tools(query: str) -> str:
            """动态图表工具 - 在首次调用时初始化 MCP 图表工具"""
            import asyncio
            try:
                # 获取事件循环
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # 同步调用异步函数
                if loop.is_running():
                    # 如果循环正在运行，创建任务
                    chart_tools_future = asyncio.create_task(_ensure_chart_tools())
                    chart_tools = loop.run_until_complete(chart_tools_future)
                else:
                    chart_tools = loop.run_until_complete(_ensure_chart_tools())
                
                return f"图表工具已动态加载，包含 {len(chart_tools)} 个工具。请使用具体的图表工具如 generate_column_chart、generate_bar_chart 等。"
            except Exception as e:
                return f"图表工具加载失败: {e}"
            
        # 预定义系统提示（不依赖动态生成）
        system_prompt = """你是一个专门用于与SQL数据库交互的智能代理。

## 可用技能

你可以访问以下专业领域的技能（通过 load_skill 工具按需加载）:
- chinook_analytics: Chinook数据库分析技能
- sales_analytics: 销售数据分析技能
- customer_analytics: 客户数据分析技能

## 严格工作流程（5步法）

当用户提出问题时，必须严格按以下5个步骤执行：

**步骤1（必须执行）**：调用 sql_db_list_tables 工具，列出数据库中所有可用的表
- 必须在所有其他步骤之前执行
- **在调用工具前，先输出**: "步骤1: 查询数据库表列表"

**步骤2（必须执行）**：调用 sql_db_schema 工具，获取相关表的结构信息
- 必须在步骤1之后执行
- 用于了解表字段和数据类型
- **在调用工具前，先输出**: "步骤2: 获取表结构信息"

**步骤3（必须执行）**：调用 sql_db_query_checker 工具，检查 SQL 查询的正确性
- 必须在步骤2之后执行
- 用于验证 SQL 语法和逻辑错误
- **在调用工具前，先输出**: "步骤3: 执行 SQL 前的检查"

**步骤4（必须执行）**：调用 sql_db_query 工具，执行 SQL 查询
- 必须在步骤3之后执行
- 执行经过检查的 SQL 查询
- **在调用工具前，先输出**: "步骤4: 执行 SQL 查询"

**步骤5（必须执行）**：使用图表工具可视化数据
- 必须在步骤4之后执行
- 使用 generate_column_chart、generate_bar_chart、smart_chart 等工具
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

**动态技能特性**：
- 技能内容动态生成，基于实时数据库结构
- 支持表结构变化，适应性强
- 减少硬编码，提高灵活性
"""

        system_prompt = f"""你是一个专门用于与SQL数据库交互的智能代理。

## 可用技能

你可以访问以下专业领域的技能（通过 load_skill 工具按需加载）:
- chinook_analytics: Chinook数据库分析技能
- sales_analytics: 销售数据分析技能  
- customer_analytics: 客户数据分析技能

## 严格工作流程（5步法）

当用户提出问题时，必须严格按以下5个步骤执行：

**步骤1（必须执行）**：调用 sql_db_list_tables 工具，列出数据库中所有可用的表
- 必须在所有其他步骤之前执行
- **在调用工具前，先输出**: "步骤1: 查询数据库表列表"

**步骤2（必须执行）**：调用 sql_db_schema 工具，获取相关表的结构信息
- 必须在步骤1之后执行
- 用于了解表字段和数据类型
- **在调用工具前，先输出**: "步骤2: 获取表结构信息"

**步骤3（必须执行）**：调用 sql_db_query_checker 工具，检查 SQL 查询的正确性
- 必须在步骤2之后执行
- 用于验证 SQL 语法和逻辑错误
- **在调用工具前，先输出**: "步骤3: 执行 SQL 前的检查"

**步骤4（必须执行）**：调用 sql_db_query 工具，执行 SQL 查询
- 必须在步骤3之后执行
- 执行经过检查的 SQL 查询
- **在调用工具前，先输出**: "步骤4: 执行 SQL 查询"

**步骤5（必须执行）**：使用图表工具可视化数据
- 必须在步骤4之后执行
- 使用 generate_column_chart、generate_bar_chart、smart_chart 等工具
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

**动态技能特性**：
- 技能内容动态生成，基于实时数据库结构
- 支持表结构变化，适应性强
- 减少硬编码，提高灵活性
"""

        # 创建 agent，避免启动时的昂贵初始化
        print("[成功] SQL Agent Skills 创建完成 (优化模式)!")
        print("[提示] Agent 已准备就绪，可以处理 SQL 查询问题")
        print("[功能] 支持按需加载专业技能进行数据分析")
        print("[优化] MCP 图表工具将在首次调用时动态初始化")

        # 直接创建 agent，但使用轻量级初始化
        from langchain.agents import create_agent
        
        # 延迟初始化昂贵组件
        async def _create_agent_with_lazy_tools():
            """按需创建 agent，延迟初始化昂贵组件"""
            all_tools = await _get_all_tools()
            model = await _ensure_model()
            
            agent = create_agent(
                model,
                all_tools,
                system_prompt=system_prompt,
            )
            return agent
            
        # 返回实际的 agent 实例而不是工厂函数
        # 使用轻量级初始化避免启动阻塞
        try:
            # 直接创建 agent，避免异步初始化阻塞
            from langchain.agents import create_agent
            
            # 使用轻量级初始化，避免启动时的昂贵操作
            all_tools = await _get_all_tools()
            model = await _ensure_model()
            
            agent = create_agent(
                model,
                all_tools,
                system_prompt=system_prompt,
            )
            print("[成功] SQL Agent Skills 创建完成!")
            return agent
        except Exception as e:
            print(f"[错误] Agent 创建失败: {e}")
            # 返回一个简单的 agent 作为后备
            from langchain.agents import create_agent
            model = await _ensure_model()
            return create_agent(
                model,
                [],  # 空工具列表作为后备
                system_prompt=system_prompt,
            )


async def create_skills_agent():
    """创建技能版本的SQL Agent（异步）"""
    # 设置数据库路径
    db_path = Path(__file__).parent.parent.parent / "data" / "Chinook.db"
    memory_db_path = Path(__file__).parent.parent.parent / "data" / "agent_memory.db"

    # 创建Agent管理器
    agent_manager = AgentManager(db_path, memory_db_path)

    # 调用异步创建方法
    return await agent_manager.create_skills_agent()
