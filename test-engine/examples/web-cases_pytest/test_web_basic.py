"""
Web 基础测试示例（使用 Playwright）
演示基本的 Web UI 自动化测试用例编写方法
"""
import allure
import pytest
from playwright.sync_api import Page, expect


@allure.feature("搜索功能")
@allure.story("百度搜索")
class TestBaiduSearch:
    """百度搜索测试"""
    
    @allure.title("测试百度首页加载")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_baidu_homepage(self, page: Page, base_url: str):
        """
        测试用例：验证百度首页正常加载
        
        步骤：
        1. 打开百度首页
        2. 验证页面标题
        3. 验证搜索框存在
        """
        with allure.step("步骤1: 打开百度首页"):
            page.goto(base_url)
            allure.attach(page.url, "当前URL", allure.attachment_type.TEXT)
        
        with allure.step("步骤2: 验证页面标题"):
            title = page.title()
            allure.attach(title, "页面标题", allure.attachment_type.TEXT)
            assert "百度" in title, f"页面标题错误: {title}"
        
        with allure.step("步骤3: 验证搜索框存在"):
            search_box = page.locator("#kw")
            # 等待元素存在即可（百度可能有特殊的visibility设置）
            expect(search_box).to_be_attached()
    
    @allure.title("测试百度搜索功能")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_baidu_search_function(self, page: Page, base_url: str):
        """
        测试用例：验证百度搜索功能
        
        步骤：
        1. 打开百度首页
        2. 输入搜索关键词
        3. 点击搜索按钮
        4. 验证搜索结果
        """
        with allure.step("步骤1: 打开百度首页"):
            page.goto(base_url)
        
        with allure.step("步骤2: 输入搜索关键词"):
            search_keyword = "Playwright 自动化测试"
            page.locator("#kw").fill(search_keyword)
            allure.attach(search_keyword, "搜索关键词", allure.attachment_type.TEXT)
        
        with allure.step("步骤3: 点击搜索按钮"):
            page.locator("#su").click()
        
        with allure.step("步骤4: 验证搜索结果"):
            # 等待搜索结果加载
            page.wait_for_selector("#content_left", timeout=10000)
            
            # 验证结果页面包含关键词
            content = page.content()
            assert "Playwright" in content or "自动化" in content, "搜索结果中未找到相关内容"
            
            # 截图
            screenshot = page.screenshot()
            allure.attach(
                screenshot,
                "搜索结果页面",
                allure.attachment_type.PNG
            )
    
    @allure.title("测试多关键词搜索-{keyword}")
    @pytest.mark.parametrize("keyword", [
        "Python",
        "Playwright",
        "自动化测试框架",
    ])
    def test_search_multiple_keywords(
        self, 
        page: Page, 
        base_url: str, 
        keyword: str
    ):
        """
        测试用例：测试多个关键词搜索
        使用参数化测试
        """
        with allure.step(f"搜索关键词: {keyword}"):
            # 打开百度首页
            page.goto(base_url)
            
            # 输入关键词
            page.locator("#kw").fill(keyword)
            
            # 点击搜索
            page.locator("#su").click()
            
            # 等待结果
            page.wait_for_selector("#content_left", timeout=10000)
            
            # 验证结果页URL包含搜索参数
            current_url = page.url
            allure.attach(current_url, "搜索结果URL", allure.attachment_type.TEXT)
            
            # 至少验证页面加载成功
            assert "baidu.com" in current_url, "搜索失败"


@allure.feature("表单操作")
@allure.story("表单填写和提交")
class TestFormOperations:
    """表单操作测试"""
    
    @allure.title("测试输入框操作")
    @allure.severity(allure.severity_level.NORMAL)
    def test_input_operations(self, page: Page, base_url: str):
        """
        测试用例：测试输入框的各种操作
        """
        with allure.step("打开测试页面"):
            page.goto(base_url)
        
        with allure.step("测试输入文本"):
            search_box = page.locator("#kw")
            search_box.fill("Test Input")
            
            # 验证输入值
            input_value = search_box.input_value()
            assert input_value == "Test Input", f"输入值不正确: {input_value}"
        
        with allure.step("测试清空输入框"):
            search_box.fill("")
            input_value = search_box.input_value()
            assert input_value == "", "清空失败"
        
        with allure.step("测试追加文本"):
            search_box.type("First ")
            search_box.type("Second")
            input_value = search_box.input_value()
            assert input_value == "First Second", "追加文本失败"


