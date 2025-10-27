"""
Web 高级测试示例（使用 Playwright）
演示高级测试技巧和最佳实践
"""
import time

import allure
import pytest
from playwright.sync_api import Page, expect


@allure.feature("高级交互")
@allure.story("键盘操作")
class TestAdvancedInteractions:
    """高级交互操作测试"""
    
    @allure.title("测试键盘快捷键操作")
    @allure.severity(allure.severity_level.NORMAL)
    def test_keyboard_shortcuts(self, page: Page, base_url: str):
        """
        测试用例：测试键盘快捷键操作
        """
        with allure.step("打开百度首页"):
            page.goto(base_url)
        
        with allure.step("使用 Tab 键导航"):
            # 定位搜索框
            search_box = page.locator("#kw")
            search_box.fill("Playwright")
            
            # 按 Tab 键
            search_box.press("Tab")
            time.sleep(0.5)
            allure.attach("Tab键导航成功", "键盘操作", allure.attachment_type.TEXT)
        
        with allure.step("使用 Enter 键提交搜索"):
            search_box = page.locator("#kw")
            search_box.fill("Python 自动化")
            search_box.press("Enter")
            
            # 等待搜索结果
            page.wait_for_selector("#content_left", timeout=10000)
            allure.attach("搜索成功", "结果", allure.attachment_type.TEXT)
    
    @allure.title("测试组合键操作")
    @allure.severity(allure.severity_level.NORMAL)
    def test_key_combinations(self, page: Page, base_url: str):
        """
        测试用例：测试组合键操作（Ctrl+A）
        """
        with allure.step("打开页面并输入文本"):
            page.goto(base_url)
            search_box = page.locator("#kw")
            test_text = "测试文本内容"
            search_box.fill(test_text)
        
        with allure.step("使用 Ctrl+A 全选并删除"):
            search_box.press("Control+A")
            time.sleep(0.3)
            search_box.press("Delete")
            time.sleep(0.3)
            
            value = search_box.input_value()
            assert value == "", f"删除失败，当前值: {value}"


@allure.feature("窗口操作")
@allure.story("多窗口切换")
class TestWindowOperations:
    """窗口操作测试"""
    
    @allure.title("测试多窗口切换")
    @allure.severity(allure.severity_level.NORMAL)
    def test_multiple_windows(self, page: Page, base_url: str):
        """
        测试用例：测试多窗口切换
        """
        with allure.step("打开初始页面"):
            page.goto(base_url)
            original_title = page.title()
            allure.attach(original_title, "原始窗口标题", allure.attachment_type.TEXT)
        
        with allure.step("打开新窗口"):
            # 使用 page.context 打开新页面
            new_page = page.context.new_page()
            new_page.goto(base_url)
            time.sleep(1)
        
        with allure.step("获取所有页面"):
            all_pages = page.context.pages
            allure.attach(f"页面数量: {len(all_pages)}", "页面信息", allure.attachment_type.TEXT)
            assert len(all_pages) >= 2, "新页面未打开"
        
        with allure.step("切换到新页面并验证"):
            new_page_title = new_page.title()
            allure.attach(new_page_title, "新页面标题", allure.attachment_type.TEXT)
        
        with allure.step("关闭新页面"):
            new_page.close()
            # 验证原页面仍然存在
            assert page.title() == original_title, "原页面异常"
    
    @allure.title("测试获取窗口大小")
    @allure.severity(allure.severity_level.MINOR)
    def test_window_size(self, page: Page, base_url: str):
        """
        测试用例：测试窗口大小操作
        """
        page.goto(base_url)
        
        with allure.step("获取当前窗口大小"):
            viewport = page.viewport_size
            allure.attach(
                f"宽度: {viewport['width']}, 高度: {viewport['height']}",
                "窗口大小",
                allure.attachment_type.TEXT
            )
            assert viewport['width'] > 0 and viewport['height'] > 0, "窗口大小异常"
        
        with allure.step("设置窗口大小"):
            page.set_viewport_size({"width": 1280, "height": 720})
            time.sleep(0.5)
            new_viewport = page.viewport_size
            allure.attach(
                f"新宽度: {new_viewport['width']}, 新高度: {new_viewport['height']}",
                "调整后窗口大小",
                allure.attachment_type.TEXT
            )


