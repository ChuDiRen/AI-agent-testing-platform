#!/usr/bin/env python3
"""
Text2SQL LangGraph API 启动脚本

继承官方 LangGraph API，注入自定义 checkpointer 和 store

启动: python run.py [port]
"""

import sys
import os
from pathlib import Path

# 添加父目录到 sys.path
_root = Path(__file__).parent.parent.resolve()
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def main():
    """启动服务"""
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8000

    # 确保数据目录存在
    data_dir = _root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1. 设置环境变量（必须在导入 langgraph_api 之前）
    os.environ.setdefault("LANGGRAPH_RUNTIME_EDITION", "inmem")
    os.environ.setdefault("LANGGRAPH_AUTH_TYPE", "noop")
    os.environ.setdefault("MIGRATIONS_PATH", "/storage/migrations/inmem")
    os.environ.setdefault("DATABASE_URI", f"sqlite:///{data_dir / 'langgraph.db'}")
    os.environ.setdefault("REDIS_URI", "")

    # 使用模块路径
    os.environ.setdefault("LANGSERVE_GRAPHS", '{"text2sql": "text2sql.chat_graph:graph"}')
    os.environ.setdefault("LANGGRAPH_HTTP", '{"app": "text2sql.api.server:app"}')

    # 2. 初始化数据库
    from text2sql.database import setup_chinook, register_connection, DatabaseConfig
    db_path = setup_chinook()
    register_connection(0, DatabaseConfig(db_type="sqlite", database=str(db_path)))

    # 3. 启动
    print(f"\n🚀 Text2SQL API: http://0.0.0.0:{port}")
    print(f"📚 Docs: http://0.0.0.0:{port}/docs\n")

    import uvicorn
    from langgraph_api.server import app
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
