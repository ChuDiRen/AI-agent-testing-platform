"""
Text2SQL - 智能自然语言到SQL转换系统

基于LangGraph的多代理架构实现，支持：
- 自然语言查询转SQL
- 多数据库支持
- 流式输出
- 图表可视化
- 智能错误恢复
"""

from .config import LLMConfig, get_model
from .state import SQLMessageState

__version__ = "0.1.0"
__all__ = ["LLMConfig", "get_model", "SQLMessageState"]