@allure.feature("元素定位")
@allure.story("多种定位方式")
class TestElementLocators:
    """元素定位方式测试"""
    
    @allure.title("测试多种元素定位方式")
    @allure.severity(allure.severity_level.NORMAL)
    def test_various_locators(self, page: Page, base_url: str):
        """
        测试用例：演示多种元素定位方式
        """
        page.goto(base_url)
        
        with allure.step("通过 ID 定位"):
            element = page.locator("#kw")
            expect(element).to_be_visible()
            allure.attach("ID: kw", "定位器", allure.attachment_type.TEXT)
        
        with allure.step("通过 CSS Selector 定位"):
            element = page.locator("css=#kw")
            expect(element).to_be_visible()
            allure.attach("CSS: #kw", "定位器", allure.attachment_type.TEXT)
        
        with allure.step("通过 XPath 定位"):
            element = page.locator("xpath=//input[@id='kw']")
            expect(element).to_be_visible()
            allure.attach("XPath: //input[@id='kw']", "定位器", allure.attachment_type.TEXT)
        
        with allure.step("通过文本定位"):
            # 查找包含"新闻"的链接
            element = page.get_by_text("新闻", exact=False)
            if element.count() > 0:
                allure.attach("找到包含'新闻'的元素", "文本定位", allure.attachment_type.TEXT)


@allure.feature("等待机制")
@allure.story("自动等待")
class TestWaitMechanisms:
    """等待机制测试"""
    
    @allure.title("测试自动等待-元素可见")
    @allure.severity(allure.severity_level.NORMAL)
    def test_auto_wait_visible(self, page: Page, base_url: str):
        """
        测试用例：测试 Playwright 自动等待元素可见
        Playwright 自动等待元素可操作
        """
        with allure.step("打开页面"):
            page.goto(base_url)
        
        with allure.step("验证元素自动等待"):
            # Playwright 自动等待元素可见
            element = page.locator("#kw")
            expect(element).to_be_visible()
            allure.attach("元素已可见", "等待结果", allure.attachment_type.TEXT)
    
    @allure.title("测试自动等待-元素可点击")
    @allure.severity(allure.severity_level.NORMAL)
    def test_auto_wait_clickable(self, page: Page, base_url: str):
        """
        测试用例：测试 Playwright 自动等待元素可点击
        """
        with allure.step("打开页面"):
            page.goto(base_url)
        
        with allure.step("验证元素可点击"):
            # Playwright 自动等待元素可点击
            element = page.locator("#su")
            expect(element).to_be_enabled()
            allure.attach("元素可点击", "等待结果", allure.attachment_type.TEXT)


@allure.feature("页面导航")
@allure.story("浏览器导航操作")
class TestPageNavigation:
    """页面导航测试"""
    
    @allure.title("测试浏览器前进后退")
    @allure.severity(allure.severity_level.MINOR)
    def test_browser_navigation(self, page: Page, base_url: str):
        """
        测试用例：测试浏览器前进后退功能
        """
        with allure.step("访问百度首页"):
            page.goto(base_url)
            url1 = page.url
            allure.attach(url1, "首页URL", allure.attachment_type.TEXT)
        
        with allure.step("执行搜索进入结果页"):
            page.locator("#kw").fill("测试")
            page.locator("#su").click()
            
            # 等待页面跳转
            page.wait_for_url("**/*", timeout=10000)
            url2 = page.url
            allure.attach(url2, "搜索结果URL", allure.attachment_type.TEXT)
        
        with allure.step("后退到首页"):
            page.go_back()
            page.wait_for_load_state("networkidle")
            assert "baidu.com" in page.url, "后退失败"
        
        with allure.step("前进到搜索结果页"):
            page.go_forward()
            page.wait_for_load_state("networkidle")
            # 验证回到搜索结果页
            assert "baidu.com" in page.url, "前进失败"
    
    @allure.title("测试页面刷新")
    @allure.severity(allure.severity_level.MINOR)
    def test_page_refresh(self, page: Page, base_url: str):
        """
        测试用例：测试页面刷新功能
        """
        with allure.step("打开页面"):
            page.goto(base_url)
            original_title = page.title()
        
        with allure.step("刷新页面"):
            page.reload()
            page.wait_for_load_state("networkidle")
        
        with allure.step("验证页面刷新成功"):
            new_title = page.title()
            assert new_title == original_title, "页面标题改变，刷新可能失败"
            allure.attach(new_title, "刷新后标题", allure.attachment_type.TEXT)

