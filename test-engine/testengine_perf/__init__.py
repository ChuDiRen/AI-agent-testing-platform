"""
testengine_perf - 性能测试引擎
基于 Locust 实现
"""
from .core.globalContext import g_context
from .extend.keywords import PerfKeywords

__all__ = ["g_context", "PerfKeywords"]
