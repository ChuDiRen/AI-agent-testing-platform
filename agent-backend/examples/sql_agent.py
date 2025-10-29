"""
SQL Agent - 基于 LangGraph 实现的数据库查询智能体 (完整重构版)

参考: https://docs.langchain.com/oss/python/langgraph/sql-agent

功能特性:
- 细粒度节点控制 (list_tables, call_get_schema, generate_query, check_query, run_query)
- SQL 安全检查和验证
- 支持人工审核模式 (human-in-the-loop)
- Pydantic 配置管理
- Python 高级语法优化

使用示例:
    # 基本模式
    python sql_agent.py

    # 人工审核模式
    python sql_agent.py --human-review
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

import requests
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, SystemMessage, ToolMessage
from langchain.tools import tool
from langchain_community.utilities import SQLDatabase
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field, field_validator


# ==================== Pydantic 配置模型 ====================

class ModelConfig(BaseModel):
    """LLM 模型配置 (仅支持 DeepSeek)"""
    name: str = "deepseek-chat"
    api_key: str = Field(..., min_length=1)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError("API Key 不能为空")
        return v


class DatabaseConfig(BaseModel):
    """数据库配置"""
    url: str = "sqlite:///Chinook.db"  # 默认值，实际使用时会被 from_env 覆盖
    sample_db_url: str = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"
    max_results: int = Field(default=5, ge=1, le=100)


class AgentConfig(BaseModel):
    """Agent 配置"""
    enable_human_review: bool = False  # 是否启用人工审核
    enable_query_check: bool = True    # 是否启用 SQL 检查
    max_retries: int = Field(default=3, ge=1, le=10)
    timeout: int = Field(default=30, ge=5, le=300)


@dataclass
class SQLAgentConfig:
    """SQL Agent 完整配置"""
    model: ModelConfig
    database: DatabaseConfig
    agent: AgentConfig = field(default_factory=AgentConfig)

    @classmethod
    def from_env(cls) -> "SQLAgentConfig":
        """从环境变量创建配置 (仅支持 DeepSeek)"""
        api_key = os.getenv("DEEPSEEK_API_KEY","sk-f79fae69b11a4fce88e04805bd6314b7")
        if not api_key:
            raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")

        os.environ["DEEPSEEK_API_KEY"] = api_key

        # 使用绝对路径
        db_path = Path(__file__).parent / "Chinook.db"
        
        return cls(
            model=ModelConfig(name="deepseek-chat", api_key=api_key),
            database=DatabaseConfig(url=os.getenv("DATABASE_URL", f"sqlite:///{db_path}")),
            agent=AgentConfig(
                enable_human_review=os.getenv("ENABLE_HUMAN_REVIEW", "false").lower() == "true"
            )
        )


# ==================== 数据库管理 ====================

_db_cache = {}  # 数据库连接缓存

def download_database(url: str) -> Optional[Path]:
    """下载示例数据库"""
    # 使用绝对路径，统一存放在 examples 目录
    local_path = Path(__file__).parent / "Chinook.db"

    if local_path.exists():
        return local_path

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        local_path.write_bytes(response.content)
        return local_path
    except Exception as e:
        print(f"✗ 数据库下载失败: {e}")
        return None


def get_database(db_url: str, sample_db_url: str) -> SQLDatabase:
    """获取数据库连接 (使用缓存避免重复连接)"""
    if db_url not in _db_cache:
        download_database(sample_db_url)
        _db_cache[db_url] = SQLDatabase.from_uri(db_url)
    return _db_cache[db_url]


# ==================== SQL 安全检查 ====================

class SQLSecurityChecker:
    """SQL 安全检查器"""

    # 危险的 SQL 关键字模式
    DANGEROUS_PATTERNS = [
        r'\bDROP\b', r'\bDELETE\b', r'\bTRUNCATE\b', r'\bINSERT\b',
        r'\bUPDATE\b', r'\bALTER\b', r'\bCREATE\b', r'\bREPLACE\b',
        r'\bEXEC\b', r'\bEXECUTE\b', r'\b--\b', r'/\*', r'\*/',
    ]

    # 常见的 SQL 错误模式
    ERROR_PATTERNS = {
        'not_in_null': r'\bNOT\s+IN\s*\([^)]*NULL',
        'union_all': r'\bUNION\b(?!\s+ALL)',
        'between_exclusive': r'\bBETWEEN\b.*\bAND\b',
    }

    @classmethod
    def check_query(cls, query: str) -> tuple[bool, list[str]]:
        """检查 SQL 查询安全性

        Returns:
            (is_safe, warnings): 是否安全和警告列表
        """
        warnings = []
        query_upper = query.upper()

        # 检查危险操作
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                warnings.append(f"检测到危险操作: {pattern}")

        # 检查常见错误
        if re.search(cls.ERROR_PATTERNS['not_in_null'], query_upper, re.IGNORECASE):
            warnings.append("警告: NOT IN 与 NULL 值可能导致意外结果")

        if re.search(cls.ERROR_PATTERNS['union_all'], query_upper, re.IGNORECASE):
            warnings.append("建议: 考虑使用 UNION ALL 而不是 UNION 以提高性能")

        is_safe = len([w for w in warnings if '危险' in w]) == 0
        return is_safe, warnings


# ==================== 工具定义 ====================

def create_sql_tools(db: SQLDatabase, config: DatabaseConfig):
    """创建 SQL 工具集"""

    @tool
    def list_tables() -> str:
        """列出数据库中的所有表"""
        return ", ".join(db.get_usable_table_names())

    @tool
    def get_schema(table_names: str) -> str:
        """获取指定表的结构信息

        Args:
            table_names: 逗号分隔的表名，例如 "Artist, Album"
        """
        tables = [t.strip() for t in table_names.split(",")]
        return db.get_table_info_no_throw(tables)

    @tool
    def run_query(query: str) -> str:
        """执行 SQL 查询

        Args:
            query: SQL 查询语句
        """
        try:
            return db.run_no_throw(query)
        except Exception as e:
            return f"查询出错: {e}"

    @tool
    def check_query(query: str) -> str:
        """检查 SQL 查询的安全性和常见错误

        Args:
            query: 待检查的 SQL 查询语句
        """
        is_safe, warnings = SQLSecurityChecker.check_query(query)

        if not is_safe:
            return f"❌ 查询不安全，请修改:\n" + "\n".join(f"- {w}" for w in warnings)

        if warnings:
            return f"✓ 查询安全，建议:\n" + "\n".join(f"- {w}" for w in warnings)

        return "✓ 查询检查通过，可以执行"

    return [list_tables, get_schema, run_query, check_query]


# ==================== Agent 节点定义 ====================

class SQLAgentNodes:
    """SQL Agent 节点集合"""

    def __init__(self, config: SQLAgentConfig, db: SQLDatabase):
        self.config = config
        self.db = db
        self.tools = create_sql_tools(db, config.database)
        self.tools_by_name = {tool.name: tool for tool in self.tools}

        # 初始化 LLM (仅支持 DeepSeek)
        self.llm = init_chat_model(
            config.model.name,
            model_provider="deepseek",
            temperature=config.model.temperature
        )

        # 获取特定工具
        self.get_schema_tool = next(t for t in self.tools if t.name == "get_schema")
        self.run_query_tool = next(t for t in self.tools if t.name == "run_query")
        self.check_query_tool = next(t for t in self.tools if t.name == "check_query")

    def list_tables_node(self, state: MessagesState) -> dict:
        """节点1: 强制列出所有表"""

        # 创建预定义的工具调用
        tool_call = {"name": "list_tables", "args": {}, "id": "list_tables_call", "type": "tool_call"}
        tool_call_message = AIMessage(content="", tool_calls=[tool_call])

        # 执行工具
        list_tables_tool = self.tools_by_name["list_tables"]
        result = list_tables_tool.invoke({})
        tool_message = ToolMessage(content=str(result), tool_call_id=tool_call["id"])

        # 添加说明消息
        info_message = AIMessage(content=f"数据库可用表: {result}")

        return {"messages": [tool_call_message, tool_message, info_message]}

    def call_get_schema_node(self, state: MessagesState) -> dict:
        """节点2: 强制调用 get_schema 工具"""
        # 强制模型调用 get_schema 工具
        llm_with_schema = self.llm.bind_tools([self.get_schema_tool], tool_choice="any")
        response = llm_with_schema.invoke(state["messages"])

        return {"messages": [response]}

    def generate_query_node(self, state: MessagesState) -> dict:
        """节点3: 生成 SQL 查询"""

        system_prompt = f"""你是一个 SQL 专家助手。根据用户问题生成正确的 {self.db.dialect} 查询。

