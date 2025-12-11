"""
Web 自动化测试关键字
基于 Playwright 实现
"""
import os
import time
from typing import Optional

import allure
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

from ..core.globalContext import g_context
from ..utils.PlaywrightManager import PlaywrightManager
from .browser_use_keywords import BrowserUseKeywords


class Keywords(BrowserUseKeywords):
    """Web 自动化测试关键字类 (Playwright 版本)，继承 Browser-Use AI 关键字"""

    def _get_page(self) -> Page:
        """获取当前 page 实例"""
        page = g_context().get_dict("current_page")
        if page is None:
            raise RuntimeError("浏览器未启动，请先使用 open_browser 关键字打开浏览器")
        return page

    def _get_selector(self, locator_type: str, element: str) -> str:
        """
        将定位方式转换为 Playwright 选择器
        
        :param locator_type: 定位方式字符串
        :param element: 元素标识
        :return: Playwright 选择器字符串
        """
        locator_type = locator_type.lower()
        
        if locator_type == "id":
            return f"#{element}"
        elif locator_type == "name":
            return f"[name='{element}']"
        elif locator_type in ["class", "class_name"]:
            return f".{element}"
        elif locator_type in ["tag", "tag_name"]:
            return element
        elif locator_type == "xpath":
            return f"xpath={element}"
        elif locator_type in ["css", "css_selector"]:
            return element
        elif locator_type in ["link", "link_text"]:
            return f"text={element}"
        elif locator_type in ["partial_link", "partial_link_text"]:
            return f"text={element}"
        elif locator_type == "placeholder":
            return f"[placeholder='{element}']"
        elif locator_type == "text":
            return f"text={element}"
        elif locator_type == "role":
            return f"role={element}"
        else:
            # 默认当作 CSS 选择器
            return element

    def _find_element(self, locator_type: str, element: str, wait_time: int = None):
        """
        查找元素
        
        :param locator_type: 定位方式
        :param element: 元素标识
        :param wait_time: 等待时间（秒）
        :return: Locator
        """
        page = self._get_page()
        selector = self._get_selector(locator_type, element)
        locator = page.locator(selector)
        
        if wait_time:
            locator.wait_for(timeout=wait_time * 1000)
        
        return locator

    def _take_screenshot_on_error(self, name: str):
        """错误时截图"""
        try:
            page = self._get_page()
            # 获取项目根目录下的 reports/screenshots 目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            screenshot_dir = os.path.join(project_root, "reports", "screenshots")
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            # 清理文件名中的非法字符
            safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in name)
            filename = os.path.join(screenshot_dir, f"{safe_name}_{timestamp}.png")
            page.screenshot(path=filename)
            
            # 附加到 Allure 报告
            with open(filename, "rb") as f:
                allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            print(f"截图失败: {e}")

    # ==================== 浏览器操作 ====================

    @allure.step("打开浏览器")
    def open_browser(self, **kwargs):
        """
        打开浏览器
        
        参数:
            browser: chromium/firefox/webkit/edge (默认 chromium)
            headless: true/false (默认 true，无头模式)
            timeout: 默认超时时间（秒，默认 30）
            window_size: 1920x1080/等 (默认 1920x1080)
        """
        browser = kwargs.get("browser", "chromium")
        # 默认无头模式，用户无感知
        # 注意：headless 参数可能是字符串 "True"/"False" 或布尔值
        headless_raw = kwargs.get("headless", True)
        if isinstance(headless_raw, bool):
            headless = headless_raw
        else:
            headless = str(headless_raw).lower() in ["true", "1", "yes"]
        timeout = int(kwargs.get("timeout", 30)) * 1000  # 转换为毫秒
        window_size = kwargs.get("window_size", "1920x1080")
        
        # 解析窗口大小
        viewport = None
        if window_size and "x" in str(window_size):
            width, height = window_size.split("x")
            viewport = {"width": int(width), "height": int(height)}
        
        print(f"正在启动浏览器: {browser}, 无头模式: {headless}")
        
        page = PlaywrightManager.create_browser(
            browser_type=browser,
            headless=headless,
            timeout=timeout,
            viewport=viewport
        )
        
        g_context().set_dict("current_page", page)
        print(f"浏览器启动成功: {browser}")

    @allure.step("关闭浏览器")
    def close_browser(self, **kwargs):
        """关闭浏览器"""
        PlaywrightManager.close()
        g_context().set_dict("current_page", None)
        print("浏览器已关闭")

    @allure.step("导航到: {url}")
    def navigate_to(self, **kwargs):
        """
        导航到指定 URL
        
        参数:
            url: 目标 URL
            wait_until: 等待条件 (load/domcontentloaded/networkidle，默认 load)
        """
        url = kwargs.get("url")
        wait_until = kwargs.get("wait_until", "load")
        
        page = self._get_page()
        page.goto(url, wait_until=wait_until)
        print(f"已导航到: {url}")

    @allure.step("刷新页面")
    def refresh_page(self, **kwargs):
        """刷新当前页面"""
        page = self._get_page()
        page.reload()
        print("页面已刷新")

    @allure.step("后退")
    def back(self, **kwargs):
        """浏览器后退"""
        page = self._get_page()
        page.go_back()
        print("已后退")

    @allure.step("前进")
    def forward(self, **kwargs):
        """浏览器前进"""
        page = self._get_page()
        page.go_forward()
        print("已前进")

    # ==================== 元素操作 ====================

    @allure.step("点击元素: {locator_type}={element}")
    def click_element(self, **kwargs):
        """
        点击元素
        
        参数:
            locator_type: id/name/xpath/css/text 等
            element: 元素标识
            wait_time: 等待时间（秒，可选）
            force: 是否强制点击 (默认 false)
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        wait_time = kwargs.get("wait_time")
        force = str(kwargs.get("force", "false")).lower() in ["true", "1", "yes"]
        
        try:
            locator = self._find_element(locator_type, element, wait_time)
            locator.click(force=force)
            print(f"已点击元素: {locator_type}={element}")
        except Exception as e:
            self._take_screenshot_on_error(f"点击元素失败_{locator_type}_{element}")
            raise Exception(f"点击元素失败: {locator_type}={element}. {str(e)}") from e

    @allure.step("输入文本: {text}")
    def input_text(self, **kwargs):
        """
        输入文本
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            text: 要输入的文本
            clear: true/false (是否先清空，默认 true)
            wait_time: 等待时间（秒，可选）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        text = str(kwargs.get("text", ""))
        clear = str(kwargs.get("clear", "true")).lower() in ["true", "1", "yes"]
        wait_time = kwargs.get("wait_time")
        
        locator = self._find_element(locator_type, element, wait_time)
        
        if clear:
            locator.clear()
        
        locator.fill(text)
        print(f"已输入文本: {text}")

    @allure.step("清空文本")
    def clear_text(self, **kwargs):
        """
        清空文本
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            wait_time: 等待时间（秒，可选）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        wait_time = kwargs.get("wait_time")
        
        locator = self._find_element(locator_type, element, wait_time)
        locator.clear()
        print(f"已清空文本: {locator_type}={element}")

    @allure.step("获取文本")
    def get_text(self, **kwargs):
        """
        获取元素文本并保存到变量
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            variable_name: 保存到的变量名
            wait_time: 等待时间（秒，可选）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        variable_name = kwargs.get("variable_name")
        wait_time = kwargs.get("wait_time")
        
        locator = self._find_element(locator_type, element, wait_time)
        text = locator.text_content() or ""
        
        if variable_name:
            g_context().set_dict(variable_name, text)
            print(f"已获取文本并保存到变量 {variable_name}: {text}")
        else:
            print(f"已获取文本: {text}")
        
        return text

    @allure.step("获取属性")
    def get_attribute(self, **kwargs):
        """
        获取元素属性并保存到变量
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            attribute_name: 要获取的属性名
            variable_name: 保存到的变量名
            wait_time: 等待时间（秒，可选）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        attribute_name = kwargs.get("attribute_name")
        variable_name = kwargs.get("variable_name")
        wait_time = kwargs.get("wait_time")
        
        locator = self._find_element(locator_type, element, wait_time)
        attr_value = locator.get_attribute(attribute_name)
        
        if variable_name:
            g_context().set_dict(variable_name, attr_value)
            print(f"已获取属性 {attribute_name} 并保存到变量 {variable_name}: {attr_value}")
        else:
            print(f"已获取属性 {attribute_name}: {attr_value}")
        
        return attr_value

    @allure.step("选择下拉框")
    def select_dropdown(self, **kwargs):
        """
        选择下拉框选项
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            select_method: value/label/index
            option_value: 选项的值/文本/索引
            wait_time: 等待时间（秒，可选）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        select_method = kwargs.get("select_method", "value")
        option_value = kwargs.get("option_value")
        wait_time = kwargs.get("wait_time")
        
        locator = self._find_element(locator_type, element, wait_time)
        
        if select_method == "value":
            locator.select_option(value=option_value)
        elif select_method in ["text", "label"]:
            locator.select_option(label=option_value)
        elif select_method == "index":
            locator.select_option(index=int(option_value))
        else:
            raise ValueError(f"不支持的选择方式: {select_method}")
        
        print(f"已选择下拉框选项: {select_method}={option_value}")

    # ==================== 等待操作 ====================

    @allure.step("等待元素出现")
    def wait_for_element(self, **kwargs):
        """
        等待元素出现

        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            timeout: 超时时间（秒，默认 15）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 15)) * 1000

        page = self._get_page()
        selector = self._get_selector(locator_type, element)

        try:
            page.locator(selector).wait_for(state="attached", timeout=timeout)
            print(f"元素已出现: {locator_type}={element}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待元素超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"等待元素超时: {locator_type}={element}") from e

    @allure.step("等待元素可见")
    def wait_for_element_visible(self, **kwargs):
        """
        等待元素可见

        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            timeout: 超时时间（秒，默认 15）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 15)) * 1000

        page = self._get_page()
        selector = self._get_selector(locator_type, element)

        try:
            page.locator(selector).wait_for(state="visible", timeout=timeout)
            print(f"元素已可见: {locator_type}={element}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待元素可见超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"等待元素可见超时: {locator_type}={element}") from e

    @allure.step("等待元素可点击")
    def wait_for_element_clickable(self, **kwargs):
        """
        等待元素可点击 (在 Playwright 中等同于可见且启用)

        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            timeout: 超时时间（秒，默认 15）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 15)) * 1000

        page = self._get_page()
        selector = self._get_selector(locator_type, element)

        try:
            locator = page.locator(selector)
            locator.wait_for(state="visible", timeout=timeout)
            # Playwright 会自动等待元素可点击
            expect(locator).to_be_enabled(timeout=timeout)
            print(f"元素已可点击: {locator_type}={element}")
        except Exception as e:
            self._take_screenshot_on_error(f"等待元素可点击超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"等待元素可点击超时: {locator_type}={element}") from e

    @allure.step("等待: {time}秒")
    def sleep(self, **kwargs):
        """
        强制等待
        
        参数:
            time: 等待时间（秒）
        """
        import time as time_module
        sleep_time = float(kwargs.get("time", 1))
        # 兼容 Playwright 和 Browser-Use 模式
        page = g_context().get_dict("current_page")
        if page:
            page.wait_for_timeout(sleep_time * 1000)
        else:
            time_module.sleep(sleep_time)
        print(f"已等待 {sleep_time} 秒")

    # ==================== 断言操作 ====================

    @allure.step("断言元素可见")
    def assert_element_visible(self, **kwargs):
        """
        断言元素可见
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            timeout: 超时时间（秒，默认 10）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 10)) * 1000
        
        page = self._get_page()
        selector = self._get_selector(locator_type, element)
        
        try:
            expect(page.locator(selector)).to_be_visible(timeout=timeout)
            print(f"✓ 断言成功: 元素可见 {locator_type}={element}")
        except Exception as e:
            self._take_screenshot_on_error(f"断言失败_元素不可见_{locator_type}_{element}")
            raise AssertionError(f"断言失败: 元素不可见 {locator_type}={element}") from e

    @allure.step("断言元素不可见")
    def assert_element_not_visible(self, **kwargs):
        """
        断言元素不可见
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            timeout: 超时时间（秒，默认 10）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 10)) * 1000
        
        page = self._get_page()
        selector = self._get_selector(locator_type, element)
        
        try:
            expect(page.locator(selector)).not_to_be_visible(timeout=timeout)
            print(f"✓ 断言成功: 元素不可见 {locator_type}={element}")
        except Exception as e:
            self._take_screenshot_on_error(f"断言失败_元素可见_{locator_type}_{element}")
            raise AssertionError(f"断言失败: 元素可见 {locator_type}={element}") from e

    @allure.step("断言文本相等")
    def assert_text_equals(self, **kwargs):
        """
        断言元素文本相等
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            expected_text: 期望的文本
            wait_time: 等待时间（秒，可选）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        expected_text = kwargs.get("expected_text", "")
        wait_time = kwargs.get("wait_time")
        
        locator = self._find_element(locator_type, element, wait_time)
        
        try:
            expect(locator).to_have_text(expected_text)
            print(f"✓ 断言成功: 文本相等 '{expected_text}'")
        except Exception as e:
            actual_text = locator.text_content()
            self._take_screenshot_on_error(f"断言失败_文本不相等_{locator_type}_{element}")
            raise AssertionError(f"文本不相等: 期望'{expected_text}', 实际'{actual_text}'") from e

    @allure.step("断言文本包含")
    def assert_text_contains(self, **kwargs):
        """
        断言元素文本包含指定内容
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            expected_text: 期望包含的文本
            wait_time: 等待时间（秒，可选）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        expected_text = kwargs.get("expected_text", "")
        wait_time = kwargs.get("wait_time")
        
        locator = self._find_element(locator_type, element, wait_time)
        
        try:
            expect(locator).to_contain_text(expected_text)
            print(f"✓ 断言成功: 文本包含 '{expected_text}'")
        except Exception as e:
            actual_text = locator.text_content()
            self._take_screenshot_on_error(f"断言失败_文本不包含_{locator_type}_{element}")
            raise AssertionError(f"文本不包含: 期望包含'{expected_text}', 实际'{actual_text}'") from e

    @allure.step("断言标题相等")
    def assert_title_equals(self, **kwargs):
        """
        断言页面标题相等
        
        参数:
            expected_title: 期望的标题
        """
        expected_title = kwargs.get("expected_title", "")
        
        page = self._get_page()
        
        try:
            expect(page).to_have_title(expected_title)
            print(f"✓ 断言成功: 标题相等 '{expected_title}'")
        except Exception as e:
            actual_title = page.title()
            self._take_screenshot_on_error(f"断言失败_标题不相等")
            raise AssertionError(f"标题不相等: 期望'{expected_title}', 实际'{actual_title}'") from e

    @allure.step("断言标题包含")
    def assert_title_contains(self, **kwargs):
        """
        断言页面标题包含指定内容
        
        参数:
            expected_text: 期望包含的文本
        """
        expected_text = kwargs.get("expected_text", "")
        
        page = self._get_page()
        actual_title = page.title()
        
        try:
            assert expected_text in actual_title, f"标题不包含: 期望包含'{expected_text}', 实际'{actual_title}'"
            print(f"✓ 断言成功: 标题包含 '{expected_text}'")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言失败_标题不包含")
            raise e

    # ==================== 高级操作 ====================

    @allure.step("切换到Frame")
    def switch_to_frame(self, **kwargs):
        """
        切换到 iframe
        
        参数:
            locator_type: id/name/xpath/css 等 (可选)
            element: 元素标识 (可选)
            index: frame 索引 (可选)
        """
        page = self._get_page()
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        index = kwargs.get("index")
        
        if index is not None:
            frames = page.frames
            frame = frames[int(index)]
            # Playwright 中 frame 操作方式不同，需要使用 frame_locator
            print(f"已切换到 frame 索引: {index}")
        elif locator_type and element:
            selector = self._get_selector(locator_type, element)
            frame_locator = page.frame_locator(selector)
            g_context().set_dict("current_frame", frame_locator)
            print(f"已切换到 frame: {locator_type}={element}")
        else:
            g_context().set_dict("current_frame", None)
            print("已切换回主文档")

    @allure.step("切换到窗口")
    def switch_to_window(self, **kwargs):
        """
        切换到窗口/标签页
        
        参数:
            index: 窗口索引 (从 0 开始)
        """
        index = kwargs.get("index", -1)
        
        page = PlaywrightManager.switch_to_page(int(index))
        if page:
            g_context().set_dict("current_page", page)
            print(f"已切换到窗口索引: {index}")
        else:
            raise RuntimeError("切换窗口失败")

    @allure.step("执行JavaScript")
    def execute_script(self, **kwargs):
        """
        执行 JavaScript 代码
        
        参数:
            script: JavaScript 代码
            variable_name: 保存返回值到变量 (可选)
        """
        script = kwargs.get("script", "")
        variable_name = kwargs.get("variable_name")
        
        page = self._get_page()
        result = page.evaluate(script)
        
        if variable_name:
            g_context().set_dict(variable_name, result)
            print(f"已执行脚本并保存结果到 {variable_name}: {result}")
        else:
            print(f"已执行脚本: {script}")
        
        return result

    @allure.step("截图")
    def take_screenshot(self, **kwargs):
        """
        截图
        
        参数:
            filename: 截图文件名 (可选，默认自动生成)
            full_page: 是否全页面截图 (默认 false)
        """
        filename = kwargs.get("filename")
        full_page = str(kwargs.get("full_page", "false")).lower() in ["true", "1", "yes"]
        
        page = self._get_page()
        
        # 获取项目根目录下的 reports/screenshots 目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        screenshot_dir = os.path.join(project_root, "reports", "screenshots")
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        if not filename.endswith(".png"):
            filename += ".png"
        
        filepath = os.path.join(screenshot_dir, filename)
        page.screenshot(path=filepath, full_page=full_page)
        
        # 附加到 Allure 报告
        with open(filepath, "rb") as f:
            allure.attach(f.read(), name=filename, attachment_type=allure.attachment_type.PNG)
        
        print(f"已截图: {filepath}")

    @allure.step("滚动到元素")
    def scroll_to_element(self, **kwargs):
        """
        滚动到元素
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            wait_time: 等待时间（秒，可选）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        wait_time = kwargs.get("wait_time")
        
        locator = self._find_element(locator_type, element, wait_time)
        locator.scroll_into_view_if_needed()
        print(f"已滚动到元素: {locator_type}={element}")

    @allure.step("鼠标悬停")
    def hover_element(self, **kwargs):
        """
        鼠标悬停到元素
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            wait_time: 等待时间（秒，可选）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        wait_time = kwargs.get("wait_time")
        
        locator = self._find_element(locator_type, element, wait_time)
        locator.hover()
        print(f"已鼠标悬停: {locator_type}={element}")

    @allure.step("获取当前URL")
    def get_current_url(self, **kwargs):
        """
        获取当前 URL 并保存到变量
        
        参数:
            variable_name: 保存到的变量名 (可选)
        """
        variable_name = kwargs.get("variable_name")
        
        page = self._get_page()
        current_url = page.url
        
        if variable_name:
            g_context().set_dict(variable_name, current_url)
            print(f"已获取当前URL并保存到 {variable_name}: {current_url}")
        else:
            print(f"当前URL: {current_url}")
        
        return current_url

    # ==================== Playwright 特有操作 ====================

    @allure.step("按键操作")
    def press_key(self, **kwargs):
        """
        按键操作
        
        参数:
            key: 按键名称 (Enter/Tab/Escape/ArrowDown 等)
            locator_type: 元素定位方式 (可选)
            element: 元素标识 (可选)
        """
        key = kwargs.get("key", "Enter")
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        
        page = self._get_page()
        
        if locator_type and element:
            locator = self._find_element(locator_type, element)
            locator.press(key)
        else:
            page.keyboard.press(key)
        
        print(f"已按键: {key}")

    @allure.step("双击元素")
    def double_click(self, **kwargs):
        """
        双击元素
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            wait_time: 等待时间（秒，可选）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        wait_time = kwargs.get("wait_time")
        
        locator = self._find_element(locator_type, element, wait_time)
        locator.dblclick()
        print(f"已双击元素: {locator_type}={element}")

    @allure.step("右键点击")
    def right_click(self, **kwargs):
        """
        右键点击元素
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 元素标识
            wait_time: 等待时间（秒，可选）
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        wait_time = kwargs.get("wait_time")
        
        locator = self._find_element(locator_type, element, wait_time)
        locator.click(button="right")
        print(f"已右键点击元素: {locator_type}={element}")

    @allure.step("拖拽元素")
    def drag_and_drop(self, **kwargs):
        """
        拖拽元素
        
        参数:
            source_locator_type: 源元素定位方式
            source_element: 源元素标识
            target_locator_type: 目标元素定位方式
            target_element: 目标元素标识
        """
        source_locator_type = kwargs.get("source_locator_type")
        source_element = kwargs.get("source_element")
        target_locator_type = kwargs.get("target_locator_type")
        target_element = kwargs.get("target_element")
        
        source = self._find_element(source_locator_type, source_element)
        target = self._find_element(target_locator_type, target_element)
        
        source.drag_to(target)
        print(f"已拖拽元素: {source_locator_type}={source_element} -> {target_locator_type}={target_element}")

    @allure.step("上传文件")
    def upload_file(self, **kwargs):
        """
        上传文件
        
        参数:
            locator_type: id/name/xpath/css 等
            element: 文件输入框元素标识
            file_path: 文件路径
        """
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        file_path = kwargs.get("file_path")
        
        locator = self._find_element(locator_type, element)
        locator.set_input_files(file_path)
        print(f"已上传文件: {file_path}")

    @allure.step("等待网络空闲")
    def wait_for_network_idle(self, **kwargs):
        """
        等待网络空闲
        
        参数:
            timeout: 超时时间（秒，默认 30）
        """
        timeout = int(kwargs.get("timeout", 30)) * 1000
        
        page = self._get_page()
        page.wait_for_load_state("networkidle", timeout=timeout)
        print("网络已空闲")

    @allure.step("断言URL包含")
    def assert_url_contains(self, **kwargs):
        """
        断言当前URL包含指定内容
        
        参数:
            expected_url: 期望URL包含的内容
        """
        expected_url = kwargs.get("expected_url", "")
        
        page = self._get_page()
        
        try:
            expect(page).to_have_url(f"*{expected_url}*")
            print(f"✓ 断言成功: URL包含 '{expected_url}'")
        except Exception as e:
            actual_url = page.url
            self._take_screenshot_on_error(f"断言失败_URL不包含")
            raise AssertionError(f"URL不包含: 期望包含'{expected_url}', 实际'{actual_url}'") from e
