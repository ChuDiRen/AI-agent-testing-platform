"""
Text2Case Task Module

自然语言生成测试用例 - 多智能体协作架构

使用Supervisor模式协调多个专家智能体：
- Supervisor: 协调者，决定下一步由哪个智能体执行
- Analyzer: 需求分析专家
- Designer: 测试点设计专家
- Writer: 用例编写专家
- Reviewer: 用例评审专家
"""
from agent_langgraph.tasks.text2case.multi_agent_state import Text2CaseState, create_initial_state
from agent_langgraph.tasks.text2case.multi_agent_graph import Text2CaseGraphBuilder, text2case_graph
from agent_langgraph.tasks.text2case.multi_agent_task import Text2CaseTask

from agent_langgraph.tasks.text2case.agents import (
    BaseAgent,
    AgentResponse,
    SupervisorAgent,
    AnalyzerAgent,
    DesignerAgent,
    WriterAgent,
    ReviewerAgent,
)

__all__ = [
    # State
    "Text2CaseState",
    "create_initial_state",
    # Graph
    "Text2CaseGraphBuilder",
    "text2case_graph",
    # Task
    "Text2CaseTask",
    # Agents
    "BaseAgent",
    "AgentResponse",
    "SupervisorAgent",
    "AnalyzerAgent",
    "DesignerAgent",
    "WriterAgent",
    "ReviewerAgent",
]
