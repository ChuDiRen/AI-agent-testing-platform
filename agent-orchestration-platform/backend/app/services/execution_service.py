"""
LangGraph 执行引擎服务
"""
import json
import asyncio
from typing import Dict, Any, AsyncIterator
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(name="execution_engine")


# 定义 Agent 状态
class AgentState(Dict[str, Any]):
    """Agent 执行状态"""
    messages: list
    current_step: str
    context: Dict[str, Any]
    final_answer: str
    tokens_used: int
    error_message: str | None


class LangGraphExecutionEngine:
    """LangGraph 执行引擎"""

    def __init__(self):
        self.checkpointer = MemorySaver()
        self.workflows: Dict[int, StateGraph] = {}

    async def create_workflow_graph(
        self,
        graph_data: Dict[str, Any],
        agent_config: Dict[str, Any]
    ) -> StateGraph:
        """根据图数据创建 LangGraph 工作流"""
        workflow = StateGraph(AgentState)

        # 根据节点类型添加节点
        for node in graph_data.get("nodes", []):
            node_type = node.get("type")
            node_id = node.get("id")

            if node_type == "agent":
                workflow.add_node(node_id, self._create_agent_node(agent_config))
            elif node_type == "tool":
                workflow.add_node(node_id, self._create_tool_node(node))
            elif node_type == "condition":
                workflow.add_node(node_id, self._create_condition_node(node))

        # 添加边（连接）
        for edge in graph_data.get("edges", []):
            source = edge.get("source")
            target = edge.get("target")

            if edge.get("type") == "conditional":
                condition = edge.get("condition")
                workflow.add_conditional_edges(
                    source,
                    self._route_condition,
                    {condition: target, "default": END}
                )
            else:
                workflow.add_edge(source, target)

        return workflow.compile(checkpointer=self.checkpointer)

    def _create_agent_node(self, agent_config: Dict[str, Any]):
        """创建 Agent 节点"""
        async def agent_node(state: AgentState):
            # TODO: 实现实际的 LLM 调用
            response = f"Agent response from {agent_config.get('name')}"
            return {
                "messages": state.get("messages", []) + [response],
                "tokens_used": state.get("tokens_used", 0) + 100
            }
        return agent_node

    def _create_tool_node(self, node: Dict[str, Any]):
        """创建 Tool 节点"""
        async def tool_node(state: AgentState):
            tool_name = node.get("name")
            logger.info(f"Executing tool: {tool_name}")
            # TODO: 实现实际的工具调用
            return {
                "messages": state.get("messages", []) + [f"Tool {tool_name} executed"],
                "context": {**state.get("context", {}), f"{tool_name}_result": "success"}
            }
        return tool_node

    def _create_condition_node(self, node: Dict[str, Any]):
        """创建条件节点"""
        async def condition_node(state: AgentState):
            condition_expr = node.get("condition")
            # TODO: 实现条件评估
            result = True  # 简化版，实际需要解析条件表达式
            return {"current_step": "true" if result else "false"}
        return condition_node

    def _route_condition(self, state: AgentState):
        """条件路由函数"""
        return state.get("current_step", "default")

    async def execute_workflow(
        self,
        workflow_id: int,
        graph_data: Dict[str, Any],
        agent_config: Dict[str, Any],
        input_data: Dict[str, Any],
        execution_id: int
    ) -> AsyncIterator[Dict[str, Any]]:
        """执行工作流（流式输出）"""

        logger.info(
            f"Starting workflow execution: workflow_id={workflow_id}, execution_id={execution_id}"
        )

        # 创建或获取工作流图
        if workflow_id not in self.workflows:
            self.workflows[workflow_id] = await self.create_workflow_graph(
                graph_data, agent_config
            )

        graph = self.workflows[workflow_id]

        # 执行工作流并流式输出
        config = {
            "configurable": {
                "thread_id": str(execution_id)
            }
        }

        async for chunk in graph.astream(
            {"messages": [input_data.get("query", "")]},
            config=config,
            stream_mode="values"
        ):
            # 发送执行状态更新
            yield {
                "type": "node_complete",
                "node_id": chunk.get("current_step", "unknown"),
                "state": chunk,
                "timestamp": datetime.now().isoformat()
            }

        # 发送完成消息
        yield {
            "type": "execution_complete",
            "execution_id": execution_id,
            "status": "completed",
            "final_answer": "Workflow execution completed",
            "timestamp": datetime.now().isoformat()
        }

    async def get_execution_state(
        self,
        execution_id: int
    ) -> Dict[str, Any]:
        """获取执行状态"""
        config = {
            "configurable": {
                "thread_id": str(execution_id)
            }
        }

        # TODO: 从 checkpointer 获取状态
        return {
            "execution_id": execution_id,
            "status": "running",
            "current_node": "agent_1"
        }


# 全局执行引擎实例
execution_engine = LangGraphExecutionEngine()
