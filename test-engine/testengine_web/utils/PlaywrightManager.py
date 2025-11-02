"""
Playwright 浏览器管理器
支持 Chromium、Firefox、WebKit 浏览器
使用 Playwright 原生浏览器管理
"""
from playwright.sync_api import sync_playwright


class PlaywrightManager:
    """Playwright 浏览器管理器"""
    
    _playwright = None
    _browser = None
    _context = None
    _page = None

    @staticmethod
    def create_page(browser="chromium", headless=False, timeout=60000, window_size="maximize", **kwargs):
        """
        创建 Playwright 页面实例

        :param browser: 浏览器类型 (chromium/firefox/webkit)
        :param headless: 是否无头模式
        :param timeout: 默认超时时间（毫秒，默认60秒）
        :param window_size: 窗口大小 (maximize/1920x1080/等)
        :param kwargs: 其他浏览器选项
        :return: Page 实例
        """
        browser = browser.lower()

        # 启动 Playwright
        if PlaywrightManager._playwright is None:
            PlaywrightManager._playwright = sync_playwright().start()

        # 创建浏览器实例
        if browser == "chromium" or browser == "chrome":
            PlaywrightManager._browser = PlaywrightManager._playwright.chromium.launch(
                headless=headless,
                **kwargs
            )
        elif browser == "firefox":
            PlaywrightManager._browser = PlaywrightManager._playwright.firefox.launch(
                headless=headless,
                **kwargs
            )
        elif browser == "webkit" or browser == "safari":
            PlaywrightManager._browser = PlaywrightManager._playwright.webkit.launch(
                headless=headless,
                **kwargs
            )
        else:
            raise ValueError(f"不支持的浏览器类型: {browser}，支持的类型: chromium, firefox, webkit")

        # 创建浏览器上下文
        context_options = {}

        # 设置窗口大小
        if window_size != "maximize":
            if "x" in window_size:
                width, height = map(int, window_size.split("x"))
                context_options["viewport"] = {"width": width, "height": height}

        PlaywrightManager._context = PlaywrightManager._browser.new_context(**context_options)

        # 设置默认超时（60秒，适应网络延迟）
        PlaywrightManager._context.set_default_timeout(timeout)
        PlaywrightManager._context.set_default_navigation_timeout(timeout)
        
        # 创建页面
        PlaywrightManager._page = PlaywrightManager._context.new_page()
        
        # 如果是 maximize，设置视口为最大
        if window_size == "maximize":
            PlaywrightManager._page.set_viewport_size({"width": 1920, "height": 1080})
        
        return PlaywrightManager._page

    @staticmethod
    def get_current_page():
        """获取当前页面实例"""
        return PlaywrightManager._page

    @staticmethod
    def get_current_context():
        """获取当前浏览器上下文"""
        return PlaywrightManager._context

    @staticmethod
    def get_current_browser():
        """获取当前浏览器实例"""
        return PlaywrightManager._browser

    @staticmethod
    def close_page():
        """关闭当前页面"""
        if PlaywrightManager._page:
            PlaywrightManager._page.close()
            PlaywrightManager._page = None

    @staticmethod
    def close_context():
        """关闭浏览器上下文"""
        if PlaywrightManager._context:
            PlaywrightManager._context.close()
            PlaywrightManager._context = None

    @staticmethod
    def close_browser():
        """关闭浏览器"""
        if PlaywrightManager._browser:
            PlaywrightManager._browser.close()
            PlaywrightManager._browser = None

    @staticmethod
    def close_all():
        """关闭所有资源"""
        PlaywrightManager.close_page()
        PlaywrightManager.close_context()
        PlaywrightManager.close_browser()
        if PlaywrightManager._playwright:
            PlaywrightManager._playwright.stop()
            PlaywrightManager._playwright = None

    @staticmethod
    def new_page():
        """在当前上下文中创建新页面"""
        if PlaywrightManager._context:
            PlaywrightManager._page = PlaywrightManager._context.new_page()
            return PlaywrightManager._page
        else:
            raise RuntimeError("浏览器上下文未初始化，请先调用 create_page()")

    @staticmethod
    def switch_to_page(page_index=0):
        """切换到指定页面"""
        if PlaywrightManager._context:
            pages = PlaywrightManager._context.pages
            if 0 <= page_index < len(pages):
                PlaywrightManager._page = pages[page_index]
                return PlaywrightManager._page
            else:
                raise IndexError(f"页面索引 {page_index} 超出范围，当前有 {len(pages)} 个页面")
        else:
            raise RuntimeError("浏览器上下文未初始化")

    @staticmethod
    def get_all_pages():
        """获取所有页面"""
        if PlaywrightManager._context:
            return PlaywrightManager._context.pages
        else:
            return []

    @staticmethod
    def set_default_timeout(timeout):
        """设置默认超时时间"""
        if PlaywrightManager._context:
            PlaywrightManager._context.set_default_timeout(timeout)
        if PlaywrightManager._page:
            PlaywrightManager._page.set_default_timeout(timeout)

    @staticmethod
    def set_viewport_size(width, height):
        """设置视口大小"""
        if PlaywrightManager._page:
            PlaywrightManager._page.set_viewport_size({"width": width, "height": height})

    @staticmethod
    def enable_tracing(name="trace", screenshots=True, snapshots=True):
        """启用追踪功能"""
        if PlaywrightManager._context:
            PlaywrightManager._context.tracing.start(
                name=name,
                screenshots=screenshots,
                snapshots=snapshots
            )

    @staticmethod
    def stop_tracing(path="trace.zip"):
        """停止追踪并保存"""
        if PlaywrightManager._context:
            PlaywrightManager._context.tracing.stop(path=path)
