#!/usr/bin/env python3
"""
LangGraph API 服务器启动脚本
支持 SQLite 持久化存储（生产模式）
"""

import os
import subprocess
import sys
from pathlib import Path


def run_langgraph_server(root: Path, port: int = 2024):
    """运行 LangGraph 服务器（生产模式 + SQLite 持久化）"""
    
    # 准备 SQLite 数据库路径
    db_dir = root / "sqlite_storage" / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "langgraph_server.db"
    
    # 构建环境变量
    env = os.environ.copy()
    
    # 关键：配置 SQLite 数据库 URI（生产模式）
    env["DATABASE_URI"] = f"sqlite:///{db_path}"
    
    # Redis URI（使用 fake 模式，不需要真实 Redis）
    env["REDIS_URI"] = "fake"
    
    # 设置为生产运行时版本（支持持久化）
    env["LANGGRAPH_RUNTIME_EDITION"] = "community"
    
    # 允许阻塞 IO
    env["LANGGRAPH_ALLOW_BLOCKING"] = "true"
    
    # 允许私有网络访问
    env["ALLOW_PRIVATE_NETWORK"] = "true"
    
    # 设置 PYTHONPATH
    pythonpath_parts = filter(None, [str(root), env.get("PYTHONPATH")])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
    
    print(f"[配置] 数据库路径: {db_path}")
    print(f"[配置] 运行模式: community (SQLite 持久化)")
    
    # 使用 uvicorn 直接启动生产模式服务器
    return subprocess.run(
        [
            sys.executable,
            "-m", "uvicorn",
            "langgraph_api.server:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--log-level", "info"
        ],
        env=env,
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
