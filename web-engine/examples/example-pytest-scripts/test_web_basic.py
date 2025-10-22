"""
Web Engine 基础测试示例
演示如何使用原生 pytest 编写 Web UI 测试
"""
import allure
import pytest


@allure.feature("搜索功能")
@allure.story("百度搜索")
def test_baidu_search(web_keywords, driver):
    """测试百度搜索功能"""
    with allure.step("打开百度首页"):
        web_keywords.navigate_to(url="https://www.baidu.com")
    
    with allure.step("断言页面标题"):
        web_keywords.assert_title_contains(期望文本="百度")
    
    with allure.step("输入搜索关键词"):
        web_keywords.input_text(定位方式="id", 元素="kw", 文本="Selenium WebDriver")
    
    with allure.step("点击搜索按钮"):
        web_keywords.click_element(定位方式="id", 元素="su")
    
    with allure.step("等待搜索结果加载"):
        web_keywords.wait_for_element_visible(
            定位方式="id",
            元素="content_left",
            超时时间=10
        )
    
    with allure.step("验证搜索结果包含关键词"):
        web_keywords.assert_text_contains(
            定位方式="id",
            元素="content_left",
            期望文本="Selenium"
        )
    
    with allure.step("截图保存"):
        web_keywords.take_screenshot(文件名="baidu_search_result")


@allure.feature("表单操作")
@allure.story("元素基本操作")
def test_element_operations(web_keywords, driver):
    """测试元素基本操作"""
    with allure.step("打开测试页面"):
        web_keywords.navigate_to(
            url="https://www.selenium.dev/selenium/web/web-form.html"
        )
    
    with allure.step("输入文本"):
        web_keywords.input_text(
            定位方式="id",
            元素="my-text-id",
            文本="Test Input Text"
        )
    
    with allure.step("输入密码"):
        web_keywords.input_text(
            定位方式="name",
            元素="my-password",
            文本="secret123"
        )
    
    with allure.step("输入文本域"):
        web_keywords.input_text(
            定位方式="name",
            元素="my-textarea",
            文本="This is a test textarea"
        )
    
    with allure.step("点击提交按钮"):
        web_keywords.click_element(
            定位方式="xpath",
            元素="//button[@type='submit']"
        )


@allure.feature("等待操作")
@allure.story("元素等待")
def test_wait_operations(web_keywords, driver):
    """测试元素等待操作"""
    with allure.step("打开百度"):
        web_keywords.navigate_to(url="https://www.baidu.com")
    
    with allure.step("等待搜索框出现"):
        web_keywords.wait_for_element(
            定位方式="id",
            元素="kw",
            超时时间=10
        )
    
    with allure.step("等待搜索框可见"):
        web_keywords.wait_for_element_visible(
            定位方式="id",
            元素="kw",
            超时时间=10
        )
    
    with allure.step("等待搜索框可点击"):
        web_keywords.wait_for_element_clickable(
            定位方式="id",
            元素="kw",
            超时时间=10
        )


@pytest.mark.smoke
@allure.severity(allure.severity_level.CRITICAL)
def test_smoke_web(web_keywords, driver):
    """冒烟测试 - 验证网站基本可访问"""
    with allure.step("打开网站首页"):
        web_keywords.navigate_to(url="https://www.baidu.com")
    
    with allure.step("验证页面标题"):
        web_keywords.assert_title_contains(期望文本="百度")
    
    with allure.step("验证搜索框可见"):
        web_keywords.assert_element_visible(定位方式="id", 元素="kw")