工作要求:
1. 仔细分析表结构和用户问题
2. 生成语法正确的 SQL 查询
3. 使用 LIMIT {self.config.database.max_results} 限制结果数量
4. 避免查询所有列，只选择必要的列
5. 使用适当的 JOIN、GROUP BY、ORDER BY 等子句

注意事项:
- 不要执行 DML 操作 (INSERT, UPDATE, DELETE, DROP 等)
- 正确处理 NULL 值
- 使用正确的数据类型转换
- 为复杂查询添加注释
"""

        messages = [SystemMessage(content=system_prompt)] + state["messages"]

        # 绑定 run_query 工具，但不强制调用
        llm_with_query = self.llm.bind_tools([self.run_query_tool])
        response = llm_with_query.invoke(messages)

        return {"messages": [response]}

    def check_query_node(self, state: MessagesState) -> dict:
        """节点4: 检查 SQL 查询安全性"""
        # 获取最后一条消息中的工具调用
        last_message = state["messages"][-1]
        if not last_message.tool_calls:
            return {"messages": []}

        tool_call = last_message.tool_calls[0]
        query = tool_call["args"].get("query", "")

        # 执行安全检查
        check_result = self.check_query_tool.invoke({"query": query})

        # 如果检查不通过，修改工具调用
        if "❌" in check_result:
            # 创建检查失败的系统消息
            system_message = SystemMessage(
                content=f"SQL 安全检查失败:\n{check_result}\n\n请重新生成安全的查询。"
            )

            # 创建新的 AI 消息，不包含工具调用
            new_ai_message = AIMessage(
                content=f"检测到不安全的查询，需要重新生成。\n{check_result}",
                id=last_message.id
            )

            return {"messages": [system_message, new_ai_message]}

        # 检查通过，保持原工具调用
        return {"messages": [last_message]}

    def should_continue(self, state: MessagesState) -> Literal["check_query", "run_query", END]:
        """条件边: 判断下一步操作"""
        last_message = state["messages"][-1]

        if not last_message.tool_calls:
            return END

        # 如果启用了查询检查，先检查
        if self.config.agent.enable_query_check:
            tool_call = last_message.tool_calls[0]
            if tool_call["name"] == "run_query":
                return "check_query"

        return "run_query"


# ==================== Agent 构建 ====================

def build_sql_agent(config: SQLAgentConfig) -> StateGraph:
    """构建 SQL Agent 状态图"""

    # 获取数据库连接
    db = get_database(config.database.url, config.database.sample_db_url)

    # 创建节点实例
    nodes = SQLAgentNodes(config, db)

    # 创建工具节点
    get_schema_node = ToolNode([nodes.get_schema_tool])
    run_query_node = ToolNode([nodes.run_query_tool])

    # 构建状态图
    builder = StateGraph(MessagesState)

    # 添加节点
    builder.add_node("list_tables", nodes.list_tables_node)
    builder.add_node("call_get_schema", nodes.call_get_schema_node)
    builder.add_node("get_schema", get_schema_node)
    builder.add_node("generate_query", nodes.generate_query_node)
    builder.add_node("check_query", nodes.check_query_node)
    builder.add_node("run_query", run_query_node)

    # 添加边
    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    builder.add_conditional_edges("generate_query", nodes.should_continue)
    builder.add_edge("check_query", "run_query")
    builder.add_edge("run_query", "generate_query")

    # 编译图 (如果启用人工审核，添加 checkpointer)
    # checkpointer = MemorySaver() if config.agent.enable_human_review else None
    # return builder.compile(checkpointer=checkpointer)
    return builder.compile()


# ==================== 使用示例 ====================
"""
使用示例:

