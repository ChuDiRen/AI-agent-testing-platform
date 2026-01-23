"""
项目启动脚本
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """运行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode


def main():
    """主函数"""
    backend_dir = Path(__file__).parent / "backend"

    print("=" * 50)
    print("企业级智能知识库系统启动脚本")
    print("=" * 50)
    print()

    # 检查环境变量配置
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("警告: .env 文件不存在，请从 .env.example 复制并配置")
        print("运行: cp .env.example .env")
        return

    print("✓ 环境变量配置已找到")

    # 安装依赖
    print()
    print("安装 Python 依赖...")
    if run_command("pip install -r requirements.txt", cwd=backend_dir) != 0:
        print("✗ 依赖安装失败")
        return
    print("✓ 依赖安装完成")

    # 初始化数据库
    print()
    print("初始化数据库...")
    if run_command("python scripts/init_db.py", cwd=backend_dir) != 0:
        print("⚠ 数据库初始化失败，可能需要先创建数据库")

    # 启动后端服务
    print()
    print("启动后端服务...")
    print("访问 http://localhost:8000/docs 查看 API 文档")
    print("按 Ctrl+C 停止服务")
    print()

    try:
        run_command("python app/main.py", cwd=backend_dir)
    except KeyboardInterrupt:
        print()
        print("服务已停止")


if __name__ == "__main__":
    main()
