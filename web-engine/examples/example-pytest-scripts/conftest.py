"""
Web Engine Pytest 配置文件
提供测试 fixtures 和配置
"""
import allure
import pytest
from webrun.core.globalContext import g_context
from webrun.extend.keywords import Keywords
from webrun.utils.DriverManager import DriverManager


@pytest.fixture(scope="function")
def driver(request):
    """
    自动管理浏览器生命周期
    
    用法:
        def test_example(driver):
            # driver 会自动创建和销毁
    """
    # 从命令行获取参数
    browser = request.config.getoption("--browser", default="chrome")
    headless = request.config.getoption("--headless", default="false")
    
    # 创建浏览器实例
    drv = DriverManager.create_driver(
        browser=browser,
        headless=headless.lower() in ["true", "1", "yes"]
    )
    
    # 存储到全局上下文（供 Keywords 使用）
    g_context().set_dict("current_driver", drv)
    
    yield drv
    
    # 测试结束后处理
    # 如果测试失败，自动截图
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        try:
            screenshot = drv.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name="失败截图",
                attachment_type=allure.attachment_type.PNG
            )
        except Exception as e:
            print(f"截图失败: {e}")
    
    # 关闭浏览器
    try:
        drv.quit()
    except Exception as e:
        print(f"关闭浏览器失败: {e}")
    finally:
        g_context().set_dict("current_driver", None)


@pytest.fixture(scope="function")
def web_keywords(driver):
    """
    提供 Web 关键字实例
    
    用法:
        def test_example(web_keywords, driver):
            web_keywords.navigate_to(url="https://example.com")
            web_keywords.click_element(定位方式="id", 元素="btn")
    """
    keywords = Keywords()
    yield keywords


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    获取测试结果，用于失败截图
    这个 hook 会在测试的各个阶段被调用
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="浏览器类型: chrome/firefox/edge"
    )
    parser.addoption(
        "--headless",
        action="store",
        default="false",
        help="是否无头模式: true/false"
    )


def pytest_configure(config):
    """Pytest 配置钩子"""
    # 注册自定义标记
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "regression: 回归测试")
    config.addinivalue_line("markers", "ui: UI 测试")
    config.addinivalue_line("markers", "web: Web 测试")

