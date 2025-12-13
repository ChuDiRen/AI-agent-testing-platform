"""
Perf Engine - 基于 Locust 的性能测试引擎

采用关键字驱动和数据驱动的设计理念，支持 YAML 格式编写性能测试用例。
"""

__version__ = "1.0.0"
__author__ = "ChuDiRen"

from .core.globalContext import g_context
from .core.exceptions import (
    EngineError,
    ParserError,
    CaseNotFoundError,
    KeywordError,
    ContextError,
    LocustError,
)

__all__ = [
    "__version__",
    "__author__",
    "g_context",
    "EngineError",
    "ParserError",
    "CaseNotFoundError",
    "KeywordError",
    "ContextError",
    "LocustError",
]
