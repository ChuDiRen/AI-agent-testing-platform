"""
Text2Case Graph Builder

多智能体协作的Graph构建器，使用Supervisor模式
"""
import json
import logging
from typing import Dict, Callable, List, Tuple, Type, Any

from langgraph.graph import StateGraph, START, END

from agent_langgraph.tasks.text2case.multi_agent_state import Text2CaseState
from agent_langgraph.tasks.text2case.agents import (
    SupervisorAgent,
    AnalyzerAgent,
    DesignerAgent,
    WriterAgent,
    ReviewerAgent,
)
from agent_langgraph.core import BaseGraphBuilder
from agent_langgraph.tasks.registry import TaskRegistry

logger = logging.getLogger(__name__)


# 创建智能体实例
supervisor = SupervisorAgent()
analyzer = AnalyzerAgent()
designer = DesignerAgent()
writer = WriterAgent()
reviewer = ReviewerAgent()


# ==================== Node Functions ====================

async def supervisor_node(state: Text2CaseState) -> Dict[str, Any]:
    """Supervisor节点：决定下一步"""
    logger.info("[supervisor_node] Deciding next agent...")
    
    response = await supervisor.process(state)
    
    if not response.success:
        return {"error": response.error, "completed": True}
    
    next_agent = response.metadata.get("next", "FINISH")
    reason = response.metadata.get("reason", "")
    
    messages = list(state.get("messages", []))
    messages.append({
        "role": "system",
        "name": "supervisor",
        "content": f"决策: {next_agent} - {reason}"
    })
    
    agent_history = list(state.get("agent_history", []))
    agent_history.append(f"supervisor -> {next_agent}")
    
    return {
        "next_agent": next_agent,
        "messages": messages,
        "agent_history": agent_history,
    }


async def analyzer_node(state: Text2CaseState) -> Dict[str, Any]:
    """Analyzer节点：需求分析"""
    logger.info("[analyzer_node] Analyzing requirement...")
    
    response = await analyzer.process(state)
    
    if not response.success:
        return {"error": response.error}
    
    messages = list(state.get("messages", []))
    messages.append(response.to_message())
    
    return {
        "analysis": response.content,
        "messages": messages,
    }


async def designer_node(state: Text2CaseState) -> Dict[str, Any]:
    """Designer节点：测试点设计"""
    logger.info("[designer_node] Designing test points...")
    
    response = await designer.process(state)
    
    if not response.success:
        return {"error": response.error}
    
    messages = list(state.get("messages", []))
    messages.append(response.to_message())
    
    return {
        "test_points": response.content,
        "messages": messages,
    }


async def writer_node(state: Text2CaseState) -> Dict[str, Any]:
    """Writer节点：编写测试用例"""
    logger.info("[writer_node] Writing test cases...")
    
    response = await writer.process(state)
    
    if not response.success:
        return {"error": response.error}
    
    messages = list(state.get("messages", []))
    messages.append(response.to_message())
    
    iteration = state.get("iteration", 0) + 1
    
    return {
        "test_cases": response.content,
        "messages": messages,
        "iteration": iteration,
        "quality_score": 0.0,  # 重置评分，等待评审
    }


async def reviewer_node(state: Text2CaseState) -> Dict[str, Any]:
    """Reviewer节点：评审测试用例"""
    logger.info("[reviewer_node] Reviewing test cases...")
    
    response = await reviewer.process(state)
    
    if not response.success:
        return {"error": response.error}
    
    messages = list(state.get("messages", []))
    messages.append(response.to_message())
    
    # 解析评审结果
    quality_score = response.metadata.get("quality_score", 0)
    passed = response.metadata.get("passed", False)
    
    # 提取改进建议作为反馈
    review_feedback = ""
    try:
        review_data = json.loads(response.content)
        suggestions = review_data.get("suggestions", [])
        issues = review_data.get("issues", [])
        if suggestions or issues:
            review_feedback = f"问题: {'; '.join(issues)}\n建议: {'; '.join(suggestions)}"
    except json.JSONDecodeError:
        pass
    
    return {
        "review_result": response.content,
        "review_feedback": review_feedback,
        "quality_score": quality_score,
        "completed": passed,
        "messages": messages,
    }


def route_next_agent(state: Text2CaseState) -> str:
    """路由到下一个智能体"""
    next_agent = state.get("next_agent", "FINISH")
    
    if state.get("error"):
        return END
    
    if next_agent == "FINISH":
        return END
    
    if next_agent in ["analyzer", "designer", "writer", "reviewer"]:
        return next_agent
    
    return END


# ==================== Graph Builder ====================

class Text2CaseGraphBuilder(BaseGraphBuilder[Text2CaseState]):
    """
    多智能体协作Graph构建器
    
    使用Supervisor模式：
    1. Supervisor分析状态，决定下一步
    2. 执行对应的专家智能体
    3. 返回Supervisor继续决策
    4. 直到Supervisor决定FINISH
    """
    
    task_type = "text2case"
    
    def get_state_class(self) -> Type[Text2CaseState]:
        return Text2CaseState
    
    def get_nodes(self) -> Dict[str, Callable]:
        return {
            "supervisor": supervisor_node,
            "analyzer": analyzer_node,
            "designer": designer_node,
            "writer": writer_node,
            "reviewer": reviewer_node,
        }
    
    def get_edges(self) -> List[Tuple[str, str]]:
        return [
            ("START", "supervisor"),
            # 各智能体执行完后返回supervisor
            ("analyzer", "supervisor"),
            ("designer", "supervisor"),
            ("writer", "supervisor"),
            ("reviewer", "supervisor"),
        ]
    
    def get_conditional_edges(self) -> List[Tuple[str, Callable, Dict[str, str]]]:
        return [
            (
                "supervisor",
                route_next_agent,
                {
                    "analyzer": "analyzer",
                    "designer": "designer",
                    "writer": "writer",
                    "reviewer": "reviewer",
                    END: END,
                }
            ),
        ]


# 注册任务
TaskRegistry.register("text2case", Text2CaseGraphBuilder)

# 构建并导出graph实例
text2case_graph = Text2CaseGraphBuilder().build()
