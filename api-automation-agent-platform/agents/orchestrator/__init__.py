"""
Orchestrator Agent - Main Coordinator

The Orchestrator Agent is responsible for:
1. Understanding user requirements
2. Breaking down tasks into subtasks
3. Coordinating sub-agents
4. Managing workflow and execution flow
5. Handling errors and retries
"""
from typing import Any, Dict, List, Optional, AsyncGenerator
from datetime import datetime

# Import LLM and framework components
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.schema import SystemMessage

from api_agent.models import TaskDB, TaskStatus
from api_agent.db import get_session
from sqlmodel import select


class OrchestratorAgent:
    """
    Main Orchestrator Agent

    Coordinates all sub-agents and manages test automation workflow.
    """

    def __init__(self, llm: Optional[Any] = None):
        """
        Initialize orchestrator agent

        Args:
            llm: Optional LLM instance. If None, creates default ChatOpenAI.
        """
        self.llm = llm or ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7
        )

        self.subagents: Dict[str, Any] = {}
        self.tools: List[Tool] = []

        self.max_iterations = 50
        self.current_task: Optional[TaskDB] = None

    def register_subagent(self, name: str, agent: Any):
        """Register a sub-agent"""
        self.subagents[name] = agent

    def register_tool(self, tool: Tool):
        """Register a tool"""
        self.tools.append(tool)

    async def process_request(
        self,
        user_request: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process user request and coordinate workflow

        Args:
            user_request: Natural language request from user
            user_id: Optional user identifier
            session_id: Optional session identifier

        Yields:
            Progress updates and results
        """
        # Create task
        task = await self._create_task(user_request, user_id, session_id)

        yield {
            "type": "task_created",
            "task_id": task.task_id,
            "status": "created"
        }

        try:
            # Execute workflow steps
            yield {"type": "step", "step": 1, "name": "Understanding requirements"}
            requirements = await self._understand_requirements(user_request)

            yield {
                "type": "step_complete",
                "step": 1,
                "requirements": requirements
            }

            yield {"type": "step", "step": 2, "name": "Planning execution"}
            execution_plan = await self._plan_execution(requirements)

            yield {
                "type": "step_complete",
                "step": 2,
                "execution_plan": execution_plan
            }

            # Step 3: Execute subtasks
            results = {}
            for i, subtask in enumerate(execution_plan.get("subtasks", []), 1):
                yield {
                    "type": "step",
                    "step": 3,
                    "name": f"Executing: {subtask.get('name', 'Unknown')}",
                    "subtask_id": subtask.get("id", "unknown")
                }

                result = await self._execute_subtask(subtask)
                results[subtask.get("id", "unknown")] = result

            # Step 4: Aggregate results
            yield {
                "type": "step",
                "step": 4,
                "name": "Aggregating results"
            }

            final_result = await self._aggregate_results(results, requirements)
            task = await self._update_task_status(task.task_id, TaskStatus.COMPLETED, final_result)

            yield {
                "type": "task_complete",
                "task_id": task.task_id,
                "result": final_result
            }

        except Exception as e:
            # Update task status
            await self._update_task_status(task.task_id, TaskStatus.FAILED, {"error": str(e)})

            yield {
                "type": "task_failed",
                "task_id": task.task_id,
                "error": str(e)
            }
