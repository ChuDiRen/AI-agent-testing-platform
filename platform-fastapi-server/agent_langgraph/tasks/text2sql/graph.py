"""
Text2SQL Graph Builder

SQL生成任务的Graph构建器
"""
import logging
from typing import Dict, Callable, List, Tuple, Type

from langgraph.graph import END

from agent_langgraph.tasks.text2sql.state import Text2SQLState
from agent_langgraph.tasks.text2sql.nodes import understand_question, generate_sql, validate_sql
from agent_langgraph.core import BaseGraphBuilder
from agent_langgraph.tasks.registry import TaskRegistry

logger = logging.getLogger(__name__)


class Text2SQLGraphBuilder(BaseGraphBuilder[Text2SQLState]):
    """
    Text2SQL Graph构建器
    
    流程：理解问题 -> 生成SQL -> 验证SQL
    """
    
    task_type = "text2sql"
    
    def get_state_class(self) -> Type[Text2SQLState]:
        return Text2SQLState
    
    def get_nodes(self) -> Dict[str, Callable[[Text2SQLState], Text2SQLState]]:
        return {
            "understand_question": understand_question,
            "generate_sql": generate_sql,
            "validate_sql": validate_sql,
        }
    
    def get_edges(self) -> List[Tuple[str, str]]:
        return [
            ("START", "understand_question"),
            ("understand_question", "generate_sql"),
            ("generate_sql", "validate_sql"),
            ("validate_sql", "END"),
        ]


# 注册任务
TaskRegistry.register("text2sql", Text2SQLGraphBuilder)

# 导出graph实例供langgraph dev使用
graph = Text2SQLGraphBuilder().build()
