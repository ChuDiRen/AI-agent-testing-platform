"""
Mobile Engine Pytest 配置文件
提供测试 fixtures 和配置
"""
import allure
import pytest
from mobilerun.core.globalContext import g_context
from mobilerun.extend.keywords import Keywords
from mobilerun.utils.AppiumManager import AppiumManager


@pytest.fixture(scope="function")
def driver(request):
    """
    自动管理 Appium driver 生命周期
    
    用法:
        def test_example(driver):
            # driver 会自动创建和销毁
    """
    # 从命令行获取参数
    platform = request.config.getoption("--platform", default="android")
    server = request.config.getoption("--appium-server", default="http://127.0.0.1:4723")
    device_name = request.config.getoption("--device-name", default=None)
    app_package = request.config.getoption("--app-package", default=None)
    app_activity = request.config.getoption("--app-activity", default=None)
    
    # 构建 capabilities
    caps = {
        "platformName": platform.capitalize(),
        "automationName": "UiAutomator2" if platform.lower() == "android" else "XCUITest",
    }
    
    if device_name:
        caps["deviceName"] = device_name
    if app_package:
        caps["appPackage"] = app_package
    if app_activity:
        caps["appActivity"] = app_activity
    
    # 存储配置到全局上下文
    g_context().set_dict("platform", platform)
    g_context().set_dict("appium_server", server)
    
    # 创建 driver
    drv = AppiumManager.create_driver(server_url=server, caps=caps)
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
    
    # 关闭 Appium session
    try:
        AppiumManager.quit()
    except Exception as e:
        print(f"关闭 Appium session 失败: {e}")
    finally:
        g_context().set_dict("current_driver", None)


@pytest.fixture(scope="function")
def mobile_keywords(driver):
    """
    提供 Mobile 关键字实例
    
    用法:
        def test_example(mobile_keywords, driver):
            mobile_keywords.click_element(定位方式="id", 元素="button")
    """
    keywords = Keywords()
    yield keywords


@pytest.fixture(scope="function")
def mobile_keywords_no_driver():
    """
    提供 Mobile 关键字实例（不自动创建 driver）
    适用于手动管理 driver 的场景
    
    用法:
        def test_example(mobile_keywords_no_driver):
            mobile_keywords_no_driver.open_app(platform="android", ...)
    """
    keywords = Keywords()
    yield keywords
    # 清理
    try:
        AppiumManager.quit()
    except Exception:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    获取测试结果，用于失败截图
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        help="移动平台: android/ios"
    )
    parser.addoption(
        "--appium-server",
        action="store",
        default="http://127.0.0.1:4723",
        help="Appium 服务器地址"
    )
    parser.addoption(
        "--device-name",
        action="store",
        default=None,
        help="设备名称"
    )
    parser.addoption(
        "--app-package",
        action="store",
        default=None,
        help="Android 应用包名"
    )
    parser.addoption(
        "--app-activity",
        action="store",
        default=None,
        help="Android 应用入口 Activity"
    )


def pytest_configure(config):
    """Pytest 配置钩子"""
    # 注册自定义标记
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "regression: 回归测试")
    config.addinivalue_line("markers", "mobile: 移动端测试")
    config.addinivalue_line("markers", "android: Android 测试")
    config.addinivalue_line("markers", "ios: iOS 测试")
