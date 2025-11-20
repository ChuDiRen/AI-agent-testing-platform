"""运行脚本 - 支持演示与流式 CLI"""
import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer


def setup_python_path():
    """配置Python导入路径，支持直接运行此脚本"""
    current_dir = Path(__file__).resolve().parent
    agent_backend_dir = current_dir.parent.parent
    if str(agent_backend_dir) not in sys.path:
        sys.path.insert(0, str(agent_backend_dir))


setup_python_path()

from examples.auto_testcase_generator.agents.writer_agent import WriterProgressHook
from examples.auto_testcase_generator.generator import generator


DEFAULT_REQUIREMENT = """
用户登录接口：POST /api/v1/auth/login

功能：用户名密码登录，返回JWT Token（有效期24小时）

参数：
- username: 必填，3-20字符
- password: 必填，6-20字符

业务规则：
- 连续失败5次锁定30分钟
- 密码错误返回剩余尝试次数
"""

app = typer.Typer(help="AI测试用例自动生成器 CLI")


def build_cli_progress_hook() -> WriterProgressHook:
    """构建用于 CLI 实时进度的 writer hook"""
    bar_width = 40

    async def _hook(chunk_updates: dict) -> None:
        current = chunk_updates.get("writer_current_chunk", 0)
        total = chunk_updates.get("writer_total_chunks", 0)
        progress = chunk_updates.get("writer_progress", 0.0)
        percent = int(progress * 100)
        filled = min(bar_width, int(bar_width * progress))
        bar = "█" * filled + "-" * (bar_width - filled)
        sys.stdout.write(f"\rWriter：[{bar}] {percent}% ({current}/{total})")
        sys.stdout.flush()
        if total and current == total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    return _hook


async def _run_requirement(
    requirement: str,
    test_type: str = "API",
    max_iterations: int = 2,
    writer_status_hook: Optional[WriterProgressHook] = None,
) -> None:
    """运行生成逻辑并打印摘要"""
    print("\n" + "=" * 60)
    print(f"AI测试用例自动生成器 ({test_type})")
    print("=" * 60)
    print(f"\n需求:\n{requirement.strip()}\n")

    try:
        result = await asyncio.wait_for(
            generator.generate(
                requirement,
                test_type=test_type,
                max_iterations=max_iterations,
                writer_status_hook=writer_status_hook,
            ),
            timeout=480.0,
        )

        print("\n" + "=" * 60)
        print("测试用例")
        print("=" * 60)
        print(f"\n{result.testcases}\n")
        print("=" * 60)
        print(f"迭代次数: {result.iteration}")
        print("=" * 60 + "\n")

    except asyncio.TimeoutError:
        print("\n❌ 超时错误: AI模型调用超时(8分钟)")
        print("💡 建议: 检查网络连接或简化需求描述\n")

    except Exception as exc:
        print(f"\n❌ 错误: {type(exc).__name__}: {str(exc)}")
        import traceback
        traceback.print_exc()
        print("\n💡 请检查API配置和网络连接\n")


@app.command(name="text")
def demo_text(max_iterations: int = typer.Option(2, help="最大迭代次数")) -> None:
    """从文本需求运行演示"""
    asyncio.run(_run_requirement(DEFAULT_REQUIREMENT, max_iterations=max_iterations))


@app.command(name="stream")
def stream_text(
    requirement_file: Optional[Path] = typer.Option(
        None,
        "-f",
        "--file",
        exists=True,
        readable=True,
        help="读取需求的文本文件",
    ),
    requirement_text: Optional[str] = typer.Option(
        None,
        "-t",
        "--text",
        help="直接传入需求文本（多行使用换行符）",
    ),
    max_iterations: int = typer.Option(2, help="最大迭代次数"),
) -> None:
    """使用流式进度输出需求"""
    if not requirement_text and not requirement_file:
        raise typer.BadParameter("请输入 --text 或 --file 中的至少一个参数。")
    requirement = requirement_text or requirement_file.read_text(encoding='utf-8')
    progress_hook = build_cli_progress_hook()
    asyncio.run(
        _run_requirement(
            requirement,
            max_iterations=max_iterations,
            writer_status_hook=progress_hook,
        )
    )


@app.command(name="swagger")
def demo_swagger() -> None:
    """从 Swagger 文档批量生成"""
    asyncio.run(generator.batch_generate_from_swagger(
        swagger_url="https://petstore.swagger.io/v2/swagger.json",
        max_apis=3,
        test_type="API",
    ))


@app.command(name="document")
def demo_document() -> None:
    """文档生成说明"""
    print("\n" + "=" * 80)
    print("🚀 示例3: 从文档生成测试用例")
    print("=" * 80 + "\n")
    print("📄 此功能需要提供文档路径")
    print("💡 使用方式: python run.py document <文档路径>")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    import sys
    # 如果没有提供命令参数,默认执行text命令
    if len(sys.argv) == 1:
        sys.argv.append("text")
    app()
