"""
LangGraph Dev 入口

直接使用 chat_graph.py 中的完整 Supervisor 多代理架构
"""

import sys
from pathlib import Path

# 添加父目录到 sys.path 以支持绝对导入
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from text2sql.chat_graph import create_text2sql_graph
from text2sql.database import setup_chinook, register_connection, DatabaseConfig

# 设置 Chinook 测试数据库并注册连接
db_path = setup_chinook()
config = DatabaseConfig(db_type="sqlite", database=str(db_path))
register_connection(0, config)

# 导出完整版图（Supervisor 多代理架构）
graph = create_text2sql_graph(
    connection_id=0,
    dialect="sqlite"
)
