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
        web_keywords.assert_title_contains(期望text="百度")
    
    with allure.step("输入搜索关键词"):
        web_keywords.input_text(locator_type="id", element="kw", text="Selenium WebDriver")
    
    with allure.step("点击搜索按钮"):
        web_keywords.click_element(locator_type="id", element="su")
    
    with allure.step("等待搜索结果加载"):
        web_keywords.wait_for_element_visible(
            locator_type="id",
            element="content_left",
            timeout=10
        )
    
    with allure.step("验证搜索结果包含关键词"):
        web_keywords.assert_text_contains(
            locator_type="id",
            element="content_left",
            期望text="Selenium"
        )
    
    with allure.step("截图保存"):
        web_keywords.take_screenshot(filename="baidu_search_result")


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
            locator_type="id",
            element="my-text-id",
            text="Test Input Text"
        )
    
    with allure.step("输入密码"):
        web_keywords.input_text(
            locator_type="name",
            element="my-password",
            text="secret123"
        )
    
    with allure.step("输入文本域"):
        web_keywords.input_text(
            locator_type="name",
            element="my-textarea",
            text="This is a test textarea"
        )
    
    with allure.step("点击提交按钮"):
        web_keywords.click_element(
            locator_type="xpath",
            element="//button[@type='submit']"
        )


@allure.feature("等待操作")
@allure.story("元素等待")
def test_wait_operations(web_keywords, driver):
    """测试元素等待操作"""
    with allure.step("打开百度"):
        web_keywords.navigate_to(url="https://www.baidu.com")
    
    with allure.step("等待搜索框出现"):
        web_keywords.wait_for_element(
            locator_type="id",
            element="kw",
            timeout=10
        )
    
    with allure.step("等待搜索框可见"):
        web_keywords.wait_for_element_visible(
            locator_type="id",
            element="kw",
            timeout=10
        )
    
    with allure.step("等待搜索框可点击"):
        web_keywords.wait_for_element_clickable(
            locator_type="id",
            element="kw",
            timeout=10
        )


@pytest.mark.smoke
@allure.severity(allure.severity_level.CRITICAL)
def test_smoke_web(web_keywords, driver):
    """冒烟测试 - 验证网站基本可访问"""
    with allure.step("打开网站首页"):
        web_keywords.navigate_to(url="https://www.baidu.com")
    
    with allure.step("验证页面标题"):
        web_keywords.assert_title_contains(期望text="百度")
    
    with allure.step("验证搜索框可见"):
        web_keywords.assert_element_visible(locator_type="id", element="kw")


