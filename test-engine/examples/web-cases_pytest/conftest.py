"""
Web Pytest 测试配置文件（使用 Playwright）
提供公共的 fixtures 和配置
"""
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Page, Browser, BrowserContext, Playwright, sync_playwright


# ===========================
# 测试环境配置
# ===========================

def pytest_addoption(parser):
    """
    添加命令行选项
    """
    parser.addoption(
        "--browser",
        action="store",
        default="chromium",
        help="浏览器类型: chromium, firefox, webkit"
    )
    parser.addoption(
        "--headless",
        action="store",
        default="false",
        help="是否使用无头模式: true/false"
    )
    parser.addoption(
        "--base-url",
        action="store",
        default="https://www.baidu.com",
        help="测试基础 URL"
    )


@pytest.fixture(scope="session")
def browser_type_name(request) -> str:
    """
    获取浏览器类型
    """
    return request.config.getoption("--browser").lower()


@pytest.fixture(scope="session")
def headless_mode(request) -> bool:
    """
    获取是否使用无头模式
    """
    return request.config.getoption("--headless").lower() == "true"


@pytest.fixture(scope="session")
def base_url(request) -> str:
    """
    获取测试基础 URL
    """
    return request.config.getoption("--base-url")


# ===========================
# Playwright Fixtures
# ===========================

@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """
    创建 Playwright 实例（Session 级别）
    """
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(
    playwright_instance: Playwright,
    browser_type_name: str,
    headless_mode: bool
) -> Generator[Browser, None, None]:
    """
    创建浏览器实例（Session 级别）
    所有测试共享同一个浏览器
    """
    # 根据浏览器类型选择
    browser_types = {
        "chromium": playwright_instance.chromium,
        "firefox": playwright_instance.firefox,
        "webkit": playwright_instance.webkit,
        "chrome": playwright_instance.chromium,  # 别名
    }
    
    browser_type = browser_types.get(browser_type_name, playwright_instance.chromium)
    
    # 启动浏览器
    browser_instance = browser_type.launch(
        headless=headless_mode,
        args=['--start-maximized'] if not headless_mode else []
    )
    
    yield browser_instance
    
    # 关闭浏览器
    browser_instance.close()


@pytest.fixture
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    创建浏览器上下文（Function 级别）
    每个测试函数独立的上下文
    """
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080}
    )
    
    yield context
    
    # 关闭上下文
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """
    创建页面实例（Function 级别）
    每个测试函数独立的页面
    """
    page = context.new_page()
    
    yield page
    
    # 关闭页面
    page.close()


@pytest.fixture(scope="class")
def class_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    创建浏览器上下文（Class 级别）
    同一测试类共享上下文
    """
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080}
    )
    
    yield context
    
    context.close()


@pytest.fixture(scope="class")
def class_page(class_context: BrowserContext) -> Generator[Page, None, None]:
    """
    创建页面实例（Class 级别）
    同一测试类共享页面
    """
    page = class_context.new_page()
    
    yield page
    
    page.close()


# ===========================
# 页面对象模式 Base Page
# ===========================

class BasePage:
    """
    页面对象基类
    提供常用的页面操作方法
    """
    
    def __init__(self, page: Page):
        self.page = page
    
    def open(self, url: str):
        """打开 URL"""
        self.page.goto(url)
    
    def get_title(self) -> str:
        """获取页面标题"""
        return self.page.title()
    
    def get_current_url(self) -> str:
        """获取当前 URL"""
        return self.page.url
    
    def take_screenshot(self, filename: str) -> str:
        """
        截图并保存
        保存到 reports/screenshots/ 目录
        """
        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent.parent
        screenshot_dir = project_root / "reports" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = screenshot_dir / filename
        self.page.screenshot(path=str(filepath))
        return str(filepath)


@pytest.fixture
def base_page(page: Page) -> BasePage:
    """
    提供 BasePage 实例
    """
    return BasePage(page)


# ===========================
# 测试数据 Fixtures
# ===========================

@pytest.fixture
def test_user():
    """
    提供测试用户数据
    """
    return {
        "username": "testuser",
        "password": "Test123456",
        "email": "testuser@example.com"
    }


# ===========================
# Pytest Hooks
# ===========================

def pytest_configure(config):
    """
    Pytest 配置钩子
    """
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试用例"
    )
    config.addinivalue_line(
        "markers", "regression: 回归测试用例"
    )
    config.addinivalue_line(
        "markers", "slow: 运行较慢的测试用例"
    )


def pytest_collection_modifyitems(items):
    """
    修改测试用例集合
    解决中文测试名称显示问题
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试失败时自动截图
    """
    outcome = yield
    report = outcome.get_result()
    
    # 只在测试执行阶段（call）失败时截图
    if report.when == "call" and report.failed:
        # 获取 page fixture
        if "page" in item.fixturenames:
            page = item.funcargs.get("page")
        elif "class_page" in item.fixturenames:
            page = item.funcargs.get("class_page")
        else:
            return
        
        # 截图
        if page:
            try:
                # 获取项目根目录
                project_root = Path(__file__).parent.parent.parent.parent
                screenshot_dir = project_root / "reports" / "screenshots"
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                
                # 生成截图文件名
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                test_name = item.name.replace("/", "_").replace("::", "_")
                filename = f"FAILED_{test_name}_{timestamp}.png"
                filepath = screenshot_dir / filename
                
                # 保存截图
                page.screenshot(path=str(filepath))
                
                # 附加到 Allure 报告
                try:
                    import allure
                    allure.attach.file(
                        str(filepath),
                        name="失败截图",
                        attachment_type=allure.attachment_type.PNG
                    )
                except ImportError:
                    pass
                
            except Exception as e:
                print(f"截图失败: {e}")

