"""
浏览器驱动管理器
支持 Chrome、Firefox、Edge 浏览器
使用 webdriver-manager 自动管理驱动
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class DriverManager:
    """浏览器驱动管理器"""

    @staticmethod
    def create_driver(browser="chrome", headless=False, implicit_wait=10, window_size="maximize"):
        """
        创建浏览器驱动实例
        
        :param browser: 浏览器类型 (chrome/firefox/edge)
        :param headless: 是否无头模式
        :param implicit_wait: 隐式等待时间（秒）
        :param window_size: 窗口大小 (maximize/1920x1080/等)
        :return: WebDriver 实例
        """
        browser = browser.lower()
        
        if browser == "chrome":
            driver = DriverManager._create_chrome_driver(headless)
        elif browser == "firefox":
            driver = DriverManager._create_firefox_driver(headless)
        elif browser == "edge":
            driver = DriverManager._create_edge_driver(headless)
        else:
            raise ValueError(f"不支持的浏览器类型: {browser}，支持的类型: chrome, firefox, edge")
        
        # 设置隐式等待
        if implicit_wait > 0:
            driver.implicitly_wait(implicit_wait)
        
        # 设置窗口大小
        if window_size == "maximize":
            driver.maximize_window()
        elif "x" in str(window_size):
            width, height = window_size.split("x")
            driver.set_window_size(int(width), int(height))
        
        return driver

    @staticmethod
    def _create_chrome_driver(headless=False):
        """创建 Chrome 驱动"""
        options = webdriver.ChromeOptions()
        
        if headless:
            options.add_argument("--headless")
        
        # 通用配置
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        return driver

    @staticmethod
    def _create_firefox_driver(headless=False):
        """创建 Firefox 驱动"""
        options = webdriver.FirefoxOptions()
        
        if headless:
            options.add_argument("--headless")
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        
        return driver

    @staticmethod
    def _create_edge_driver(headless=False):
        """创建 Edge 驱动"""
        options = webdriver.EdgeOptions()
        
        if headless:
            options.add_argument("--headless")
        
        # 通用配置
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        
        return driver

