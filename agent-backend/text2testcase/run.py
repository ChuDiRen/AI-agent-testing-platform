"""CLI入口 - 测试用例生成器命令行工具"""
import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

import typer

# Windows控制台UTF-8编码
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from .agents.writer_agent import WriterProgressHook
from .generator import generator


# 默认演示需求
DEFAULT_REQUIREMENT = """
用户登录接口：POST /api/v1/auth/login
功能：用户名密码登录，返回JWT Token（有效期24小时）
参数：username(必填,3-20字符), password(必填,6-20字符)
业务规则：连续失败5次锁定30分钟，密码错误返回剩余尝试次数
"""

app = typer.Typer(help="AI测试用例生成器")


def build_cli_progress_hook() -> WriterProgressHook:
    """构建CLI进度条回调"""
    async def _hook(chunk_updates: dict) -> None:
        current = chunk_updates.get("writer_current_chunk", 0)
        total = chunk_updates.get("writer_total_chunks", 0)
        progress = chunk_updates.get("writer_progress", 0.0)
        filled = int(40 * progress)
        bar = "█" * filled + "-" * (40 - filled)
        sys.stdout.write(f"\rWriter：[{bar}] {int(progress*100)}% ({current}/{total})")
        sys.stdout.flush()
        if total and current == total:
            sys.stdout.write("\n")
    return _hook


async def _run_requirement(
    requirement: str,
    test_type: str = "API",
    max_iterations: int = 2,
    writer_status_hook: Optional[WriterProgressHook] = None,
) -> None:
    """执行生成流程"""
    print(f"\n{'='*60}\nAI测试用例生成器 ({test_type})\n{'='*60}")
    print(f"需求:\n{requirement.strip()}\n")

    try:
        result = await asyncio.wait_for(
            generator.generate(requirement, test_type=test_type,
                             max_iterations=max_iterations,
                             writer_status_hook=writer_status_hook),
            timeout=480.0,
        )
        print(f"\n{'='*60}\n测试用例\n{'='*60}")
        print(f"{result.testcases}\n{'='*60}")
        print(f"迭代次数: {result.iteration}\n")

    except asyncio.TimeoutError:
        print("\n❌ 超时(8分钟)，请检查网络或简化需求")
        raise typer.Exit(1)
    except Exception as exc:
        print(f"\n❌ {type(exc).__name__}: {exc}")
        raise typer.Exit(1)


@app.command(name="text")
def demo_text(max_iterations: int = typer.Option(2, help="最大迭代次数")) -> None:
    """运行默认演示"""
    asyncio.run(_run_requirement(DEFAULT_REQUIREMENT, max_iterations=max_iterations))


@app.command(name="stream")
def stream_text(
    requirement_file: Optional[Path] = typer.Option(None, "-f", "--file", exists=True, help="需求文件"),
    requirement_text: Optional[str] = typer.Option(None, "-t", "--text", help="需求文本"),
    max_iterations: int = typer.Option(2, help="最大迭代次数"),
) -> None:
    """流式进度输出"""
    if not requirement_text and not requirement_file:
        raise typer.BadParameter("请提供 --text 或 --file")
    requirement = requirement_text or requirement_file.read_text(encoding='utf-8')
    asyncio.run(_run_requirement(requirement, max_iterations=max_iterations,
                                 writer_status_hook=build_cli_progress_hook()))


@app.command(name="swagger")
def demo_swagger() -> None:
    """从Swagger批量生成"""
    asyncio.run(generator.batch_generate_from_swagger(
        swagger_url="https://petstore.swagger.io/v2/swagger.json",
        max_apis=3, test_type="API"))


@app.command(name="document")
def demo_document() -> None:
    """文档生成说明"""
    print("\n使用方式: python -m text2testcase.run document <文档路径>\n")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("text")
    try:
        app()
    except SystemExit as e:
        os._exit(e.code if e.code is not None else 0)
    os._exit(0)
