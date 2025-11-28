"""
提示词管理模块

支持从Markdown文件加载和动态格式化提示词
"""

from .loader import load_prompt, clear_cache, get_prompt_path

__all__ = ["load_prompt", "clear_cache", "get_prompt_path"]
