"""
自动测试用例生成器 V3 (Auto Testcase Generator V3)

核心架构:
- 4个专家智能体: Analyzer, TestPointDesigner, Writer, Reviewer
- 1个Supervisor协调者: 调度智能体执行顺序
- middlewareV1: 上下文工程优化 (消息过滤、状态同步、动态注入)
- 人工审核: 在关键步骤暂停等待确认
- 持久化存储: 保存生成历史到数据库

使用示例:
    from auto_testcase_generator import TestCaseGeneratorV3
    import asyncio

    # 创建生成器
    generator = TestCaseGeneratorV3(
        enable_middleware=True,
        enable_human_review=False,
        enable_persistence=True,
    )

    # 生成测试用例
    result = await generator.generate("需求描述...", test_type="API")
"""

from .generator_v3 import TestCaseGeneratorV3
from .models import TestCaseState
from .config import Config

__all__ = [
    'TestCaseGeneratorV3',
    'TestCaseState',
    'Config',
]

__version__ = "3.0.0"

