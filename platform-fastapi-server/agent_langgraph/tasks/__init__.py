"""
LangGraph Tasks Module

包含所有任务类型的实现：
- text2case: 自然语言生成测试用例（多智能体协作）
- text2sql: 自然语言转SQL查询
- text2api: 自然语言生成API请求

扩展新任务类型：
1. 在tasks/下创建新目录（如text2xxx）
2. 实现state.py、nodes.py、graph.py、task.py
3. 在graph.py中调用TaskRegistry.register()注册
4. 在此__init__.py中导出
"""
from agent_langgraph.tasks.base_task import BaseTask, TaskResult
from agent_langgraph.tasks.text2case import (
    Text2CaseState,
    Text2CaseGraphBuilder,
    text2case_graph,
    Text2CaseTask,
    # Agents
    BaseAgent,
    AgentResponse,
    SupervisorAgent,
    AnalyzerAgent,
    DesignerAgent,
    WriterAgent,
    ReviewerAgent,
)
from agent_langgraph.tasks.text2sql import (
    Text2SQLState,
    Text2SQLGraphBuilder,
    text2sql_graph,
    Text2SQLTask,
)
from agent_langgraph.tasks.text2api import (
    Text2APIState,
    Text2APIGraphBuilder,
    text2api_graph,
    Text2APITask,
)
from agent_langgraph.tasks.registry import TaskRegistry, get_graph, get_all_graphs

__all__ = [
    # Base
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