@allure.feature("JavaScript交互")
@allure.story("执行JavaScript脚本")
class TestJavaScriptExecution:
    """JavaScript 执行测试"""
    
    @allure.title("测试执行JavaScript获取页面信息")
    @allure.severity(allure.severity_level.NORMAL)
    def test_execute_js_get_info(self, page: Page, base_url: str):
        """
        测试用例：执行 JavaScript 获取页面信息
        """
        with allure.step("打开页面"):
            page.goto(base_url)
        
        with allure.step("获取页面标题"):
            title = page.evaluate("() => document.title")
            allure.attach(title, "JS获取的标题", allure.attachment_type.TEXT)
            assert title == page.title(), "标题不一致"
        
        with allure.step("获取页面URL"):
            url = page.evaluate("() => window.location.href")
            allure.attach(url, "JS获取的URL", allure.attachment_type.TEXT)
            assert url == page.url, "URL不一致"
        
        with allure.step("获取页面高度"):
            height = page.evaluate("() => document.body.scrollHeight")
            allure.attach(str(height), "页面高度", allure.attachment_type.TEXT)
            assert height > 0, "页面高度异常"
    
    @allure.title("测试执行JavaScript操作元素")
    @allure.severity(allure.severity_level.NORMAL)
    def test_execute_js_manipulate_element(self, page: Page, base_url: str):
        """
        测试用例：使用 JavaScript 操作元素
        """
        with allure.step("打开页面"):
            page.goto(base_url)
        
        with allure.step("使用JS设置输入框值"):
            page.evaluate("""
                () => {
                    document.querySelector('#kw').value = 'JavaScript输入';
                }
            """)
            
            # 验证值设置成功
            value = page.locator("#kw").input_value()
            assert value == "JavaScript输入", f"JS设置值失败: {value}"
            allure.attach(value, "输入框值", allure.attachment_type.TEXT)
        
        with allure.step("使用JS点击按钮"):
            page.evaluate("() => document.querySelector('#su').click()")
            
            # 等待搜索结果
            page.wait_for_selector("#content_left", timeout=10000)
            allure.attach("点击成功", "结果", allure.attachment_type.TEXT)
    
    @allure.title("测试页面滚动")
    @allure.severity(allure.severity_level.NORMAL)
    def test_page_scrolling(self, page: Page, base_url: str):
        """
        测试用例：测试页面滚动
        """
        with allure.step("打开页面"):
            page.goto(base_url)
        
        with allure.step("获取初始滚动位置"):
            initial_scroll = page.evaluate("() => window.pageYOffset")
            allure.attach(str(initial_scroll), "初始滚动位置", allure.attachment_type.TEXT)
        
        with allure.step("滚动到页面底部"):
            page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            
            bottom_scroll = page.evaluate("() => window.pageYOffset")
            allure.attach(str(bottom_scroll), "底部滚动位置", allure.attachment_type.TEXT)
            assert bottom_scroll >= initial_scroll, "滚动失败"
        
        with allure.step("滚动到页面顶部"):
            page.evaluate("() => window.scrollTo(0, 0)")
            time.sleep(0.5)
            
            top_scroll = page.evaluate("() => window.pageYOffset")
            assert top_scroll == 0, "未滚动到顶部"


@allure.feature("截图和报告")
@allure.story("截图操作")
class TestScreenshotOperations:
    """截图操作测试"""
    
    @allure.title("测试页面截图")
    @allure.severity(allure.severity_level.MINOR)
    def test_take_screenshot(self, page: Page, base_url: str):
        """
        测试用例：测试页面截图功能
        """
        with allure.step("打开页面"):
            page.goto(base_url)
        
        with allure.step("截取整个页面"):
            screenshot_bytes = page.screenshot()
            allure.attach(
                screenshot_bytes,
                "页面截图",
                allure.attachment_type.PNG
            )
            assert screenshot_bytes is not None, "截图失败"
        
        with allure.step("保存截图到文件"):
            from pathlib import Path
            from datetime import datetime
            
            # 获取项目根目录
            project_root = Path(__file__).parent.parent.parent.parent
            screenshot_dir = project_root / "reports" / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_screenshot_{timestamp}.png"
            filepath = screenshot_dir / filename
            
            page.screenshot(path=str(filepath))
            assert filepath.exists(), "截图文件未保存"
            allure.attach(str(filepath), "截图路径", allure.attachment_type.TEXT)


