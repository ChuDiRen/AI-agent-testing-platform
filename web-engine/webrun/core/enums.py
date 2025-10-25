"""
枚举类型定义
用于定义Web自动化测试引擎中的常量
"""
from enum import Enum


class CaseType(str, Enum):
    """测试用例类型枚举"""
    YAML = "yaml"
    EXCEL = "excel"
    PYTEST = "pytest"


class BrowserType(str, Enum):
    """浏览器类型枚举"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


class LocatorType(str, Enum):
    """元素定位方式枚举"""
    ID = "id"
    NAME = "name"
    CLASS_NAME = "class_name"
    TAG_NAME = "tag_name"
    XPATH = "xpath"
    CSS_SELECTOR = "css_selector"
    LINK_TEXT = "link_text"
    PARTIAL_LINK_TEXT = "partial_link_text"


class WaitCondition(str, Enum):
    """等待条件枚举"""
    PRESENCE = "presence"  # 元素存在于DOM中
    VISIBLE = "visible"  # 元素可见
    CLICKABLE = "clickable"  # 元素可点击
    INVISIBLE = "invisible"  # 元素不可见


__all__ = ["CaseType", "BrowserType", "LocatorType", "WaitCondition"]
