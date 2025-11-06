#!/usr/bin/env python3
"""
简易 LangGraph API 服务器 - 单函数极简版

使用 subprocess 启动 LangGraph 开发服务器的最小化脚本
"""

import os
import sys
import subprocess
from pathlib import Path
from contextlib import suppress


def run_langgraph_server(root: Path, port: int = 2024):
    """运行 LangGraph 服务器 - 无日志纯净版"""
    src = root / "src"
    return subprocess.run(
        ["langgraph", "dev", "--allow-blocking", "--port", str(port), "--server-log-level", "ERROR"],
        env={**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, [str(src), os.environ.get("PYTHONPATH")]))},
        cwd=root, check=False
    )


def main():
    """启动 LangGraph 服务器 - 极致简化版"""
    # 初始化路径和环境（多重赋值 + filter + map）
    root, port = Path(__file__).parent, 2024
    sys.path[0:0] = list(map(str, filter(Path.exists, [root / d for d in ("src", "examples")])))
    os.environ["BG_JOB_ISOLATED_LOOPS"] = "true"
    
    # 加载 .env 文件（suppress + 动态导入 + 短路求值）
    with suppress(ImportError):
        (env_file := root / ".env").exists() and __import__('dotenv').load_dotenv(env_file)
    
    # 启动服务器（异常处理链）
    try:
        run_langgraph_server(root, port)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}") or __import__('traceback').print_exc() or sys.exit(1)


if __name__ == "__main__":
    main()
