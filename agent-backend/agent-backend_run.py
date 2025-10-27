# Copyright (c) 2025 左岚. All rights reserved.
import subprocess
import os
import sys
from pathlib import Path

# 添加 src 目录到 Python 搜索路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# 设置环境变量以允许阻塞调用
os.environ["BG_JOB_ISOLATED_LOOPS"] = "true"

# 使用 --allow-blocking 参数启动 LangGraph
env = os.environ.copy()
existing_pythonpath = env.get("PYTHONPATH", "")
env["PYTHONPATH"] = (
    f"{str(src_path)}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else str(src_path)
)
subprocess.run(["langgraph", "dev", "--allow-blocking"], env=env, cwd=str(Path(__file__).parent))
