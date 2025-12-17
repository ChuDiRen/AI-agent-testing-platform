"""
LangGraph TestCase Generator Module

基于LangGraph的多智能体协作测试用例生成器
支持国产大模型（DeepSeek、通义千问、智谱AI、Kimi、SiliconFlow）

架构说明：
- core/: 核心抽象层（BaseState、BaseGraphBuilder、ModelFactory）
- tasks/: 任务实现（text2case、text2sql、text2api）
- prompts/: 提示词模板
- services/: 服务层
"""

from agent_langgraph.core import (
    BaseGraphBuilder,
    ModelFactory,
    ModelConfig,
)

from agent_langgraph.tasks import (
    BaseTask,
    TaskResult,
    # Text2Case
    Text2CaseState,
    Text2CaseGraphBuilder,
    text2case_graph,
    Text2CaseTask,
    # Text2Case Agents
    BaseAgent,
    AgentResponse,
    SupervisorAgent,
    AnalyzerAgent,
    DesignerAgent,
    WriterAgent,
    ReviewerAgent,
    # Text2SQL
    Text2SQLState,
    Text2SQLGraphBuilder,
    text2sql_graph,
    Text2SQLTask,
    # Text2API
    Text2APIState,
    Text2APIGraphBuilder,
    text2api_graph,
    Text2APITask,
    # Registry
    TaskRegistry,
    get_graph,
    get_all_graphs,
)

__all__ = [
    # Core
    "BaseGraphBuilder",
    "ModelFactory",
    "ModelConfig",
    # Tasks Base
    "BaseTask",
    "TaskResult",
    # Text2Case
    "Text2CaseState",
    "Text2CaseGraphBuilder",
    "text2case_graph",
    "Text2CaseTask",
    # Text2Case Agents
    "BaseAgent",
    "AgentResponse",
    "SupervisorAgent",
    "AnalyzerAgent",
    "DesignerAgent",
    "WriterAgent",
    "ReviewerAgent",
    # Text2SQL
    "Text2SQLState",
    "Text2SQLGraphBuilder",
    "text2sql_graph",
    "Text2SQLTask",
    # Text2API
    "Text2APIState",
    "Text2APIGraphBuilder",
    "text2api_graph",
    "Text2APITask",
    # Registry
    "TaskRegistry",
    "get_graph",
    "get_all_graphs",
]
