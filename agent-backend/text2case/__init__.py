"""text2case - AI测试用例生成器

基于 LangGraph 官方 langgraph_supervisor 构建
使用 Supervisor + ReAct Agents 模式

使用方式:
    # 同步调用（简单模式）
    from text2case.chat_graph import run_text2case_sync
    result = run_text2case_sync("用户登录接口...", test_type="API")
    
    # 异步调用（带记忆）
    from text2case.chat_graph import run_text2case
    result = await run_text2case("用户登录接口...", thread_id="session_123")
"""
import sys
import os

# Windows控制台UTF-8编码
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from .config import LLMConfig, get_model
from .chat_graph import (
    create_text2case_graph,
    run_text2case,
    run_text2case_sync,
    graph,
    get_app,
    get_app_simple,
)
from .models import TestCaseState, TestCaseSuite, TestCaseModule, TestCaseItem

__all__ = [
    # 配置
    'LLMConfig',
    'get_model',
    # 图工厂
    'create_text2case_graph',
    'graph',
    'get_app',
    'get_app_simple',
    # 便捷函数
    'run_text2case',
    'run_text2case_sync',
    # 数据模型
    'TestCaseState',
    'TestCaseSuite',
    'TestCaseModule',
    'TestCaseItem',
]

__version__ = "6.0.0"
