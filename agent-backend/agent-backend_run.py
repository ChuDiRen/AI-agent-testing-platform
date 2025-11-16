#!/usr/bin/env python3
"""
LangGraph API 服务器启动脚本
支持 SQLite 持久化存储（通过 langgraph.json 配置）
"""

import os
import subprocess
import sys
from pathlib import Path


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
    # 启动服务器
    try:
        print(f"[启动] 正在启动 LangGraph API 服务器...")
        print(f"[启动] 端口: {port}")
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
