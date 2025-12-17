"""
Text2SQL Task

SQL生成任务的便捷执行类
"""
from typing import Optional

from agent_langgraph.tasks.text2sql.state import Text2SQLState, create_initial_state
from agent_langgraph.tasks.text2sql.graph import Text2SQLGraphBuilder
from agent_langgraph.tasks.base_task import BaseTask, TaskResult
from agent_langgraph.core import ModelConfig


class Text2SQLTask(BaseTask[Text2SQLState]):
    """
    Text2SQL任务
    
    用法：
        task = Text2SQLTask()
        result = task.run(question="查询所有用户", dialect="mysql")
        print(result.state["sql"])
    """
    
    task_type = "text2sql"
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        super().__init__(model_config)
        self._graph = None
    
    def get_graph(self):
        if self._graph is None:
            self._graph = Text2SQLGraphBuilder().build()
        return self._graph
    
    def create_initial_state(
        self,
        question: str = "",
        schema: str = "",
        dialect: str = "mysql",
        **kwargs
    ) -> Text2SQLState:
        return create_initial_state(
            question=question,
            schema=schema,
            dialect=dialect,
        )
