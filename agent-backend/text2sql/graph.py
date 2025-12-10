"""
LangGraph Dev 入口

直接使用 chat_graph.py 中的完整 Supervisor 多代理架构
"""

from .chat_graph import create_text2sql_graph
from .database import setup_chinook

# 设置 Chinook 测试数据库
db_path = setup_chinook()

# 导出完整版图（Supervisor 多代理架构）
graph = create_text2sql_graph(
    connection_id=0,
    dialect="sqlite"
)
