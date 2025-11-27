"""
上下文管理模块

提供消息裁剪和上下文压缩功能，防止上下文爆炸
"""

from text2sql.context.trimmer import MessageTrimmer, trim_messages
from text2sql.context.compressor import ContextCompressor
from text2sql.context.manager import ContextManager

__all__ = [
    "MessageTrimmer",
    "trim_messages",
    "ContextCompressor", 
    "ContextManager"
]
