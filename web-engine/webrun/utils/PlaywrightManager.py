"""
Playwright 浏览器管理器
支持 Chromium、Firefox、WebKit 浏览器
"""
import asyncio
from typing import Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright


class PlaywrightManager:
    """Playwright 浏览器管理器"""
    
    _playwright: Optional[Playwright] = None
    _browser: Optional[Browser] = None
    _context: Optional[BrowserContext] = None
    _page: Optional[Page] = None
    
    @classmethod
    def create_browser(cls, browser_type: str = "chromium", headless: bool = False, 
                       timeout: int = 30000, viewport: dict = None) -> Page:
        """
        创建浏览器并返回页面实例
        
        :param browser_type: 浏览器类型 (chromium/firefox/webkit)
        :param headless: 是否无头模式
        :param timeout: 默认超时时间（毫秒）
        :param viewport: 视口大小 {"width": 1920, "height": 1080}
        :return: Page 实例
        """
        # 启动 Playwright
        cls._playwright = sync_playwright().start()
        
        # 选择浏览器类型
        browser_type = browser_type.lower()
        if browser_type in ["chromium", "chrome"]:
            browser_launcher = cls._playwright.chromium
        elif browser_type == "firefox":
            browser_launcher = cls._playwright.firefox
        elif browser_type in ["webkit", "safari"]:
            browser_launcher = cls._playwright.webkit
        elif browser_type == "edge":
            # Edge 使用 Chromium 内核，通过 channel 指定
            browser_launcher = cls._playwright.chromium
            cls._browser = browser_launcher.launch(
                headless=headless,
                channel="msedge"
            )
        else:
            raise ValueError(f"不支持的浏览器类型: {browser_type}，支持的类型: chromium, firefox, webkit, edge")
        
        # 启动浏览器（非 Edge 情况）
        if cls._browser is None:
            cls._browser = browser_launcher.launch(headless=headless)
        
        # 创建浏览器上下文
        context_options = {
            "viewport": viewport or {"width": 1920, "height": 1080},
        }
        cls._context = cls._browser.new_context(**context_options)
        cls._context.set_default_timeout(timeout)
        
        # 创建页面
        cls._page = cls._context.new_page()
        
        return cls._page
    
    @classmethod
    def get_page(cls) -> Optional[Page]:
        """获取当前页面"""
        return cls._page
    
    @classmethod
    def get_context(cls) -> Optional[BrowserContext]:
        """获取当前浏览器上下文"""
        return cls._context
    
    @classmethod
    def get_browser(cls) -> Optional[Browser]:
        """获取当前浏览器"""
        return cls._browser
    
    @classmethod
    def close(cls):
        """关闭浏览器和 Playwright"""
        if cls._page:
            cls._page.close()
            cls._page = None
        if cls._context:
            cls._context.close()
            cls._context = None
        if cls._browser:
            cls._browser.close()
            cls._browser = None
        if cls._playwright:
            cls._playwright.stop()
            cls._playwright = None
    
    @classmethod
    def new_page(cls) -> Optional[Page]:
        """创建新页面"""
        if cls._context:
            return cls._context.new_page()
        return None
    
    @classmethod
    def switch_to_page(cls, index: int = -1) -> Optional[Page]:
        """
        切换到指定页面
        
        :param index: 页面索引，-1 表示最后一个
        :return: Page 实例
        """
        if cls._context:
            pages = cls._context.pages
            if pages:
                cls._page = pages[index]
                return cls._page
        return None
