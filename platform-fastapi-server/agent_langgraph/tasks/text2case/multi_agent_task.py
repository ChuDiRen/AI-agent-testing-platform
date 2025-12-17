"""
Text2Case Task

多智能体协作任务的便捷执行类
"""
import logging
from typing import Optional, AsyncIterator, Dict, Any

from agent_langgraph.tasks.text2case.multi_agent_state import Text2CaseState, create_initial_state
from agent_langgraph.tasks.text2case.multi_agent_graph import text2case_graph
from agent_langgraph.tasks.base_task import BaseTask, TaskResult
from agent_langgraph.core import ModelConfig

logger = logging.getLogger(__name__)


class Text2CaseTask(BaseTask[Text2CaseState]):
    """
    测试用例生成任务
    
    使用Supervisor模式协调多个专家智能体：
    - Analyzer: 需求分析
    - Designer: 测试点设计
    - Writer: 用例编写
    - Reviewer: 用例评审
    
    用法：
        task = Text2CaseTask()
        result = await task.arun(
            requirement="用户登录功能",
            test_type="API",
            max_iterations=3
        )
        print(result.state["test_cases"])
    """
    
    task_type = "text2case"
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        super().__init__(model_config)
        self._graph = None
    
    def get_graph(self):
        if self._graph is None:
            self._graph = text2case_graph
        return self._graph
    
    def create_initial_state(
        self,
        requirement: str = "",
        test_type: str = "API",
        max_iterations: int = 3,
        **kwargs
    ) -> Text2CaseState:
        return create_initial_state(
            requirement=requirement,
            test_type=test_type,
            max_iterations=max_iterations,
        )
    
    async def arun_with_callback(
        self,
        requirement: str,
        test_type: str = "API",
        max_iterations: int = 3,
        on_agent_start: Optional[callable] = None,
        on_agent_end: Optional[callable] = None,
        **kwargs
    ) -> TaskResult:
        """
        带回调的异步执行
        
        Args:
            requirement: 需求描述
            test_type: 测试类型
            max_iterations: 最大迭代次数
            on_agent_start: 智能体开始执行回调 (agent_name, state) -> None
            on_agent_end: 智能体执行完成回调 (agent_name, state) -> None
        """
        graph = self.get_graph()
        initial_state = self.create_initial_state(
            requirement=requirement,
            test_type=test_type,
            max_iterations=max_iterations,
        )
        
        logger.info(f"Starting multi-agent task: {self.task_type}")
        
        try:
            final_state = None
            async for event in graph.astream(initial_state):
                for node_name, state in event.items():
                    if on_agent_start and node_name != "__end__":
                        on_agent_start(node_name, state)
                    
                    final_state = state
                    
                    if on_agent_end and node_name != "__end__":
                        on_agent_end(node_name, state)
            
            if final_state is None:
                final_state = initial_state
            
            success = final_state.get("completed", False) and not final_state.get("error")
            
            return TaskResult(
                success=success,
                state=final_state,
                output=final_state.get("test_cases"),
                error=final_state.get("error"),
            )
        except Exception as e:
            logger.error(f"Multi-agent task failed: {e}")
            return TaskResult(
                success=False,
                state={},
                error=str(e),
            )
    
    async def astream(
        self,
        requirement: str,
        test_type: str = "API",
        max_iterations: int = 3,
        **kwargs
    ) -> AsyncIterator[tuple]:
        """
        流式执行，逐步返回每个智能体的输出
        
        Yields:
            (agent_name, state) 元组
        """
        graph = self.get_graph()
        initial_state = self.create_initial_state(
            requirement=requirement,
            test_type=test_type,
            max_iterations=max_iterations,
        )
        
        async for event in graph.astream(initial_state):
            for node_name, state in event.items():
                if node_name != "__end__":
                    yield node_name, state
    
    def get_execution_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取执行摘要
        
        Args:
            state: 最终状态
            
        Returns:
            执行摘要
        """
        agent_history = state.get("agent_history", [])
        
        return {
            "total_steps": len(agent_history),
            "agent_history": agent_history,
            "iterations": state.get("iteration", 0),
            "quality_score": state.get("quality_score", 0),
            "completed": state.get("completed", False),
            "has_error": bool(state.get("error")),
        }
