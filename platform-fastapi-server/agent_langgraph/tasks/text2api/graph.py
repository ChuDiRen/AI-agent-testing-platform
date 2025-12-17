"""
Text2API Graph Builder

API请求生成任务的Graph构建器
"""
import logging
from typing import Dict, Callable, List, Tuple, Type

from agent_langgraph.tasks.text2api.state import Text2APIState
from agent_langgraph.tasks.text2api.nodes import understand_description, generate_api_request
from agent_langgraph.core import BaseGraphBuilder
from agent_langgraph.tasks.registry import TaskRegistry

logger = logging.getLogger(__name__)


class Text2APIGraphBuilder(BaseGraphBuilder[Text2APIState]):
    """
    Text2API Graph构建器
    
    流程：理解描述 -> 生成API请求
    """
    
    task_type = "text2api"
    
    def get_state_class(self) -> Type[Text2APIState]:
        return Text2APIState
    
    def get_nodes(self) -> Dict[str, Callable[[Text2APIState], Text2APIState]]:
        return {
            "understand_description": understand_description,
            "generate_api_request": generate_api_request,
        }
    
    def get_edges(self) -> List[Tuple[str, str]]:
        return [
            ("START", "understand_description"),
            ("understand_description", "generate_api_request"),
            ("generate_api_request", "END"),
        ]


# 注册任务
TaskRegistry.register("text2api", Text2APIGraphBuilder)

# 导出graph实例供langgraph dev使用
graph = Text2APIGraphBuilder().build()
