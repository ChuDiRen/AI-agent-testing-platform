"""
Text2Case Multi-Agent Module

多智能体协作架构：
- Supervisor: 协调者，决定下一步由哪个智能体执行
- Analyzer: 需求分析专家
- Designer: 测试点设计专家
- Writer: 用例编写专家
- Reviewer: 用例评审专家
"""
from agent_langgraph.tasks.text2case.agents.base import BaseAgent, AgentResponse
from agent_langgraph.tasks.text2case.agents.analyzer import AnalyzerAgent
from agent_langgraph.tasks.text2case.agents.designer import DesignerAgent
from agent_langgraph.tasks.text2case.agents.writer import WriterAgent
from agent_langgraph.tasks.text2case.agents.reviewer import ReviewerAgent
from agent_langgraph.tasks.text2case.agents.supervisor import SupervisorAgent

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "AnalyzerAgent",
    "DesignerAgent",
    "WriterAgent",
    "ReviewerAgent",
    "SupervisorAgent",
]