@allure.feature("性能测试")
@allure.story("页面加载性能")
class TestPerformance:
    """性能测试"""
    
    @allure.title("测试页面加载时间")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    def test_page_load_time(self, page: Page, base_url: str):
        """
        测试用例：测试页面加载时间
        要求：页面加载时间 < 5 秒
        """
        with allure.step("记录开始时间并加载页面"):
            start_time = time.time()
            page.goto(base_url, wait_until="networkidle")
            end_time = time.time()
            
            load_time = end_time - start_time
            allure.attach(f"{load_time:.2f} 秒", "页面加载时间", allure.attachment_type.TEXT)
        
        with allure.step("验证加载时间"):
            assert load_time < 5.0, f"页面加载时间过长: {load_time:.2f}秒"
    
    @allure.title("测试使用Performance API获取性能数据")
    @allure.severity(allure.severity_level.NORMAL)
    def test_performance_metrics(self, page: Page, base_url: str):
        """
        测试用例：使用 Performance API 获取详细性能数据
        """
        with allure.step("加载页面"):
            page.goto(base_url, wait_until="networkidle")
        
        with allure.step("获取性能数据"):
            # 获取 Navigation Timing 数据
            timing = page.evaluate("""
                () => {
                    const timing = window.performance.timing;
                    return {
                        'dns': timing.domainLookupEnd - timing.domainLookupStart,
                        'tcp': timing.connectEnd - timing.connectStart,
                        'request': timing.responseStart - timing.requestStart,
                        'response': timing.responseEnd - timing.responseStart,
                        'dom': timing.domComplete - timing.domLoading,
                        'loadTime': timing.loadEventEnd - timing.navigationStart
                    };
                }
            """)
            
            allure.attach(
                f"DNS: {timing.get('dns')}ms\n"
                f"TCP: {timing.get('tcp')}ms\n"
                f"请求: {timing.get('request')}ms\n"
                f"响应: {timing.get('response')}ms\n"
                f"DOM: {timing.get('dom')}ms\n"
                f"总加载时间: {timing.get('loadTime')}ms",
                "性能数据",
                allure.attachment_type.TEXT
            )
        
        with allure.step("验证性能指标"):
            load_time = timing.get('loadTime', 0)
            assert load_time > 0, "未获取到加载时间"
            assert load_time < 10000, f"页面加载时间过长: {load_time}ms"


@allure.feature("数据驱动测试")
@allure.story("使用外部数据")
class TestDataDriven:
    """数据驱动测试示例"""
    
    # 测试数据
    search_data = [
        {"keyword": "Python", "expected_in_title": True},
        {"keyword": "Playwright", "expected_in_title": True},
        {"keyword": "测试自动化", "expected_in_title": True},
    ]
    
    @allure.title("测试数据驱动搜索-{data[keyword]}")
    @pytest.mark.parametrize("data", search_data)
    def test_data_driven_search(
        self, 
        page: Page, 
        base_url: str, 
        data: dict
    ):
        """
        测试用例：数据驱动的搜索测试
        """
        keyword = data["keyword"]
        
        with allure.step(f"搜索关键词: {keyword}"):
            page.goto(base_url)
            
            page.locator("#kw").fill(keyword)
            page.locator("#su").click()
            
            # 等待搜索结果
            page.wait_for_selector("#content_left", timeout=10000)
        
        with allure.step("验证搜索结果"):
            # 等待页面标题更新
            time.sleep(1)
            page_title = page.title()
            allure.attach(page_title, "搜索结果页标题", allure.attachment_type.TEXT)
            
            # 验证标题包含"百度"
            assert "百度" in page_title, "搜索结果页标题异常"


@allure.feature("高级定位器")
@allure.story("Playwright 定位器特性")
class TestAdvancedLocators:
    """Playwright 高级定位器测试"""
    
    @allure.title("测试文本定位器")
    @allure.severity(allure.severity_level.NORMAL)
    def test_text_locators(self, page: Page, base_url: str):
        """
        测试用例：测试 Playwright 的文本定位器
        """
        page.goto(base_url)
        
        with allure.step("通过精确文本定位"):
            # 查找包含"新闻"的元素
            element = page.get_by_text("新闻", exact=False)
            if element.count() > 0:
                allure.attach("找到包含'新闻'的元素", "文本定位", allure.attachment_type.TEXT)
        
        with allure.step("通过角色定位"):
            # 查找按钮角色的元素
            buttons = page.get_by_role("button")
            allure.attach(f"找到 {buttons.count()} 个按钮", "角色定位", allure.attachment_type.TEXT)
    
    @allure.title("测试链式定位器")
    @allure.severity(allure.severity_level.NORMAL)
    def test_chained_locators(self, page: Page, base_url: str):
        """
        测试用例：测试 Playwright 的链式定位器
        """
        page.goto(base_url)
        
        with allure.step("使用链式定位器"):
            # 在搜索框容器中查找输入框
            search_input = page.locator("form").locator("#kw")
            expect(search_input).to_be_visible()
            allure.attach("链式定位成功", "定位结果", allure.attachment_type.TEXT)