# 1. 基本使用
from sql_agent import SQLAgentConfig, build_sql_agent
from langchain.messages import HumanMessage

config = SQLAgentConfig.from_env()
agent = build_sql_agent(config)
result = agent.invoke({"messages": [HumanMessage(content="数据库中有多少个艺术家?")]})
print(result["messages"][-1].content)

# 2. 启用人工审核模式
config = SQLAgentConfig.from_env()
config.agent.enable_human_review = True
agent = build_sql_agent(config)

# 3. 自定义配置
from sql_agent import ModelConfig, DatabaseConfig, AgentConfig

config = SQLAgentConfig(
    model=ModelConfig(name="deepseek-chat", api_key="your-api-key"),
    database=DatabaseConfig(url="sqlite:///your_database.db", max_results=10),
    agent=AgentConfig(enable_query_check=True)
)
agent = build_sql_agent(config)
"""
config = SQLAgentConfig.from_env()
# config.agent.enable_human_review = True
agent = build_sql_agent(config)

# # ==================== 主函数 ====================
# 
# def run_test_queries(agent, config: SQLAgentConfig):
#     """运行测试查询"""
#     test_questions = [
#         "数据库中有多少个艺术家?",
#         "哪个流派的曲目平均时长最长? 显示前5个",
#         "列出销售额最高的5位客户",
#     ]
# 
#     print("="*60)
#     print("开始测试查询")
#     print("="*60)
# 
#     for question in test_questions:
#         print(f"\n问题: {question}")
#         print("-"*60)
# 
#         try:
#             result = agent.invoke({"messages": [HumanMessage(content=question)]})
#             answer = result["messages"][-1].content
#             print(f"回答: {answer}\n")
#         except Exception as e:
#             print(f"✗ 查询失败: {e}")
# 
# 
# def main():
#     """主函数"""
#     import argparse
# 
#     # 解析命令行参数
#     parser = argparse.ArgumentParser(description="SQL Agent - 数据库查询智能体")
#     parser.add_argument("--human-review", action="store_true", help="启用人工审核模式")
#     parser.add_argument("--skip-test", action="store_true", help="跳过测试查询")
#     args = parser.parse_args()
# 
#     print("="*60)
#     print("SQL Agent - 数据库查询智能体")
#     print("="*60)
# 
#     # 加载配置
#     config = SQLAgentConfig.from_env()
#     if args.human_review:
#         config.agent.enable_human_review = True
# 
#     print(f"\n📋 配置信息:")
#     print(f"  模型: DeepSeek/{config.model.name}")
#     print(f"  数据库: {config.database.url}")
#     print(f"  人工审核: {'启用' if config.agent.enable_human_review else '禁用'}")
#     print(f"  SQL 检查: {'启用' if config.agent.enable_query_check else '禁用'}")
# 
#     # 构建 Agent
#     print("\n🔧 正在构建 Agent...")
#     agent = build_sql_agent(config)
#     print("✓ Agent 初始化完成\n")
# 
#     # 运行测试查询
#     if not args.skip_test:
#         run_test_queries(agent, config)
# 
# 
# if __name__ == "__main__":
#     main()
