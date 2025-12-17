"""
Text2API Task

API请求生成任务的便捷执行类
"""
from typing import Optional

from agent_langgraph.tasks.text2api.state import Text2APIState, create_initial_state
from agent_langgraph.tasks.text2api.graph import Text2APIGraphBuilder
from agent_langgraph.tasks.base_task import BaseTask, TaskResult
from agent_langgraph.core import ModelConfig


class Text2APITask(BaseTask[Text2APIState]):
    """
    Text2API任务
    
    用法：
        task = Text2APITask()
        result = task.run(description="获取用户列表", base_url="https://api.example.com")
        print(result.state["curl"])
    """
    
    task_type = "text2api"
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        super().__init__(model_config)
        self._graph = None
    
    def get_graph(self):
        if self._graph is None:
            self._graph = Text2APIGraphBuilder().build()
        return self._graph
    
    def create_initial_state(
        self,
        description: str = "",
        api_spec: str = "",
        base_url: str = "",
        auth_type: str = "none",
        **kwargs
    ) -> Text2APIState:
        return create_initial_state(
            description=description,
            api_spec=api_spec,
            base_url=base_url,
            auth_type=auth_type,
        )
