#!/usr/bin/env python3
"""
LangGraph API 服务器启动脚本
支持 SQLite 持久化存储（通过 langgraph.json 配置）和数据库checkpointer
"""

import subprocess
import sys
from pathlib import Path

# 在启动前设置checkpointer
try:
    from aiassistant.langgraph.checkpointer import create_database_checkpointer
    from aiassistant.langgraph.graph import build_graph
    
    # 创建数据库checkpointer
    db_checkpointer = create_database_checkpointer()
    
    # 构建使用数据库checkpointer的图
    graph = build_graph(checkpointer=db_checkpointer)
    
    print("[配置] 已启用数据库checkpointer")
except Exception as e:
    print(f"[警告] 数据库checkpointer初始化失败，将使用默认文件存储: {e}")
    print("[配置] 使用默认文件存储")


def run_langgraph_server(root: Path, port: int = 2024):
    """运行 LangGraph 服务器（社区版本地模式 + SQLite 持久化）"""
    
    # 准备 SQLite 数据库路径
    db_dir = root / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[配置] 数据库目录: {db_dir}")
    print(f"[配置] 数据库文件: {db_dir / 'agent_checkpoints.db'}")
    print(f"[配置] 运行模式: 社区版本地开发模式 (SQLite 持久化)")
    print(f"[配置] 配置文件: langgraph.json (已配置 checkpointer 和 store)")
    print(f"[配置] 环境变量: .env\n")
    
    # 使用 langgraph dev 命令启动服务器（社区版，无需 Docker）
    # 自动读取 langgraph.json 和 .env 配置
    # --allow-blocking: 允许阻塞调用（用于 MCP 工具加载）
    return subprocess.run(
        [
            "langgraph",
            "dev",
            "--port", str(port),
            "--host", "0.0.0.0",
            "--no-browser",
            "--allow-blocking"
        ],
        cwd=root,
        check=False
    )


def main():
    """启动 LangGraph 服务器"""
    root = Path(__file__).parent
    port = 2024
    
    try:
        print(f"[启动] 正在启动 LangGraph API 服务器...")
        print(f"[启动] 端口: {port}")
        print(f"[启动] API地址: http://localhost:{port}")
        print(f"[启动] 按 Ctrl+C 停止服务\n")
        
        run_langgraph_server(root, port)
        
    except KeyboardInterrupt:
        print("\n[停止] 服务器已停止")
    except Exception as e:
        print(f"\n[错误] 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
