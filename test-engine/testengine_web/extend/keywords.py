"""
Web 自动化测试关键字
基于 Playwright 实现，提供现代化的 Web 自动化测试能力
"""
import os
import time

import allure
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

from ..core.globalContext import g_context  # 相对导入: webrun内部模块
from ..utils.PlaywrightManager import PlaywrightManager  # 相对导入: webrun内部模块


class Keywords:
    """Web 自动化测试关键字类 - Playwright 版本"""

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
        """等待页面加载完成"""
        kwargs.pop("关键字", None)

        wait_until = kwargs.get("wait_until", "load")  # load, domcontentloaded, networkidle
        timeout = int(kwargs.get("timeout", 30000))

        page = self._get_page()

        try:
            if wait_until == "networkidle":
                page.wait_for_load_state("networkidle", timeout=timeout)
            elif wait_until == "domcontentloaded":
                page.wait_for_load_state("domcontentloaded", timeout=timeout)
            else:  # load
                page.wait_for_load_state("load", timeout=timeout)

            print(f"页面加载完成: {wait_until}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待页面加载超时_{wait_until}")
            raise PlaywrightTimeoutError(f"等待页面加载超时: {wait_until}") from e

    # ==================== AI 驱动操作 ====================

    def _ai_click(self, bbox):
        """
        根据边界框坐标点击element中心（Playwright 适配版）
        
        :param bbox: 边界框坐标 [xmin, ymin, xmax, ymax]
        """
        # 计算中心点坐标
        x_coordinate = (bbox[0] + bbox[2]) / 2
        y_coordinate = (bbox[1] + bbox[3]) / 2
        print(f"element中心点坐标信息: {x_coordinate}, {y_coordinate}")
        
        page = self._get_page()
        # Playwright 坐标点击
        page.mouse.click(x_coordinate, y_coordinate)

    def _ai_input(self, bbox, text):
        """
        点击并在element位置输入text（Playwright 适配版）
        
        :param bbox: 边界框坐标 [xmin, ymin, xmax, ymax]
        :param text: 要输入的text
        """
        self._ai_click(bbox)
        # Playwright 输入text
        page = self._get_page()
        page.keyboard.type(text)

    def _ai_extract_text(self, text):
        """
        将提取的text保存到全局上下文
        
        :param text: 提取的text内容
        """
        g_context().set_dict("ai_extracted_text", text)
        print(f"已提取text到全局变量 ai_extracted_text: {text}")

    def _load_ai_config(self):
        """加载AI配置文件"""
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), "ai_config.yaml")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠ 加载AI配置失败，使用默认配置: {e}")
            return {
                "AI_PROVIDER": "qwen-vl",
                "QWEN_VL": {
                    "API_KEY": "sk-aeb8d69039b14320b0fe58cb8285d8b1",
                    "BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "MODEL": "qwen-vl-max-latest",
                    "MIN_PIXELS": 401408,
                    "MAX_PIXELS": 1605632,
                    "FACTOR": 28,
                    "RETRY_COUNT": 2,
                    "TIMEOUT": 60
                },
                "AI_ENABLED": True,
                "AI_FALLBACK_TO_TRADITIONAL": True
            }

    def _call_ai_vision(self, user_description, actions):
        """
        调用 AI VL 模型进行截图分析（支持多模型配置）
        
        :param user_description: 用户的operation_desc
        :param actions: 支持的操作类型列表
        :return: AI 返回的结果字典
        """
        import base64
        import json
        import os
        import re
        import uuid
        
        # 延迟导入并添加详细错误处理
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError(
                "AI 功能需要 openai 包，请运行: pip install openai\n"
                f"详细错误: {e}"
            )
        except TypeError as e:
            # 处理 importlib_metadata 的问题
            raise RuntimeError(
                "导入 openai 包时遇到环境问题，可能是 Python 环境配置错误。\n"
                "建议解决方案：\n"
                "1. 重新安装 openai: pip uninstall openai && pip install openai\n"
                "2. 更新 importlib-metadata: pip install --upgrade importlib-metadata\n"
                "3. 检查虚拟环境是否正常\n"
                f"详细错误: {e}"
            )
        except Exception as e:
            raise RuntimeError(f"导入 openai 包失败: {e}")
        
        try:
            from PIL import Image
        except ImportError:
            raise RuntimeError("AI 功能需要 Pillow 包，请运行: pip install Pillow")
        
        try:
            from qwen_vl_utils import smart_resize
        except ImportError:
            raise RuntimeError("AI 功能需要 qwen-vl-utils 包，请运行: pip install qwen-vl-utils")

        # 加载配置
        config = self._load_ai_config()
        
        # 检查AI功能是否启用
        if not config.get("AI_ENABLED", True):
            raise RuntimeError("AI 功能已禁用，请在 ai_config.yaml 中启用")
        
        # 获取当前使用的AI提供商配置
        provider = config.get("AI_PROVIDER", "qwen-vl").upper().replace("-", "_")
        provider_config = config.get(provider, config.get("QWEN_VL"))
        
        # 初始化 OpenAI 客户端
        ai_client = OpenAI(
            api_key=provider_config.get("API_KEY"),
            base_url=provider_config.get("BASE_URL"),
        )

        # 优化后的提示词模板（避免触发内容审核）
        prompt = """
# 任务
在网页截图中定位UI组件。

# 输出
```json
{{
  "bbox": [x1, y1, x2, y2],
  "action": "{actions}",
  "text": "组件内容",
  "errors"?: "定位失败原因"
}}
```

# 步骤
1. 分析截图中的UI组件
2. 根据描述定位目标组件
3. 返回组件的边界框坐标

# 目标组件
{user_text}
"""

        ai_prompt = prompt.format(
            user_text=user_description,
            actions=", ".join(actions)
        )

        # Playwright 截图并转换为 base64
        page = self._get_page()
        screenshot_bytes = page.screenshot(type='png')
        image_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

        # 保存临时截图文件
        image_path = os.path.join(
            os.path.dirname(__file__),
            f"{str(uuid.uuid4()).replace('-', '')}.png"
        )
        with open(image_path, 'wb') as f:
            f.write(screenshot_bytes)

        # 获取图片尺寸
        width, height = Image.open(image_path).size
        print(f"截图尺寸：{width}, {height}")

        # 从配置读取图片处理参数
        min_pixels = provider_config.get("MIN_PIXELS", 401408)
        max_pixels = provider_config.get("MAX_PIXELS", 1605632)
        factor = provider_config.get("FACTOR", 28)
        
        # 自适应调整：当截图超大时自动调整 factor
        total_pixels = width * height
        if total_pixels > 10_000_000:
            factor = max(14, factor // 2)
            print(f"⚠ 超大截图({total_pixels}px)，调整factor={factor}")
        
        input_height, input_width = smart_resize(
            height, width,
            factor=factor,
            min_pixels=min_pixels,
            max_pixels=max_pixels
        )
        print(f"输入尺寸：{input_height}, {input_width} (factor={factor})")

        # 删除临时图片
        os.remove(image_path)

        if config.get("DEBUG", {}).get("VERBOSE", False):
            print(f'AI提示词: {ai_prompt}')

        # 调用 AI 模型（带重试）
        retry_count = provider_config.get("RETRY_COUNT", 2)
        last_error = None
        
        for attempt in range(retry_count + 1):
            try:
                completion = ai_client.chat.completions.create(
                    model=provider_config.get("MODEL"),
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "min_pixels": min_pixels,
                                "max_pixels": max_pixels,
                                "image_url": {"url": f"data:image/png;base64,{image_base64}"}
                            },
                            {
                                "type": "text",
                                "text": ai_prompt
                            }
                        ]
                    }],
                    timeout=provider_config.get("TIMEOUT", 60)
                )
                
                if config.get("DEBUG", {}).get("PRINT_AI_RESPONSE", False):
                    print("AI执行结果：", completion.model_dump_json())
                
                # 解析 AI 返回的 JSON 内容
                ai_response = json.loads(completion.model_dump_json())['choices'][0]['message']['content']
                pattern = r'```json\n(.*?)```'
                match = re.search(pattern, ai_response, re.DOTALL)
                
                if not match:
                    raise ValueError(f"AI 返回内容格式错误: {ai_response}")
                
                json_content = match.group(1)
                result = json.loads(json_content)
                print("AI识别结果：", result)

                # Windows 平台坐标缩放
                if os.name == 'nt':
                    bbox = result['bbox']
                    result['bbox'] = [
                        bbox[0] / input_width * width,
                        bbox[1] / input_height * height,
                        bbox[2] / input_width * width,
                        bbox[3] / input_height * height
                    ]
                    print(f"坐标缩放后：{result['bbox']}")

                # 检查错误
                if 'errors' in result and result['errors']:
                    raise AssertionError(f"AI 无法完成操作: {result['errors']}")

                return result
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                # 检查是否是内容审核错误
                if "data_inspection_failed" in error_msg or "inappropriate content" in error_msg.lower():
                    print(f"⚠ AI内容审核失败 (尝试 {attempt + 1}/{retry_count + 1})")
                    if attempt < retry_count:
                        print("  提示：可在 ai_config.yaml 中切换到 DeepSeek 等其他模型")
                        continue
                elif attempt < retry_count:
                    print(f"⚠ AI调用失败 (尝试 {attempt + 1}/{retry_count + 1}): {error_msg}")
                    continue
                
        # 所有重试都失败
        print(f"✖ AI调用失败: {last_error}")
        if config.get("AI_FALLBACK_TO_TRADITIONAL", True):
            print("  建议：请使用传统定位方式（如 CSS选择器、XPath）代替AI定位")
        raise last_error

    @allure.step("AI操作: {operation_desc}")
    def ai_operation(self, **kwargs):
        """
        AI 驱动的主操作调度器
        
        参数:
            operation_desc: 自然语言描述的操作，如"点击登录按钮"、"在用户名输入框输入admin"
        
        示例:
            - operation_desc: "点击红色的提交按钮"
            - operation_desc: "在密码框输入123456"
            - operation_desc: "提取页面标题text"
        """
        kwargs.pop("关键字", None)
        operation_desc = kwargs.get("operation_desc")
        
        if not operation_desc:
            raise ValueError("operation_desc不能为空")

        # 支持的操作类型
        actions = ['点击', '输入', 'text提取', '滚动', '悬停', '拖拽']
        
        try:
            # 调用 AI 视觉分析
            result = self._call_ai_vision(operation_desc, actions)
            
            # 根据操作类型执行相应操作
            action = result.get('action')
            bbox = result.get('bbox')
            text = result.get('text', '')
            
            page = self._get_page()
            
            if action == '点击':
                self._ai_click(bbox)
                print(f"✓ AI操作成功: 点击element")
            elif action == '输入':
                self._ai_input(bbox, text)
                print(f"✓ AI操作成功: 输入text '{text}'")
            elif action == 'text提取':
                self._ai_extract_text(text)
                print(f"✓ AI操作成功: 提取text '{text}'")
            elif action == '滚动':
                x = (bbox[0] + bbox[2]) / 2
                y = (bbox[1] + bbox[3]) / 2
                page.evaluate(f"window.scrollTo({x}, {y})")
                print(f"✓ AI操作成功: 滚动到element")
            elif action == '悬停':
                x = (bbox[0] + bbox[2]) / 2
                y = (bbox[1] + bbox[3]) / 2
                page.mouse.move(x, y)
                print(f"✓ AI操作成功: 鼠标悬停")
            elif action == '拖拽':
                # 拖拽需要两个element，这里简化处理
                raise NotImplementedError("拖拽操作需要使用 ai_drag 方法")
            else:
                raise ValueError(f"不支持的操作类型: {action}")
                
        except Exception as e:
            self._take_screenshot_on_error(f"AI操作失败_{operation_desc}")
            raise e

    @allure.step("AI点击: {element_desc}")
    def ai_click(self, **kwargs):
        """
        AI 驱动的点击操作
        
        参数:
            element描述: element的自然语言描述，如"红色的提交按钮"、"登录链接"
        """
        kwargs.pop("关键字", None)
        element_desc = kwargs.get("element_desc")
        
        if not element_desc:
            raise ValueError("element描述不能为空")
        
        operation_desc = f"点击{element_desc}"
        self.ai_operation(operation_desc=operation_desc)

    @allure.step("AI输入: {text}")
    def ai_input(self, **kwargs):
        """
        AI 驱动的输入操作
        
        参数:
            element描述: 输入框的自然语言描述，如"用户名输入框"、"搜索框"
            text: 要输入的text内容
        """
        kwargs.pop("关键字", None)
        element_desc = kwargs.get("element_desc")
        text = kwargs.get("text", "")
        
        if not element_desc:
            raise ValueError("element描述不能为空")
        
        operation_desc = f"在{element_desc}输入{text}"
        
        try:
            actions = ['输入']
            result = self._call_ai_vision(operation_desc, actions)
            self._ai_input(result['bbox'], text)
            print(f"✓ AI输入成功: 在{element_desc}输入 '{text}'")
        except Exception as e:
            self._take_screenshot_on_error(f"AI输入失败_{element_desc}")
            raise e

    @allure.step("AI提取text: {text_desc}")
    def ai_extract_text(self, **kwargs):
        """
        AI 驱动的text提取
        
        参数:
            text_desc: 要提取text的描述，如"页面标题"、"错误提示信息"
            variable_name: 保存到的variable_name（可选，默认保存到 ai_extracted_text）
        """
        kwargs.pop("关键字", None)
        text_desc = kwargs.get("text_desc")
        variable_name = kwargs.get("variable_name", "ai_extracted_text")
        
        if not text_desc:
            raise ValueError("text_desc不能为空")
        
        operation_desc = f"提取{text_desc}的text内容"
        
        try:
            actions = ['text提取']
            result = self._call_ai_vision(operation_desc, actions)
            text = result.get('text', '')
            g_context().set_dict(variable_name, text)
            print(f"✓ AItext提取成功: 已提取 '{text}' 并保存到变量 {variable_name}")
        except Exception as e:
            self._take_screenshot_on_error(f"AItext提取失败_{text_desc}")
            raise e

    @allure.step("AI滚动: {element_desc}")
    def ai_scroll(self, **kwargs):
        """
        AI 驱动的滚动操作
        
        参数:
            element描述: 要滚动到的element描述，如"页面底部"、"评论区"
        """
        kwargs.pop("关键字", None)
        element_desc = kwargs.get("element_desc")
        
        if not element_desc:
            raise ValueError("element描述不能为空")
        
        operation_desc = f"滚动到{element_desc}"
        
        try:
            actions = ['滚动']
            result = self._call_ai_vision(operation_desc, actions)
            bbox = result['bbox']
            
            page = self._get_page()
            x = (bbox[0] + bbox[2]) / 2
            y = (bbox[1] + bbox[3]) / 2
            page.evaluate(f"window.scrollTo({x}, {y})")
            print(f"✓ AI滚动成功: 滚动到{element_desc}")
        except Exception as e:
            self._take_screenshot_on_error(f"AI滚动失败_{element_desc}")
            raise e

    @allure.step("AI悬停: {element_desc}")
    def ai_hover(self, **kwargs):
        """
        AI 驱动的鼠标悬停操作
        
        参数:
            element描述: 要悬停的element描述，如"用户菜单"、"导航栏"
        """
        kwargs.pop("关键字", None)
        element_desc = kwargs.get("element_desc")
        
        if not element_desc:
            raise ValueError("element描述不能为空")
        
        operation_desc = f"鼠标悬停在{element_desc}"
        
        try:
            actions = ['悬停']
            result = self._call_ai_vision(operation_desc, actions)
            bbox = result['bbox']
            
            page = self._get_page()
            x = (bbox[0] + bbox[2]) / 2
            y = (bbox[1] + bbox[3]) / 2
            page.mouse.move(x, y)
            print(f"✓ AI悬停成功: 鼠标悬停在{element_desc}")
        except Exception as e:
            self._take_screenshot_on_error(f"AI悬停失败_{element_desc}")
            raise e

    @allure.step("AI拖拽: {source_element_desc} -> {target_element_desc}")
    def ai_drag(self, **kwargs):
        """
        AI 驱动的拖拽操作
        
        参数:
            源element描述: 要拖拽的element描述，如"待办事项"
            目标element描述: 拖拽目标的描述，如"已完成区域"
        """
        kwargs.pop("关键字", None)
        source_element_desc = kwargs.get("source_element_desc")
        target_element_desc = kwargs.get("target_element_desc")
        
        if not source_element_desc or not target_element_desc:
            raise ValueError("源element描述和目标element描述不能为空")
        
        try:
            # 先找到源element
            operation_desc1 = f"找到{source_element_desc}"
            actions = ['拖拽']
            result1 = self._call_ai_vision(operation_desc1, actions)
            source_bbox = result1['bbox']
            source_x = (source_bbox[0] + source_bbox[2]) / 2
            source_y = (source_bbox[1] + source_bbox[3]) / 2
            
            # 再找到目标element
            operation_desc2 = f"找到{target_element_desc}"
            result2 = self._call_ai_vision(operation_desc2, actions)
            target_bbox = result2['bbox']
            target_x = (target_bbox[0] + target_bbox[2]) / 2
            target_y = (target_bbox[1] + target_bbox[3]) / 2
            
            # 执行拖拽 (Playwright 方式)
            page = self._get_page()
            page.mouse.move(source_x, source_y)
            page.mouse.down()
            page.mouse.move(target_x, target_y)
            page.mouse.up()
            
            print(f"✓ AI拖拽成功: {source_element_desc} -> {target_element_desc}")
        except Exception as e:
            self._take_screenshot_on_error(f"AI拖拽失败_{source_element_desc}_to_{target_element_desc}")
            raise e

    @allure.step("AI断言可见: {element_desc}")
    def ai_assert_visible(self, **kwargs):
        """
        AI 驱动的可见性断言
        
        参数:
            element描述: 要断言可见的element描述，如"成功提示消息"、"登录按钮"
        """
        kwargs.pop("关键字", None)
        element_desc = kwargs.get("element_desc")
        
        if not element_desc:
            raise ValueError("element描述不能为空")
        
        operation_desc = f"找到{element_desc}"
        
        try:
            actions = ['点击']  # 使用点击操作来定位element
            result = self._call_ai_vision(operation_desc, actions)
            
            # 如果 AI 能找到element，说明element可见
            if result.get('bbox'):
                print(f"✓ AI断言成功: {element_desc} 可见")
            else:
                raise AssertionError(f"AI断言失败: {element_desc} 不可见")
        except Exception as e:
            self._take_screenshot_on_error(f"AI断言失败_{element_desc}")
            raise AssertionError(f"AI断言失败: {element_desc} 不可见") from e

    # ============ 旧关键字兼容方法 - 向后兼容 ============
    
    def input_context(self, **kwargs):
        """
        旧版关键字兼容: input_context -> input_text
        
        旧参数映射:
            定位方式 -> locator_type
            目标对象 -> element
            数据内容 -> text
        """
        kwargs.pop("关键字", None)
        locator_type = kwargs.get("定位方式", kwargs.get("locator_type"))
        element = kwargs.get("目标对象", kwargs.get("element"))
        text = kwargs.get("数据内容", kwargs.get("text"))
        
        # 调用新的 input_text 方法
        return self.input_text(locator_type=locator_type, element=element, text=text)
    
    def option_click(self, **kwargs):
        """
        旧版关键字兼容: option_click -> click_element
        
        旧参数映射:
            定位方式 -> locator_type
            目标对象 -> element
        """
        kwargs.pop("关键字", None)
        locator_type = kwargs.get("定位方式", kwargs.get("locator_type"))
        element = kwargs.get("目标对象", kwargs.get("element"))
        
        # 调用新的 click_element 方法
        return self.click_element(locator_type=locator_type, element=element)
    
    def wait_sleep(self, **kwargs):
        """
        旧版关键字兼容: wait_sleep -> sleep
        
        旧参数映射:
            数据内容 -> time
        """
        kwargs.pop("关键字", None)
        time_value = kwargs.get("数据内容", kwargs.get("time"))
        
        if time_value:
            time_value = float(time_value)
        
        # 调用新的 sleep 方法
        return self.sleep(time=time_value)
    
    def assert_browser_title(self, **kwargs):
        """
        旧版关键字兼容: assert_browser_title -> assert_title_equals
        
        旧参数映射:
            数据内容 -> expected_title
        """
        kwargs.pop("关键字", None)
        expected_title = kwargs.get("数据内容", kwargs.get("expected_title"))
        
        # 调用新的 assert_title_equals 方法
        return self.assert_title_equals(expected_title=expected_title)





