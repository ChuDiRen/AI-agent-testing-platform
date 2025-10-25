"""
自定义异常类
定义测试引擎的异常层次结构
"""


class EngineError(Exception):
    """引擎基础异常"""
    pass


class ParserError(EngineError):
    """解析器异常"""
    pass


class CaseNotFoundError(EngineError):
    """用例未找到异常"""
    pass


class KeywordError(EngineError):
    """关键字执行异常"""
    pass


class ContextError(EngineError):
    """上下文管理异常"""
    pass


__all__ = [
    "EngineError",
    "ParserError",
    "CaseNotFoundError",
    "KeywordError",
    "ContextError",
]

