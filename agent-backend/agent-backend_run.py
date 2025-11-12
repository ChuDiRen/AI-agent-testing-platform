#!/usr/bin/env python3
"""
LangGraph API 服务器启动脚本
支持 SQLite 持久化存储
"""

import os
import subprocess
import sys
from pathlib import Path


def run_langgraph_server(root: Path, port: int = 2024):
    """运行 LangGraph 服务器"""
    src = root / "src"
    
    # 构建环境变量
    env = os.environ.copy()
    pythonpath_parts = filter(None, [str(src), env.get("PYTHONPATH")])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
    
    # 启动 LangGraph 开发服务器(允许CORS跨域)
    return subprocess.run(
        [
            "langgraph", "dev",
            "--allow-blocking",
            "--port", str(port),
            "--server-log-level", "INFO",
            "--host", "0.0.0.0"  # 允许外部访问
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
