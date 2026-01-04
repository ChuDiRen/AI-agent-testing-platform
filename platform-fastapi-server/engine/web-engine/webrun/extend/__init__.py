"""
Web Engine 扩展模块

包含:
- keywords: Playwright 关键字库
- browser_use_keywords: Browser-Use AI 关键字库
"""

from .keywords import Keywords
from .browser_use_keywords import BrowserUseKeywords, get_browser_use_keywords

__all__ = [
    "Keywords",
    "BrowserUseKeywords", 
    "get_browser_use_keywords",
]