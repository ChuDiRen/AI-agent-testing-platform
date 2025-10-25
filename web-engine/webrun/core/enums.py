"""
枚举类型定义
用于定义Web自动化测试引擎中的常量
"""
from enum import Enum

from selenium.webdriver.common.by import By


class LocatorType(str, Enum):
    """元素定位方式枚举"""
    ID = "id"
    NAME = "name"
    CLASS_NAME = "class"
    CLASS_NAME_FULL = "class_name"
    TAG_NAME = "tag"
    TAG_NAME_FULL = "tag_name"
    XPATH = "xpath"
    CSS_SELECTOR = "css"
    CSS_SELECTOR_FULL = "css_selector"
    LINK_TEXT = "link"
    LINK_TEXT_FULL = "link_text"
    PARTIAL_LINK_TEXT = "partial_link"
    PARTIAL_LINK_TEXT_FULL = "partial_link_text"
    
    def to_selenium_by(self) -> str:
        """转换为 Selenium By 定位器"""
        mapping = {
            self.ID: By.ID,
            self.NAME: By.NAME,
            self.CLASS_NAME: By.CLASS_NAME,
            self.CLASS_NAME_FULL: By.CLASS_NAME,
            self.TAG_NAME: By.TAG_NAME,
            self.TAG_NAME_FULL: By.TAG_NAME,
            self.XPATH: By.XPATH,
            self.CSS_SELECTOR: By.CSS_SELECTOR,
            self.CSS_SELECTOR_FULL: By.CSS_SELECTOR,
            self.LINK_TEXT: By.LINK_TEXT,
            self.LINK_TEXT_FULL: By.LINK_TEXT,
            self.PARTIAL_LINK_TEXT: By.PARTIAL_LINK_TEXT,
            self.PARTIAL_LINK_TEXT_FULL: By.PARTIAL_LINK_TEXT,
        }
        return mapping[self]


class BrowserType(str, Enum):
    """浏览器类型枚举"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"


class WindowSize(str, Enum):
    """窗口大小枚举"""
    MAXIMIZE = "maximize"
    FULLSCREEN = "fullscreen"
    # 可以添加更多预定义尺寸
    HD = "1366x768"
    FULL_HD = "1920x1080"
    MOBILE = "375x667"


class CaseType(str, Enum):
    """测试用例类型枚举"""
    YAML = "yaml"
    EXCEL = "excel"
    PYTEST = "pytest"


__all__ = ["LocatorType", "BrowserType", "WindowSize", "CaseType"]

