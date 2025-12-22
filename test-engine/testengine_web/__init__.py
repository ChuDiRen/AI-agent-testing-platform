"""
testengine_web - Web UI 自动化测试引擎
基于 Playwright 实现
"""
from .core.globalContext import g_context
from .extend.keywords import Keywords

__all__ = ["g_context", "Keywords"]
