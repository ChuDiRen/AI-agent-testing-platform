#!/usr/bin/env python3
"""
简易 LangGraph API 服务器

使用 subprocess 启动 LangGraph 开发服务器的最小化脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """设置必需的环境变量"""
    # 将 src 目录添加到 Python 路径
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    # 将 examples 目录添加到 Python 路径
    examples_path = Path(__file__).parent / "examples"
    if examples_path.exists():
        sys.path.insert(0, str(examples_path))

    # 设置环境变量
    os.environ["BG_JOB_ISOLATED_LOOPS"] = "true"  # 允许阻塞调用

    # 如果存在 .env 文件则加载
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✅ 已从 .env 文件加载环境变量")
        except ImportError:
            print("⚠️  未安装 python-dotenv,跳过 .env 文件加载")

def main():
    """启动服务器"""
    print("🚀 正在启动 LangGraph API 服务器...")

    # 设置环境
    setup_environment()

    # 打印服务器信息
    print("\n" + "="*60)
    print("📍 服务器地址: http://localhost:2025")
    print("📚 API 文档: http://localhost:2025/docs")
    print("🎨 LangGraph UI: http://localhost:2025/ui")
    print("💚 健康检查: http://localhost:2025/ok")
    print("="*60)

    try:
        # 设置 PYTHONPATH 环境变量
        env = os.environ.copy()
        src_path = Path(__file__).parent / "src"
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{str(src_path)}{os.pathsep}{existing_pythonpath}"
            if existing_pythonpath
            else str(src_path)
        )

        # 使用 langgraph dev 命令启动服务器 (添加详细日志)
        subprocess.run(
            ["langgraph", "dev", "--allow-blocking", "--port", "2025", "--server-log-level", "DEBUG"],
            env=env,
            cwd=str(Path(__file__).parent)
        )
    except KeyboardInterrupt:
        print("\n🛑 服务器已被用户停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
