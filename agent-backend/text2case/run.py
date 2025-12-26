"""CLI入口 - 测试用例生成器命令行工具

基于新架构 (langgraph_supervisor + ReAct Agents)
"""
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

from .chat_graph import run_text2case_sync, run_text2case


# 默认演示需求
DEFAULT_REQUIREMENT = """
用户登录接口：POST /api/v1/auth/login
功能：用户名密码登录，返回JWT Token（有效期24小时）
参数：username(必填,3-20字符), password(必填,6-20字符)
业务规则：连续失败5次锁定30分钟，密码错误返回剩余尝试次数
"""

app = typer.Typer(help="AI测试用例生成器 v6.0 (langgraph_supervisor 架构)")


async def _run_async(
    requirement: str,
    test_type: str = "API",
    enable_review: bool = False,
    enable_export: bool = False,
    thread_id: str = "default",
    user_id: str = "default",
) -> None:
    """异步执行生成流程"""
    print(f"\n{'='*60}\nAI测试用例生成器 ({test_type}) - 新架构\n{'='*60}")
    print(f"需求:\n{requirement.strip()}\n")
    print(f"📌 Thread ID: {thread_id}")

    try:
        result = await asyncio.wait_for(
            run_text2case(
                requirement=requirement,
                test_type=test_type,
                thread_id=thread_id,
                user_id=user_id,
                enable_review=enable_review,
                enable_export=enable_export,
            ),
            timeout=480.0,
        )
        
        print(f"\n{'='*60}\n测试用例\n{'='*60}")
        print(f"{result.get('content', '')}\n{'='*60}")

    except asyncio.TimeoutError:
        print("\n❌ 超时(8分钟)，请检查网络或简化需求")
        raise typer.Exit(1)
    except Exception as exc:
        print(f"\n❌ {type(exc).__name__}: {exc}")
        raise typer.Exit(1)


def _run_sync(
    requirement: str,
    test_type: str = "API",
    enable_review: bool = False,
    enable_export: bool = False,
    thread_id: str = "default",
    user_id: str = "default",
    use_memory: bool = True,
) -> None:
    """同步执行生成流程"""
    print(f"\n{'='*60}\nAI测试用例生成器 ({test_type}) - 新架构\n{'='*60}")
    print(f"需求:\n{requirement.strip()}\n")
    if use_memory:
        print(f"📌 Thread ID: {thread_id}")

    try:
        result = run_text2case_sync(
            requirement=requirement,
            test_type=test_type,
            thread_id=thread_id,
            user_id=user_id,
            enable_review=enable_review,
            enable_export=enable_export,
            use_memory=use_memory,
        )
        
        print(f"\n{'='*60}\n测试用例\n{'='*60}")
        print(f"{result.get('content', '')}\n{'='*60}")

    except Exception as exc:
        print(f"\n❌ {type(exc).__name__}: {exc}")
        raise typer.Exit(1)


@app.command(name="demo")
def demo(
    enable_review: bool = typer.Option(False, "--review", "-r", help="启用评审"),
    enable_export: bool = typer.Option(False, "--export", "-e", help="启用导出"),
    thread_id: str = typer.Option("demo", "--thread", "-t", help="会话ID"),
    no_memory: bool = typer.Option(False, "--no-memory", help="禁用记忆"),
) -> None:
    """运行默认演示"""
    _run_sync(
        DEFAULT_REQUIREMENT, 
        enable_review=enable_review, 
        enable_export=enable_export,
        thread_id=thread_id,
        use_memory=not no_memory,
    )


@app.command(name="generate")
def generate(
    requirement_file: Optional[Path] = typer.Option(None, "-f", "--file", exists=True, help="需求文件"),
    requirement_text: Optional[str] = typer.Option(None, "-t", "--text", help="需求文本"),
    test_type: str = typer.Option("API", "--type", help="测试类型: API/Web/App"),
    enable_review: bool = typer.Option(False, "--review", "-r", help="启用评审"),
    enable_export: bool = typer.Option(False, "--export", "-e", help="启用导出"),
    thread_id: str = typer.Option("default", "--thread", help="会话ID"),
    no_memory: bool = typer.Option(False, "--no-memory", help="禁用记忆"),
) -> None:
    """生成测试用例"""
    if not requirement_text and not requirement_file:
        raise typer.BadParameter("请提供 --text 或 --file")
    
    requirement = requirement_text or requirement_file.read_text(encoding='utf-8')
    _run_sync(
        requirement, 
        test_type=test_type, 
        enable_review=enable_review, 
        enable_export=enable_export,
        thread_id=thread_id,
        use_memory=not no_memory,
    )


@app.command(name="async")
def async_generate(
    requirement_file: Optional[Path] = typer.Option(None, "-f", "--file", exists=True, help="需求文件"),
    requirement_text: Optional[str] = typer.Option(None, "-t", "--text", help="需求文本"),
    test_type: str = typer.Option("API", "--type", help="测试类型: API/Web/App"),
    thread_id: str = typer.Option("default", "--thread", help="会话ID"),
    user_id: str = typer.Option("default", "--user", help="用户ID"),
    enable_review: bool = typer.Option(False, "--review", "-r", help="启用评审"),
    enable_export: bool = typer.Option(False, "--export", "-e", help="启用导出"),
) -> None:
    """异步生成测试用例（带持久化记忆）"""
    if not requirement_text and not requirement_file:
        raise typer.BadParameter("请提供 --text 或 --file")
    
    requirement = requirement_text or requirement_file.read_text(encoding='utf-8')
    asyncio.run(_run_async(
        requirement,
        test_type=test_type,
        thread_id=thread_id,
        user_id=user_id,
        enable_review=enable_review,
        enable_export=enable_export,
    ))


@app.command(name="version")
def version() -> None:
    """显示版本信息"""
    from . import __version__
    print(f"text2case v{__version__}")
    print("架构: langgraph_supervisor + ReAct Agents")
    print("记忆: SQLite 持久化 (data/agent_memory.db)")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("demo")
    try:
        app()
    except SystemExit as e:
        os._exit(e.code if e.code is not None else 0)
    os._exit(0)
