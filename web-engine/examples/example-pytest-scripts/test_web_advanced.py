"""
Web Engine 高级测试示例
演示 pytest 高级特性：参数化、测试类、fixture 等
"""
import allure
import pytest


# ==================== 参数化测试 ====================
@pytest.mark.parametrize("search_word,expected_text", [
    ("Python", "Python"),
    ("Java", "Java"),
    ("Selenium", "Selenium"),
])
@allure.feature("参数化测试")
@allure.story("搜索数据驱动")
def test_search_ddt(web_keywords, driver, search_word, expected_text):
    """数据驱动搜索测试"""
    with allure.step(f"搜索关键词: {search_word}"):
        web_keywords.navigate_to(url="https://www.baidu.com")
        web_keywords.input_text(定位方式="id", 元素="kw", 文本=search_word)
        web_keywords.click_element(定位方式="id", 元素="su")
        web_keywords.wait_for_element_visible(
            定位方式="id",
            元素="content_left",
            超时时间=10
        )
        web_keywords.assert_text_contains(
            定位方式="id",
            元素="content_left",
            期望文本=expected_text
        )


# ==================== 测试类 ====================
class TestWebForm:
    """Web 表单测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, web_keywords, driver):
        """每个测试前的准备"""
        self.kw = web_keywords
        self.driver = driver
        with allure.step("打开测试页面"):
            self.kw.navigate_to(
                url="https://www.selenium.dev/selenium/web/web-form.html"
            )
        yield
        # teardown 代码
        with allure.step("测试清理"):
            pass
    
    @allure.story("文本输入")
    def test_input_text(self):
        """测试文本输入"""
        with allure.step("输入文本"):
            self.kw.input_text(
                定位方式="id",
                元素="my-text-id",
                文本="Hello World"
            )
    
    @allure.story("下拉框选择")
    def test_select_dropdown(self):
        """测试下拉框选择"""
        with allure.step("选择下拉框选项"):
            self.kw.select_dropdown(
                定位方式="name",
                元素="my-select",
                选择方式="value",
                选项值="2"
            )
    
    @allure.story("表单提交")
    def test_submit_form(self):
        """测试表单提交"""
        with allure.step("填写表单"):
            self.kw.input_text(
                定位方式="id",
                元素="my-text-id",
                文本="Test User"
            )
        
        with allure.step("提交表单"):
            self.kw.click_element(
                定位方式="xpath",
                元素="//button[@type='submit']"
            )
        
        with allure.step("等待提交成功"):
            self.kw.wait_for_element_visible(
                定位方式="id",
                元素="message",
                超时时间=5
            )


# ==================== Fixture 示例 ====================
@pytest.fixture
def open_baidu(web_keywords, driver):
    """打开百度首页的 fixture"""
    with allure.step("打开百度首页"):
        web_keywords.navigate_to(url="https://www.baidu.com")
    yield
    # 清理工作
    with allure.step("关闭页面"):
        pass


@allure.feature("Fixture 测试")
@allure.story("使用自定义 Fixture")
def test_with_custom_fixture(web_keywords, driver, open_baidu):
    """使用自定义 fixture 的测试"""
    with allure.step("验证页面已打开"):
        web_keywords.assert_title_contains(期望文本="百度")


# ==================== 浏览器操作 ====================
@allure.feature("浏览器操作")
@allure.story("页面导航")
class TestBrowserOperations:
    """浏览器操作测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, web_keywords, driver):
        """测试准备"""
        self.kw = web_keywords
        self.driver = driver
    
    def test_navigation(self):
        """测试页面导航"""
        with allure.step("打开百度"):
            self.kw.navigate_to(url="https://www.baidu.com")
        
        with allure.step("打开新闻页"):
            self.kw.navigate_to(url="https://news.baidu.com")
        
        with allure.step("后退"):
            self.kw.back()
        
        with allure.step("前进"):
            self.kw.forward()
        
        with allure.step("刷新页面"):
            self.kw.refresh_page()
    
    def test_get_elements_info(self):
        """测试获取元素信息"""
        with allure.step("打开测试页面"):
            self.kw.navigate_to(
                url="https://www.selenium.dev/selenium/web/web-form.html"
            )
        
        with allure.step("获取文本"):
            text = self.kw.get_text(
                定位方式="xpath",
                元素="//h1",
                变量名="page_title"
            )
            print(f"获取到的文本: {text}")


# ==================== 高级操作 ====================
@allure.feature("高级操作")
@allure.story("JavaScript 执行")
def test_execute_javascript(web_keywords, driver):
    """测试 JavaScript 执行"""
    with allure.step("打开页面"):
        web_keywords.navigate_to(url="https://www.baidu.com")
    
    with allure.step("执行 JavaScript 获取标题"):
        web_keywords.execute_script(
            脚本="return document.title;",
            变量名="page_title"
        )
    
    with allure.step("执行 JavaScript 滚动"):
        web_keywords.execute_script(
            脚本="window.scrollTo(0, document.body.scrollHeight);"
        )


@allure.feature("高级操作")
@allure.story("元素滚动和悬停")
def test_scroll_and_hover(web_keywords, driver):
    """测试滚动和悬停操作"""
    with allure.step("打开百度"):
        web_keywords.navigate_to(url="https://www.baidu.com")
    
    with allure.step("滚动到页面底部"):
        web_keywords.execute_script(
            脚本="window.scrollTo(0, document.body.scrollHeight);"
        )
    
    with allure.step("等待1秒"):
        web_keywords.sleep(时间=1)
    
    with allure.step("鼠标悬停搜索框"):
        web_keywords.hover_element(定位方式="id", 元素="kw")


# ==================== 标记示例 ====================
@pytest.mark.smoke
@allure.severity(allure.severity_level.BLOCKER)
def test_critical_page(web_keywords, driver):
    """关键页面测试"""
    with allure.step("验证关键页面可访问"):
        web_keywords.navigate_to(url="https://www.baidu.com")
        web_keywords.assert_title_contains(期望文本="百度")


@pytest.mark.regression
@allure.severity(allure.severity_level.NORMAL)
def test_regression_case(web_keywords, driver):
    """回归测试用例"""
    with allure.step("执行回归测试"):
        web_keywords.navigate_to(url="https://www.baidu.com")
        web_keywords.assert_element_visible(定位方式="id", 元素="kw")


# ==================== 跳过测试 ====================
@pytest.mark.skip(reason="此功能暂未实现")
def test_not_implemented(web_keywords, driver):
    """尚未实现的测试"""
    pass


@pytest.mark.skipif(True, reason="条件跳过示例")
def test_conditional_skip(web_keywords, driver):
    """条件跳过的测试"""
    pass


# ==================== 预期失败 ====================
@pytest.mark.xfail(reason="已知 UI 缺陷")
def test_known_ui_issue(web_keywords, driver):
    """已知问题的测试"""
    web_keywords.navigate_to(url="https://www.example.com/broken-page")
    web_keywords.assert_element_visible(定位方式="id", 元素="non-existent")

