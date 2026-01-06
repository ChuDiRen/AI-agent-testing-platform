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
import uuid
import json

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

    async def _create_task(self, user_request: str, user_id: Optional[str], session_id: Optional[str]) -> TaskDB:
        """Create a new task in database"""
        task = TaskDB(
            task_id=str(uuid.uuid4()),
            user_request=user_request,
            user_id=user_id,
            session_id=session_id,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to database
        with get_session() as session:
            session.add(task)
            session.commit()
            session.refresh(task)
        
        self.current_task = task
        return task

    async def _understand_requirements(self, user_request: str) -> Dict[str, Any]:
        """Understand user requirements using LLM"""
        system_prompt = """
        You are an API testing expert. Analyze the user request and extract:
        1. API source/document location
        2. Test types required (functional, security, performance, integration)
        3. Output format preferences
        4. Special requirements
        
        Return structured JSON.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "User request: {request}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"request": user_request})
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "api_source": user_request,
                "test_types": ["functional"],
                "output_format": "playwright",
                "special_requirements": []
            }

    async def _plan_execution(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Plan execution steps based on requirements"""
        subtasks = []
        
        # Step 1: RAG Retrieval
        subtasks.append({
            "id": "rag_retrieval",
            "name": "Retrieve API Information",
            "agent": "rag-retrieval",
            "input": {
                "query": requirements.get("api_source", ""),
                "mode": "mix",
                "top_k": 10
            }
        })
        
        # Step 2: Test Planning
        subtasks.append({
            "id": "test_planning",
            "name": "Generate Test Plan",
            "agent": "planner",
            "input": {
                "api_info": "{{rag_retrieval.result}}",
                "test_types": requirements.get("test_types", ["functional"])
            }
        })
        
        # Step 3: Test Generation
        subtasks.append({
            "id": "test_generation",
            "name": "Generate Test Code",
            "agent": "generator",
            "input": {
                "test_plan": "{{test_planning.result}}",
                "output_format": requirements.get("output_format", "playwright")
            }
        })
        
        # Step 4: Test Execution (optional)
        if requirements.get("execute_tests", False):
            subtasks.append({
                "id": "test_execution",
                "name": "Execute Tests",
                "agent": "executor",
                "input": {
                    "test_files": "{{test_generation.result}}"
                }
            })
        
        # Step 5: Result Analysis
        subtasks.append({
            "id": "result_analysis",
            "name": "Analyze Results",
            "agent": "analyzer",
            "input": {
                "test_results": "{{test_execution.result}}" if requirements.get("execute_tests", False) else "{{test_generation.result}}"
            }
        })
        
        return {
            "subtasks": subtasks,
            "estimated_duration": len(subtasks) * 30,  # 30 seconds per subtask
            "requirements": requirements
        }

    async def _execute_subtask(self, subtask: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single subtask"""
        agent_name = subtask.get("agent")
        agent = self.subagents.get(agent_name)
        
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")
        
        # Process input template variables
        input_data = subtask.get("input", {})
        processed_input = await self._process_template_variables(input_data)
        
        # Execute agent
        if hasattr(agent, 'execute'):
            result = await agent.execute(processed_input)
        else:
            raise ValueError(f"Agent {agent_name} does not have execute method")
        
        return {
            "agent": agent_name,
            "subtask_id": subtask.get("id"),
            "result": result,
            "status": "completed"
        }

    async def _process_template_variables(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process template variables in input data"""
        # Simple template processing - in real implementation, use proper templating engine
        processed = {}
        for key, value in input_data.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Extract variable name
                var_name = value[2:-2].strip()
                # In real implementation, resolve from previous results
                processed[key] = f"RESOLVED_{var_name}"
            else:
                processed[key] = value
        return processed

    async def _aggregate_results(self, results: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from all subtasks"""
        return {
            "summary": {
                "total_subtasks": len(results),
                "completed": len([r for r in results.values() if r.get("status") == "completed"]),
                "failed": len([r for r in results.values() if r.get("status") == "failed"])
            },
            "results": results,
            "requirements": requirements,
            "final_output": self._generate_final_output(results, requirements)
        }

    def _generate_final_output(self, results: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final output based on results"""
        # Extract key results
        rag_result = results.get("rag_retrieval", {}).get("result", {})
        plan_result = results.get("test_planning", {}).get("result", {})
        generation_result = results.get("test_generation", {}).get("result", {})
        
        return {
            "api_information": rag_result,
            "test_plan": plan_result,
            "generated_tests": generation_result,
            "execution_summary": "Test automation workflow completed successfully"
        }

    async def _update_task_status(self, task_id: str, status: TaskStatus, result: Dict[str, Any]) -> TaskDB:
        """Update task status in database"""
        with get_session() as session:
            task = session.exec(select(TaskDB).where(TaskDB.task_id == task_id)).first()
            if task:
                task.status = status
                task.result = json.dumps(result) if result else None
                task.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(task)
            return task
