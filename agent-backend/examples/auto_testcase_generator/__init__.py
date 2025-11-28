"""
自动测试用例生成器 V3 (Auto Testcase Generator V3)

核心架构:
- 4个专家智能体: Analyzer, TestPointDesigner, Writer, Reviewer
- 1个Supervisor协调者: 调度智能体执行顺序
- middlewareV1: 上下文工程优化 (消息过滤、状态同步、动态注入)
- 人工审核: 在关键步骤暂停等待确认
- 持久化存储: 保存生成历史到数据库

使用示例:
    from auto_testcase_generator import generator
    import asyncio

    # 使用全局生成器实例
    result = await generator.generate("需求描述...", test_type="API")

    # 或创建自定义生成器
    from auto_testcase_generator import TestCaseGeneratorV3
    custom_generator = TestCaseGeneratorV3(
        enable_middleware=True,
        enable_human_review=True,
        enable_persistence=True,
    )
    result = await custom_generator.generate("需求描述...", test_type="API")
"""
import sys
import os

# 修复 Windows 控制台编码问题 (支持 emoji 和中文)
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from .config import Config
from .generator import generator, TestCaseGeneratorV3
from .models import TestCaseState
from .batch_processor import BatchProcessor, BatchConfig, BatchResult

__all__ = [
    'generator',  # 全局实例
    'TestCaseGeneratorV3',  # 类
    'TestCaseState',
    'Config',
    # 批量处理
    'BatchProcessor',
    'BatchConfig',
    'BatchResult',
]

__version__ = "5.0.0"  # 升级版本号

