"""
Mobile Engine 高级测试示例
演示 pytest 高级特性：参数化、测试类、fixture 等
"""
import allure
import pytest


@pytest.mark.parametrize("setting_name,expected_text", [
    ("显示", "显示"),
    ("声音", "声音"),
    ("存储", "存储"),
])
@allure.feature("设置导航")
def test_navigate_settings(mobile_keywords, driver, setting_name, expected_text):
    """参数化测试 - 导航到不同设置项"""
    with allure.step(f"点击 {setting_name}"):
        mobile_keywords.click_element(
            关键字="click_element",
            定位方式="xpath",
            元素=f"//android.widget.TextView[@text='{setting_name}']"
        )
    
    with allure.step("验证页面标题"):
        mobile_keywords.assert_text_contains(
            关键字="assert_text_contains",
            定位方式="xpath",
            元素="//android.widget.TextView[@resource-id='android:id/title']",
            期望文本=expected_text
        )
    
    with allure.step("返回"):
        mobile_keywords.press_back(关键字="press_back")


@allure.feature("搜索功能")
class TestSearchFeature:
    """搜索功能测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_search(self, mobile_keywords, driver):
        """每个测试前打开搜索"""
        with allure.step("打开搜索"):
            mobile_keywords.click_element(
                关键字="click_element",
                定位方式="id",
                元素="com.android.settings:id/search_action_bar"
            )
        yield
        with allure.step("清理搜索"):
            mobile_keywords.press_back(关键字="press_back")
    
    def test_search_wifi(self, mobile_keywords, driver):
        """搜索 WIFI"""
        with allure.step("输入搜索词"):
            mobile_keywords.input_text(
                关键字="input_text",
                定位方式="id",
                元素="android:id/search_src_text",
                文本="WIFI"
            )
        
        with allure.step("验证搜索结果"):
            mobile_keywords.sleep(关键字="sleep", 时间=1)
    
    def test_search_bluetooth(self, mobile_keywords, driver):
        """搜索蓝牙"""
        with allure.step("输入搜索词"):
            mobile_keywords.input_text(
                关键字="input_text",
                定位方式="id",
                元素="android:id/search_src_text",
                文本="蓝牙"
            )
        
        with allure.step("验证搜索结果"):
            mobile_keywords.sleep(关键字="sleep", 时间=1)


@allure.feature("滑动操作")
class TestSwipeOperations:
    """滑动操作测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_swipe(self, mobile_keywords, driver):
        """测试前准备"""
        yield
    
    @pytest.mark.parametrize("direction", ["up", "down", "left", "right"])
    def test_swipe_directions(self, mobile_keywords, driver, direction):
        """测试不同方向滑动"""
        with allure.step(f"向 {direction} 滑动"):
            mobile_keywords.swipe(
                关键字="swipe",
                方向=direction,
                持续时间=500
            )
        
        with allure.step("等待动画"):
            mobile_keywords.sleep(关键字="sleep", 时间=0.5)


@pytest.fixture
def app_context():
    """提供应用上下文数据"""
    return {
        "package": "com.android.settings",
        "activity": ".Settings",
        "timeout": 10
    }


@allure.feature("应用生命周期")
def test_app_lifecycle(mobile_keywords_no_driver, app_context):
    """测试应用生命周期管理"""
    with allure.step("启动应用"):
        mobile_keywords_no_driver.open_app(
            关键字="open_app",
            platform="android",
            app_package=app_context["package"],
            app_activity=app_context["activity"]
        )
    
    with allure.step("等待应用加载"):
        mobile_keywords_no_driver.sleep(关键字="sleep", 时间=2)
    
    with allure.step("切换到后台"):
        mobile_keywords_no_driver.background_app(
            关键字="background_app",
            秒数=2
        )
    
    with allure.step("验证应用恢复"):
        mobile_keywords_no_driver.sleep(关键字="sleep", 时间=1)
    
    with allure.step("关闭应用"):
        mobile_keywords_no_driver.close_app(关键字="close_app")


@pytest.mark.smoke
@allure.severity(allure.severity_level.CRITICAL)
def test_critical_flow(mobile_keywords_no_driver):
    """关键流程测试"""
    with allure.step("启动应用"):
        mobile_keywords_no_driver.open_app(
            关键字="open_app",
            platform="android",
            app_package="com.android.settings",
            app_activity=".Settings"
        )
    
    with allure.step("执行关键操作"):
        mobile_keywords_no_driver.sleep(关键字="sleep", 时间=2)
    
    with allure.step("关闭应用"):
        mobile_keywords_no_driver.close_app(关键字="close_app")


@pytest.mark.skip(reason="此测试需要特定设备")
def test_specific_device(mobile_keywords, driver):
    """需要特定设备的测试"""
    pass


@pytest.mark.skipif(True, reason="条件跳过示例")
def test_conditional_skip(mobile_keywords, driver):
    """条件跳过示例"""
    pass


@pytest.mark.xfail(reason="已知 UI 缺陷")
def test_known_issue(mobile_keywords, driver):
    """已知问题测试"""
    with allure.step("执行已知会失败的操作"):
        mobile_keywords.click_element(
            关键字="click_element",
            定位方式="id",
            元素="non_existent_element"
        )
