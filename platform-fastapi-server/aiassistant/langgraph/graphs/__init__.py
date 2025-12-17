"""
LangGraph Graphs 模块

定义多个LangGraph图，供langgraph dev服务器使用:
- text2case: 自然语言生成测试用例
- text2sql: 自然语言转SQL查询
- text2api: 自然语言生成API请求
"""
from .text2case import graph as text2case_graph
from .text2sql import graph as text2sql_graph
from .text2api import graph as text2api_graph

__all__ = [
    "text2case_graph",
    "text2sql_graph",
    "text2api_graph",
]
