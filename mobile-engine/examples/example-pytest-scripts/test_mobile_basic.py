"""
Mobile Engine 基础测试示例
演示如何使用原生 pytest 编写移动端测试
"""
import allure
import pytest


@allure.feature("应用管理")
@allure.story("启动应用")
def test_open_app(mobile_keywords_no_driver):
    """测试启动应用"""
    with allure.step("启动应用"):
        mobile_keywords_no_driver.open_app(
            关键字="open_app",
            platform="android",
            server="http://127.0.0.1:4723",
            app_package="com.android.settings",
            app_activity=".Settings"
        )
    
    with allure.step("等待应用启动"):
        mobile_keywords_no_driver.sleep(关键字="sleep", 时间=2)
    
    with allure.step("关闭应用"):
        mobile_keywords_no_driver.close_app(关键字="close_app")


@allure.feature("元素操作")
@allure.story("点击元素")
def test_click_element(mobile_keywords, driver):
    """测试点击元素"""
    with allure.step("点击设置项"):
        mobile_keywords.click_element(
            关键字="click_element",
            定位方式="xpath",
            元素="//android.widget.TextView[@text='显示']"
        )


@allure.feature("元素操作")
@allure.story("输入文本")
def test_input_text(mobile_keywords, driver):
    """测试输入文本"""
    with allure.step("点击搜索框"):
        mobile_keywords.click_element(
            关键字="click_element",
            定位方式="id",
            元素="com.android.settings:id/search_action_bar"
        )
    
    with allure.step("输入搜索内容"):
        mobile_keywords.input_text(
            关键字="input_text",
            定位方式="id",
            元素="android:id/search_src_text",
            文本="WIFI"
        )


@allure.feature("手势操作")
@allure.story("滑动屏幕")
def test_swipe(mobile_keywords, driver):
    """测试滑动屏幕"""
    with allure.step("向上滑动"):
        mobile_keywords.swipe(
            关键字="swipe",
            方向="up",
            持续时间=500
        )
    
    with allure.step("等待动画"):
        mobile_keywords.sleep(关键字="sleep", 时间=1)
    
    with allure.step("向下滑动"):
        mobile_keywords.swipe(
            关键字="swipe",
            方向="down",
            持续时间=500
        )


@allure.feature("断言操作")
@allure.story("元素存在断言")
def test_assert_element_exists(mobile_keywords, driver):
    """测试断言元素存在"""
    with allure.step("断言标题存在"):
        mobile_keywords.assert_element_exists(
            关键字="assert_element_exists",
            定位方式="xpath",
            元素="//android.widget.TextView[@text='设置']"
        )


@pytest.mark.smoke
@allure.severity(allure.severity_level.CRITICAL)
def test_smoke_mobile(mobile_keywords_no_driver):
    """冒烟测试 - 验证应用基本可用性"""
    with allure.step("启动设置应用"):
        mobile_keywords_no_driver.open_app(
            关键字="open_app",
            platform="android",
            app_package="com.android.settings",
            app_activity=".Settings"
        )
    
    with allure.step("验证应用已启动"):
        mobile_keywords_no_driver.sleep(关键字="sleep", 时间=2)
    
    with allure.step("截图"):
        mobile_keywords_no_driver.take_screenshot(
            关键字="take_screenshot",
            filename="smoke_test"
        )
    
    with allure.step("关闭应用"):
        mobile_keywords_no_driver.close_app(关键字="close_app")


@pytest.mark.android
@allure.feature("设备操作")
def test_device_info(mobile_keywords, driver):
    """测试获取设备信息"""
    with allure.step("获取设备信息"):
        # 直接使用 driver 获取设备信息
        device_info = {
            "platform": driver.capabilities.get("platformName"),
            "device": driver.capabilities.get("deviceName"),
            "version": driver.capabilities.get("platformVersion")
        }
        allure.attach(
            str(device_info),
            name="设备信息",
            attachment_type=allure.attachment_type.TEXT
        )
