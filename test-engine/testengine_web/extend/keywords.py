"""
Web 自动化测试关键字
基于 Playwright 实现
"""
import os
import time
from typing import Optional

import allure
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

from ..core.globalContext import g_context
from ..utils.PlaywrightManager import PlaywrightManager


class Keywords:
    """Web 自动化测试关键字类"""

    def _get_page(self):
        """获取当前页面实例"""
        page = g_context().get_dict("current_page")
        if page is None:
            raise RuntimeError("浏览器页面未初始化，请先使用 open_browser 关键字打开浏览器")
        return page

    def _get_locator(self, locator_type, element):
        """
        获取 Playwright 定位器
        
        :param locator_type: locator_type字符串
        :param element: element标识
        :return: Playwright Locator
        """
        page = self._get_page()
        locator_type = locator_type.lower()
        
        # Playwright 现代locator_type
        if locator_type == "role":
            # 按角色定位：支持多种格式
            # 格式1: button[name="百度一下"]
            # 格式2: button,name=Submit
            # 格式3: button
            if "[name=" in element:
                # 格式1: button[name="百度一下"]
                import re
                match = re.match(r'(\w+)\[name="([^"]+)"\]', element)
                if match:
                    role, name = match.groups()
                    return page.get_by_role(role, name=name)
            elif "," in element:
                # 格式2: button,name=Submit
                role, name_part = element.split(",", 1)
                if name_part.startswith("name="):
                    name = name_part[5:]
                    return page.get_by_role(role, name=name)
            # 格式3: button
            return page.get_by_role(element)
        elif locator_type == "text":
            return page.get_by_text(element)
        elif locator_type == "label":
            return page.get_by_label(element)
        elif locator_type == "placeholder":
            return page.get_by_placeholder(element)
        elif locator_type == "test_id" or locator_type == "testid":
            return page.get_by_test_id(element)
        elif locator_type == "alt":
            return page.get_by_alt_text(element)
        elif locator_type == "title":
            return page.get_by_title(element)
        # 传统locator_type
        elif locator_type == "id":
            return page.locator(f"#{element}")
        elif locator_type == "name":
            return page.locator(f"[name='{element}']")
        elif locator_type == "class" or locator_type == "class_name":
            return page.locator(f".{element}")
        elif locator_type == "tag" or locator_type == "tag_name":
            return page.locator(element)
        elif locator_type == "xpath":
            return page.locator(f"xpath={element}")
        elif locator_type == "css" or locator_type == "css_selector":
            return page.locator(element)
        else:
            raise ValueError(f"不支持的locator_type: {locator_type}")

    def _take_screenshot_on_error(self, filename_prefix="error"):
        """错误时自动截图"""
        try:
            page = self._get_page()
            timestamp = int(time.time())
            filename = f"{filename_prefix}_{timestamp}.png"
            # 使用 test-engine 目录下的 reports/screenshots
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # test-engine 目录
            screenshot_dir = os.path.join(project_root, "reports", "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, filename)
            page.screenshot(path=screenshot_path, full_page=True)
            allure.attach.file(screenshot_path, name=f"错误截图_{filename_prefix}", attachment_type=allure.attachment_type.PNG)
            print(f"错误截图已保存: {screenshot_path}")
        except Exception as e:
            print(f"截图失败: {e}")

    # ==================== 浏览器操作 ====================

    @allure.step("打开浏览器")
    def open_browser(self, **kwargs):
        """
        打开浏览器

        参数:
            browser: chromium/firefox/webkit (默认 chromium)
            headless: true/false (默认 false)
            timeout: timeout（毫秒，默认 60000）
            implicit_wait: 隐式等待时间（秒，将转换为 Playwright 的 default_timeout）
            window_size: maximize/1920x1080/等 (默认 maximize)
            enable_tracing: true/false (默认 false)
            url: 可选，打开浏览器后立即导航到该URL
        """
        kwargs.pop("关键字", None)

        browser = kwargs.get("browser", "chromium")
        headless = str(kwargs.get("headless", "false")).lower() in ["true", "1", "yes"]
        # implicit_wait 转换为毫秒（Playwright 使用毫秒）
        implicit_wait = kwargs.get("implicit_wait")
        if implicit_wait:
            timeout = int(float(implicit_wait) * 1000)  # 秒转毫秒
        else:
            timeout = int(kwargs.get("timeout", 60000))  # 默认60秒
        window_size = kwargs.get("window_size", "maximize")
        enable_tracing = str(kwargs.get("enable_tracing", "false")).lower() in ["true", "1", "yes"]
        url = kwargs.get("url")  # 可选的URL参数

        print(f"正在启动浏览器: {browser}, 无头模式: {headless}")

        # 创建页面
        page = PlaywrightManager.create_page(
            browser=browser,
            headless=headless,
            timeout=timeout,
            window_size=window_size
        )

        # 启用追踪（如果需要）
        if enable_tracing:
            PlaywrightManager.enable_tracing()

        # 保存到全局上下文
        g_context().set_dict("current_page", page)
        g_context().set_dict("current_browser", browser)

        # 如果提供了URL，立即导航
        if url:
            try:
                page.goto(url, wait_until="load", timeout=timeout)
                print(f"已导航到: {url}")
            except Exception as e:
                print(f"导航到 {url} 失败: {e}")
                raise

        print(f"浏览器启动成功: {browser}")

    @allure.step("关闭浏览器")
    def close_browser(self, **kwargs):
        """关闭浏览器"""
        kwargs.pop("关键字", None)
        
        # 停止追踪（如果启用了）
        try:
            PlaywrightManager.stop_tracing("trace.zip")
        except:
            pass
        
        PlaywrightManager.close_all()
        g_context().set_dict("current_page", None)
        g_context().set_dict("current_browser", None)
        print("浏览器已关闭")

    @allure.step("导航到: {url}")
    def navigate_to(self, **kwargs):
        """
        导航到指定 URL
        
        参数:
            url: 目标 URL
            wait_until: load/domcontentloaded/networkidle (默认 load)
            timeout: timeout（毫秒，可选）
        """
        kwargs.pop("关键字", None)
        
        url = kwargs.get("url")
        wait_until = kwargs.get("wait_until", "load")
        timeout = kwargs.get("timeout")
        
        if not url:
            raise ValueError("url 参数不能为空")
        
        page = self._get_page()
        
        try:
            if timeout:
                page.goto(url, wait_until=wait_until, timeout=int(timeout))
            else:
                page.goto(url, wait_until=wait_until)
            print(f"已导航到: {url}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"导航超时_{url.replace('://', '_').replace('/', '_')}")
            raise PlaywrightTimeoutError(f"导航到 {url} 超时") from e

    @allure.step("点击element: {locator_type}={element}")
    def click_element(self, **kwargs):
        """
        点击element
        
        参数:
            locator_type: id/name/xpath/css/role/text/label 等
            element: element标识
            timeout: timeout（毫秒，可选）
            force_click: true/false (默认 false)
        """
        kwargs.pop("关键字", None)
        
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = kwargs.get("timeout")
        force_click = str(kwargs.get("force_click", "false")).lower() in ["true", "1", "yes"]
        
        locator = self._get_locator(locator_type, element)
        
        try:
            if timeout:
                locator.click(timeout=int(timeout), force=force_click)
            else:
                locator.click(force=force_click)
            print(f"已点击element: {locator_type}={element}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"点击超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"点击element超时: {locator_type}={element}") from e

    @allure.step("输入text: {text}")
    def input_text(self, **kwargs):
        """
        输入text到element

        参数:
            locator_type: id/name/xpath/css/role/text/label 等
            element: element标识
            text: 要输入的text
            clear: true/false (默认 true)
            timeout: timeout（毫秒，默认10000）
            wait_visible: 是否等待元素可见 (默认 true)
        """
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        text = kwargs.get("text", "")
        clear = str(kwargs.get("clear", "true")).lower() in ["true", "1", "yes"]
        timeout = int(kwargs.get("timeout", 10000))  # 默认10秒
        wait_visible = str(kwargs.get("wait_visible", "true")).lower() in ["true", "1", "yes"]
        force_action = str(kwargs.get("force_action", "false")).lower() in ["true", "1", "yes"]

        locator = self._get_locator(locator_type, element)

        try:
            # 先等待元素可见（如果需要）
            if wait_visible:
                try:
                    locator.wait_for(state="visible", timeout=timeout)
                except PlaywrightTimeoutError:
                    print(f"警告: 元素 {locator_type}={element} 不可见，尝试强制操作")
                    if not force_action:
                        force_action = True

            # 如果element隐藏，先尝试点击使其可见
            if force_action:
                try:
                    locator.click(force=True, timeout=2000)
                except:
                    pass

            # 执行输入操作
            if clear:
                locator.fill(text, timeout=timeout, force=force_action)
            else:
                locator.type(text, timeout=timeout)
            print(f"已输入text: {text} 到 {locator_type}={element}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"输入text超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"输入text超时: {locator_type}={element}, 请检查元素是否存在或页面是否加载完成") from e
        except Exception as e:
            self._take_screenshot_on_error(f"输入text失败_{locator_type}_{element}")
            raise Exception(f"输入text失败: {locator_type}={element}, 错误: {str(e)}") from e

    @allure.step("等待页面加载完成")
    def wait_for_page_load(self, **kwargs):
        """
        等待页面加载完成

        参数:
            wait_until: load/domcontentloaded/networkidle (默认 load)
            timeout: 超时时间（毫秒，默认60000）
        """
        kwargs.pop("关键字", None)

        wait_until = kwargs.get("wait_until", "load")  # load/domcontentloaded/networkidle
        timeout = int(kwargs.get("timeout", 60000))  # 默认60秒

        page = self._get_page()

        try:
            # 先等待 domcontentloaded，然后根据需要等待 load 或 networkidle
            if wait_until == "networkidle":
                page.wait_for_load_state("domcontentloaded", timeout=timeout)
                page.wait_for_load_state("networkidle", timeout=timeout)
            elif wait_until == "domcontentloaded":
                page.wait_for_load_state("domcontentloaded", timeout=timeout)
            else:  # load
                page.wait_for_load_state("load", timeout=timeout)

            print(f"页面加载完成: {wait_until}")
            # 额外等待100ms确保DOM完全稳定
            time.sleep(0.1)
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待页面加载超时_{wait_until}")
            raise PlaywrightTimeoutError(f"等待页面加载超时: {wait_until}，请检查网络连接或页面是否正常") from e

    @allure.step("断言页面标题: {expected_title}")
    def assert_title(self, **kwargs):
        """断言页面标题"""
        kwargs.pop("关键字", None)
        
        expected_title = kwargs.get("expected_title")
        timeout = int(kwargs.get("timeout", 5000))
        
        page = self._get_page()
        
        try:
            expect(page).to_have_title(expected_title, timeout=timeout)
            print(f"断言成功: 页面标题为 '{expected_title}'")
        except AssertionError as e:
            actual_title = page.title()
            self._take_screenshot_on_error(f"断言页面标题失败_{expected_title}")
            raise AssertionError(f"断言失败: expected_title '{expected_title}'，实际标题 '{actual_title}'") from e

    @allure.step("断言text包含: {expected_text}")
    def assert_text_contains(self, **kwargs):
        """断言elementtext包含指定内容"""
        kwargs.pop("关键字", None)
        
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        expected_text = kwargs.get("expected_text")
        timeout = int(kwargs.get("timeout", 5000))
        
        if locator_type and element:
            locator = self._get_locator(locator_type, element)
        else:
            # 如果没有指定element，则检查整个页面
            page = self._get_page()
            locator = page.locator("body")
        
        try:
            expect(locator).to_contain_text(expected_text, timeout=timeout)
            print(f"断言成功: text包含 '{expected_text}'")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言text包含失败_{expected_text}")
            raise AssertionError(f"断言失败: text不包含 '{expected_text}'") from e

    @allure.step("截图")
    def take_screenshot(self, **kwargs):
        """截图"""
        kwargs.pop("关键字", None)
        
        filename = kwargs.get("filename", f"screenshot_{int(time.time())}")
        full_page = str(kwargs.get("full_page", "true")).lower() in ["true", "1", "yes"]
        
        page = self._get_page()
        
        # 确保filename有扩展名
        if not filename.endswith('.png'):
            filename += '.png'
        
        # 使用 test-engine 目录下的 reports/screenshots
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # test-engine 目录
        screenshot_dir = os.path.join(project_root, "reports", "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, filename)
        
        # 截图
        page.screenshot(path=screenshot_path, full_page=full_page)
        
        # 添加到 Allure 报告
        allure.attach.file(screenshot_path, name=f"截图_{filename}", attachment_type=allure.attachment_type.PNG)
        
        print(f"截图已保存: {screenshot_path}")
        return screenshot_path

    @allure.step("断言页面标题等于: {expected_title}")
    def assert_title_equals(self, **kwargs):
        """断言页面标题等于指定内容"""
        kwargs.pop("关键字", None)

        expected_title = kwargs.get("expected_title")
        timeout = int(kwargs.get("timeout", 5000))

        page = self._get_page()

        try:
            expect(page).to_have_title(expected_title, timeout=timeout)
            print(f"断言成功: 页面标题等于 '{expected_title}'")
        except AssertionError as e:
            actual_title = page.title()
            self._take_screenshot_on_error(f"断言页面标题等于失败_{expected_title}")
            raise AssertionError(f"断言失败: expected_title '{expected_title}'，实际标题 '{actual_title}'") from e

    @allure.step("断言页面标题包含: {expected_text}")
    def assert_title_contains(self, **kwargs):
        """断言页面标题包含指定text"""
        kwargs.pop("关键字", None)

        expected_text = kwargs.get("expected_text")
        timeout = int(kwargs.get("timeout", 5000))

        page = self._get_page()

        try:
            # Playwright 没有直接的 title contains 断言，我们手动实现
            actual_title = page.title()
            if expected_text not in actual_title:
                raise AssertionError(f"断言失败: 页面标题 '{actual_title}' 不包含 '{expected_text}'")
            print(f"断言成功: 页面标题包含 '{expected_text}'")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言页面标题包含失败_{expected_text}")
            raise e

    @allure.step("获取element属性: {attribute_name}")
    def get_attribute(self, **kwargs):
        """获取element属性值"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        attribute_name = kwargs.get("attribute_name")
        variable_name = kwargs.get("variable_name")

        locator = self._get_locator(locator_type, element)

        try:
            attribute_value = locator.get_attribute(attribute_name)
            print(f"获取属性成功: {locator_type}={element} 的 {attribute_name} = {attribute_value}")

            # 如果指定了variable_name，保存到全局上下文
            if variable_name:
                g_context().set_dict(variable_name, attribute_value)
                print(f"属性值已保存到变量: {variable_name} = {attribute_value}")

            return attribute_value
        except Exception as e:
            self._take_screenshot_on_error(f"获取属性失败_{locator_type}_{element}_{attribute_name}")
            raise Exception(f"获取element属性失败: {locator_type}={element}, 属性={attribute_name}") from e

    @allure.step("等待: {time}秒")
    def sleep(self, **kwargs):
        """等待指定时间"""
        kwargs.pop("关键字", None)

        duration = float(kwargs.get("time", 1))

        print(f"等待 {duration} 秒...")
        time.sleep(duration)
        print(f"等待完成")

    @allure.step("获取elementtext")
    def get_element_text(self, **kwargs):
        """获取elementtext内容"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        variable_name = kwargs.get("variable_name")

        locator = self._get_locator(locator_type, element)

        try:
            text_content = locator.text_content()
            print(f"获取text成功: {locator_type}={element} 的text = {text_content}")

            # 如果指定了variable_name，保存到全局上下文
            if variable_name:
                g_context().set_dict(variable_name, text_content)
                print(f"text内容已保存到变量: {variable_name} = {text_content}")

            return text_content
        except Exception as e:
            self._take_screenshot_on_error(f"获取text失败_{locator_type}_{element}")
            raise Exception(f"获取elementtext失败: {locator_type}={element}") from e

    @allure.step("等待element可见: {locator_type}={element}")
    def wait_for_element_visible(self, **kwargs):
        """等待element可见"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 30000))

        locator = self._get_locator(locator_type, element)

        try:
            locator.wait_for(state="visible", timeout=timeout)
            print(f"element已可见: {locator_type}={element}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待element可见超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"等待element可见超时: {locator_type}={element}") from e

    @allure.step("等待element隐藏: {locator_type}={element}")
    def wait_for_element_hidden(self, **kwargs):
        """等待element隐藏"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 30000))

        locator = self._get_locator(locator_type, element)

        try:
            locator.wait_for(state="hidden", timeout=timeout)
            print(f"element已隐藏: {locator_type}={element}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待element隐藏超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"等待element隐藏超时: {locator_type}={element}") from e

    @allure.step("获取current_url")
    def get_current_url(self, **kwargs):
        """获取当前页面URL"""
        kwargs.pop("关键字", None)

        variable_name = kwargs.get("variable_name")

        page = self._get_page()

        try:
            current_url = page.url
            print(f"获取current_url成功: {current_url}")

            # 如果指定了variable_name，保存到全局上下文
            if variable_name:
                g_context().set_dict(variable_name, current_url)
                print(f"URL已保存到变量: {variable_name} = {current_url}")

            return current_url
        except Exception as e:
            self._take_screenshot_on_error("获取current_url失败")
            raise Exception("获取current_url失败") from e

    @allure.step("选择下拉框选项")
    def select_dropdown(self, **kwargs):
        """选择下拉框选项"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        select_method = kwargs.get("select_method", "value")  # value/text/index
        option_value = kwargs.get("option_value")

        locator = self._get_locator(locator_type, element)

        try:
            if select_method == "value":
                locator.select_option(value=option_value)
            elif select_method == "text":
                locator.select_option(label=option_value)
            elif select_method == "index":
                locator.select_option(index=int(option_value))
            else:
                raise ValueError(f"不支持的select_method: {select_method}")

            print(f"选择下拉框成功: {locator_type}={element}, {select_method}={option_value}")
        except Exception as e:
            self._take_screenshot_on_error(f"选择下拉框失败_{locator_type}_{element}")
            raise Exception(f"选择下拉框失败: {locator_type}={element}, {select_method}={option_value}") from e

    @allure.step("断言element可见: {locator_type}={element}")
    def assert_element_visible(self, **kwargs):
        """断言element可见"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 5000))

        locator = self._get_locator(locator_type, element)

        try:
            expect(locator).to_be_visible(timeout=timeout)
            print(f"断言成功: element可见 {locator_type}={element}")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言element可见失败_{locator_type}_{element}")
            raise AssertionError(f"断言失败: element不可见 {locator_type}={element}") from e

    @allure.step("断言element存在: {locator_type}={element}")
    def assert_element_exists(self, **kwargs):
        """断言element存在"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 5000))

        locator = self._get_locator(locator_type, element)

        try:
            expect(locator).to_be_attached(timeout=timeout)
            print(f"断言成功: element存在 {locator_type}={element}")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言element存在失败_{locator_type}_{element}")
            raise AssertionError(f"断言失败: element不存在 {locator_type}={element}") from e

    @allure.step("双击element: {locator_type}={element}")
    def double_click_element(self, **kwargs):
        """双击element"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = kwargs.get("timeout")

        locator = self._get_locator(locator_type, element)

        try:
            if timeout:
                locator.dblclick(timeout=int(timeout))
            else:
                locator.dblclick()
            print(f"已双击element: {locator_type}={element}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"双击超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"双击element超时: {locator_type}={element}") from e

    @allure.step("右键点击element: {locator_type}={element}")
    def right_click_element(self, **kwargs):
        """右键点击element"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = kwargs.get("timeout")

        locator = self._get_locator(locator_type, element)

        try:
            if timeout:
                locator.click(button="right", timeout=int(timeout))
            else:
                locator.click(button="right")
            print(f"已右键点击element: {locator_type}={element}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"右键点击超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"右键点击element超时: {locator_type}={element}") from e

    @allure.step("悬停element: {locator_type}={element}")
    def hover_element(self, **kwargs):
        """悬停在element上"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = kwargs.get("timeout")

        locator = self._get_locator(locator_type, element)

        try:
            if timeout:
                locator.hover(timeout=int(timeout))
            else:
                locator.hover()
            print(f"已悬停element: {locator_type}={element}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"悬停超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"悬停element超时: {locator_type}={element}") from e

    @allure.step("切换到iframe")
    def switch_to_frame(self, **kwargs):
        """切换到iframe"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")

        page = self._get_page()

        try:
            if locator_type and element:
                # 切换到指定的iframe
                frame_locator = self._get_locator(locator_type, element)
                frame = page.frame_locator(f"#{element}" if locator_type == "id" else f"[{locator_type}='{element}']")
                # 保存当前frame到上下文
                g_context().set_dict("current_frame", frame)
                print(f"已切换到iframe: {locator_type}={element}")
            else:
                # 切换回主文档
                g_context().set_dict("current_frame", None)
                print("已切换回主文档")
        except Exception as e:
            self._take_screenshot_on_error(f"切换iframe失败_{locator_type}_{element}")
            raise Exception(f"切换iframe失败: {locator_type}={element}") from e

    @allure.step("执行JavaScriptscript")
    def execute_script(self, **kwargs):
        """执行JavaScriptscript"""
        kwargs.pop("关键字", None)

        script = kwargs.get("script")
        variable_name = kwargs.get("variable_name")

        page = self._get_page()

        try:
            result = page.evaluate(script)
            print(f"JavaScript执行成功: {script}")
            print(f"执行结果: {result}")

            # 如果指定了variable_name，保存到全局上下文
            if variable_name:
                g_context().set_dict(variable_name, result)
                print(f"结果已保存到变量: {variable_name} = {result}")

            return result
        except Exception as e:
            self._take_screenshot_on_error("JavaScript执行失败")
            raise Exception(f"JavaScript执行失败: {script}") from e

    @allure.step("clear输入框")
    def clear_element(self, **kwargs):
        """clear输入框"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")

        locator = self._get_locator(locator_type, element)

        try:
            locator.clear()
            print(f"已clear输入框: {locator_type}={element}")
        except Exception as e:
            self._take_screenshot_on_error(f"clear输入框失败_{locator_type}_{element}")
            raise Exception(f"clear输入框失败: {locator_type}={element}") from e

    @allure.step("刷新页面")
    def refresh_page(self, **kwargs):
        """刷新页面"""
        kwargs.pop("关键字", None)

        page = self._get_page()

        try:
            page.reload()
            print("页面刷新成功")
        except Exception as e:
            self._take_screenshot_on_error("页面刷新失败")
            raise Exception("页面刷新失败") from e

    @allure.step("后退")
    def go_back(self, **kwargs):
        """浏览器后退"""
        kwargs.pop("关键字", None)

        page = self._get_page()

        try:
            page.go_back()
            print("浏览器后退成功")
        except Exception as e:
            self._take_screenshot_on_error("浏览器后退失败")
            raise Exception("浏览器后退失败") from e

    @allure.step("前进")
    def go_forward(self, **kwargs):
        """浏览器前进"""
        kwargs.pop("关键字", None)

        page = self._get_page()

        try:
            page.go_forward()
            print("浏览器前进成功")
        except Exception as e:
            self._take_screenshot_on_error("浏览器前进失败")
            raise Exception("浏览器前进失败") from e

    @allure.step("等待element存在: {locator_type}={element}")
    def wait_for_element(self, **kwargs):
        """等待element存在（attached）"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 30000))

        locator = self._get_locator(locator_type, element)

        try:
            locator.wait_for(state="attached", timeout=timeout)
            print(f"element已存在: {locator_type}={element}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待element存在超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"等待element存在超时: {locator_type}={element}") from e

    @allure.step("等待element可点击: {locator_type}={element}")
    def wait_for_element_clickable(self, **kwargs):
        """等待element可点击"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 30000))

        locator = self._get_locator(locator_type, element)

        try:
            # Playwright 中可点击意味着element可见且启用
            locator.wait_for(state="visible", timeout=timeout)
            expect(locator).to_be_enabled(timeout=timeout)
            print(f"element已可点击: {locator_type}={element}")
        except (PlaywrightTimeoutError, AssertionError) as e:
            self._take_screenshot_on_error(f"等待element可点击超时_{locator_type}_{element}")
            raise PlaywrightTimeoutError(f"等待element可点击超时: {locator_type}={element}") from e

    @allure.step("滚动到element: {locator_type}={element}")
    def scroll_to_element(self, **kwargs):
        """滚动到element"""
        kwargs.pop("关键字", None)

        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")

        locator = self._get_locator(locator_type, element)

        try:
            locator.scroll_into_view_if_needed()
            print(f"已滚动到element: {locator_type}={element}")
        except Exception as e:
            self._take_screenshot_on_error(f"滚动到element失败_{locator_type}_{element}")
            raise Exception(f"滚动到element失败: {locator_type}={element}") from e

    @allure.step("等待text出现: {expected_text}")
    def wait_for_text(self, **kwargs):
        """等待页面中出现指定text"""
        kwargs.pop("关键字", None)

        expected_text = kwargs.get("expected_text")
        timeout = int(kwargs.get("timeout", 30000))
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")

        page = self._get_page()

        try:
            if locator_type and element:
                # 在指定element中等待text
                locator = self._get_locator(locator_type, element)
                expect(locator).to_contain_text(expected_text, timeout=timeout)
            else:
                # 在整个页面中等待text
                page.wait_for_selector(f"text={expected_text}", timeout=timeout)

            print(f"text已出现: {expected_text}")
        except (PlaywrightTimeoutError, AssertionError) as e:
            self._take_screenshot_on_error(f"等待text出现超时_{expected_text}")
            raise PlaywrightTimeoutError(f"等待text出现超时: {expected_text}") from e

    @allure.step("等待页面加载")
    def wait_for_page_load(self, **kwargs):
        """
        等待页面加载完成
        
        参数:
            wait_until: load/domcontentloaded/networkidle
            timeout: 超时时间（毫秒）
        """
        kwargs.pop("关键字", None)
        wait_until = kwargs.get("wait_until", "load")
        timeout = int(kwargs.get("timeout", 30000))

        page = self._get_page()

        try:
            page.wait_for_load_state(wait_until, timeout=timeout)
            print(f"页面加载完成: {wait_until}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待页面加载超时_{wait_until}")
            raise PlaywrightTimeoutError(f"等待页面加载超时: {wait_until}") from e

    # ==================== 多窗口/标签页操作 ====================

    @allure.step("打开新标签页")
    def open_new_tab(self, **kwargs) -> None:
        """
        打开新标签页
        
        参数:
            url: 新标签页 URL（可选）
        """
        kwargs.pop("关键字", None)
        url = kwargs.get("url")
        
        context = PlaywrightManager.get_context()
        new_page = context.new_page()
        
        if url:
            new_page.goto(url)
        
        # 保存新页面到上下文
        pages = g_context().get_dict("all_pages") or []
        pages.append(new_page)
        g_context().set_dict("all_pages", pages)
        g_context().set_dict("current_page", new_page)
        
        print(f"已打开新标签页，当前共 {len(pages)} 个标签页")

    @allure.step("切换到标签页: {index}")
    def switch_to_tab(self, **kwargs) -> None:
        """
        切换到指定标签页
        
        参数:
            index: 标签页索引（从 0 开始）
        """
        kwargs.pop("关键字", None)
        index = int(kwargs.get("index", 0))
        
        pages = g_context().get_dict("all_pages") or []
        if not pages:
            context = PlaywrightManager.get_context()
            pages = context.pages
            g_context().set_dict("all_pages", pages)
        
        if index < 0 or index >= len(pages):
            raise ValueError(f"标签页索引超出范围: {index}，当前共 {len(pages)} 个标签页")
        
        target_page = pages[index]
        g_context().set_dict("current_page", target_page)
        target_page.bring_to_front()
        
        print(f"已切换到标签页 {index}")

    @allure.step("关闭当前标签页")
    def close_current_tab(self, **kwargs) -> None:
        """关闭当前标签页"""
        kwargs.pop("关键字", None)
        
        page = self._get_page()
        pages = g_context().get_dict("all_pages") or []
        
        if page in pages:
            pages.remove(page)
        
        page.close()
        
        # 切换到最后一个标签页
        if pages:
            g_context().set_dict("current_page", pages[-1])
            g_context().set_dict("all_pages", pages)
        else:
            g_context().set_dict("current_page", None)
        
        print(f"已关闭当前标签页，剩余 {len(pages)} 个标签页")

    @allure.step("获取所有标签页数量")
    def get_tab_count(self, **kwargs) -> int:
        """
        获取所有标签页数量
        
        参数:
            variable_name: 存储变量名（可选）
        """
        kwargs.pop("关键字", None)
        variable_name = kwargs.get("variable_name")
        
        context = PlaywrightManager.get_context()
        count = len(context.pages)
        
        if variable_name:
            g_context().set_dict(variable_name, count)
            print(f"标签页数量已保存到变量: {variable_name} = {count}")
        else:
            print(f"当前标签页数量: {count}")
        
        return count

    # ==================== Cookie 操作 ====================

    @allure.step("设置 Cookie")
    def set_cookie(self, **kwargs) -> None:
        """
        设置 Cookie
        
        参数:
            name: Cookie 名称
            value: Cookie 值
            domain: 域名（可选）
            path: 路径（可选，默认 /）
        """
        kwargs.pop("关键字", None)
        
        name = kwargs.get("name")
        value = kwargs.get("value")
        domain = kwargs.get("domain")
        path = kwargs.get("path", "/")
        
        page = self._get_page()
        context = page.context
        
        cookie = {
            "name": name,
            "value": value,
            "path": path,
            "url": page.url if not domain else None
        }
        if domain:
            cookie["domain"] = domain
        
        context.add_cookies([cookie])
        print(f"已设置 Cookie: {name}={value}")

    @allure.step("获取 Cookie")
    def get_cookie(self, **kwargs) -> Optional[str]:
        """
        获取 Cookie
        
        参数:
            name: Cookie 名称
            variable_name: 存储变量名（可选）
        """
        kwargs.pop("关键字", None)
        
        name = kwargs.get("name")
        variable_name = kwargs.get("variable_name")
        
        page = self._get_page()
        context = page.context
        cookies = context.cookies()
        
        value = None
        for cookie in cookies:
            if cookie["name"] == name:
                value = cookie["value"]
                break
        
        if variable_name:
            g_context().set_dict(variable_name, value)
            print(f"Cookie 已保存到变量: {variable_name} = {value}")
        else:
            print(f"Cookie {name} = {value}")
        
        return value

    @allure.step("删除 Cookie")
    def delete_cookie(self, **kwargs) -> None:
        """
        删除 Cookie
        
        参数:
            name: Cookie 名称（可选，不传则删除所有）
        """
        kwargs.pop("关键字", None)
        
        name = kwargs.get("name")
        page = self._get_page()
        context = page.context
        
        if name:
            cookies = context.cookies()
            remaining = [c for c in cookies if c["name"] != name]
            context.clear_cookies()
            if remaining:
                context.add_cookies(remaining)
            print(f"已删除 Cookie: {name}")
        else:
            context.clear_cookies()
            print("已删除所有 Cookie")

    # ==================== LocalStorage 操作 ====================

    @allure.step("设置 LocalStorage")
    def set_local_storage(self, **kwargs) -> None:
        """
        设置 LocalStorage
        
        参数:
            key: 键名
            value: 值
        """
        kwargs.pop("关键字", None)
        
        key = kwargs.get("key")
        value = kwargs.get("value")
        
        page = self._get_page()
        page.evaluate(f"localStorage.setItem('{key}', '{value}')")
        print(f"已设置 LocalStorage: {key}={value}")

    @allure.step("获取 LocalStorage")
    def get_local_storage(self, **kwargs) -> Optional[str]:
        """
        获取 LocalStorage
        
        参数:
            key: 键名
            variable_name: 存储变量名（可选）
        """
        kwargs.pop("关键字", None)
        
        key = kwargs.get("key")
        variable_name = kwargs.get("variable_name")
        
        page = self._get_page()
        value = page.evaluate(f"localStorage.getItem('{key}')")
        
        if variable_name:
            g_context().set_dict(variable_name, value)
            print(f"LocalStorage 已保存到变量: {variable_name} = {value}")
        else:
            print(f"LocalStorage {key} = {value}")
        
        return value

    @allure.step("删除 LocalStorage")
    def delete_local_storage(self, **kwargs) -> None:
        """
        删除 LocalStorage
        
        参数:
            key: 键名（可选，不传则清空所有）
        """
        kwargs.pop("关键字", None)
        
        key = kwargs.get("key")
        page = self._get_page()
        
        if key:
            page.evaluate(f"localStorage.removeItem('{key}')")
            print(f"已删除 LocalStorage: {key}")
        else:
            page.evaluate("localStorage.clear()")
            print("已清空所有 LocalStorage")

    # ==================== 文件下载验证 ====================

    @allure.step("等待文件下载")
    def wait_for_download(self, **kwargs) -> str:
        """
        等待文件下载完成
        
        参数:
            locator_type: 触发下载的元素定位方式
            element: 元素标识
            save_path: 保存路径（可选）
            variable_name: 存储下载路径的变量名（可选）
        """
        kwargs.pop("关键字", None)
        
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        save_path = kwargs.get("save_path")
        variable_name = kwargs.get("variable_name")
        
        page = self._get_page()
        
        with page.expect_download() as download_info:
            if locator_type and element:
                locator = self._get_locator(locator_type, element)
                locator.click()
            else:
                raise ValueError("需要指定触发下载的元素")
        
        download = download_info.value
        
        if save_path:
            download.save_as(save_path)
            file_path = save_path
        else:
            file_path = download.path()
        
        if variable_name:
            g_context().set_dict(variable_name, file_path)
            print(f"下载路径已保存到变量: {variable_name} = {file_path}")
        else:
            print(f"文件已下载: {file_path}")
        
        return file_path

    @allure.step("断言文件已下载")
    def assert_file_downloaded(self, **kwargs) -> None:
        """
        断言文件已下载
        
        参数:
            file_path: 文件路径
            expected_size: 期望的最小文件大小（字节，可选）
        """
        kwargs.pop("关键字", None)
        
        file_path = kwargs.get("file_path")
        expected_size = kwargs.get("expected_size")
        
        if not os.path.exists(file_path):
            raise AssertionError(f"文件不存在: {file_path}")
        
        actual_size = os.path.getsize(file_path)
        
        if expected_size and actual_size < int(expected_size):
            raise AssertionError(f"文件大小不符: 期望 >= {expected_size} 字节, 实际 {actual_size} 字节")
        
        print(f"文件下载断言成功: {file_path} ({actual_size} 字节)")





