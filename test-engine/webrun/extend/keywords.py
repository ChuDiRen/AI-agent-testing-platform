"""
Web 自动化测试关键字
基于 Playwright 实现，提供现代化的 Web 自动化测试能力
"""
import os
import time
import allure
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

from webrun.core.globalContext import g_context
from webrun.utils.PlaywrightManager import PlaywrightManager


class Keywords:
    """Web 自动化测试关键字类 - Playwright 版本"""

    def _get_page(self):
        """获取当前页面实例"""
        page = g_context().get_dict("current_page")
        if page is None:
            raise RuntimeError("浏览器页面未初始化，请先使用 open_browser 关键字打开浏览器")
        return page

    def _get_locator(self, 定位方式, 元素):
        """
        获取 Playwright 定位器
        
        :param 定位方式: 定位方式字符串
        :param 元素: 元素标识
        :return: Playwright Locator
        """
        page = self._get_page()
        定位方式 = 定位方式.lower()
        
        # Playwright 现代定位方式
        if 定位方式 == "role":
            # 按角色定位：支持多种格式
            # 格式1: button[name="百度一下"]
            # 格式2: button,name=Submit
            # 格式3: button
            if "[name=" in 元素:
                # 格式1: button[name="百度一下"]
                import re
                match = re.match(r'(\w+)\[name="([^"]+)"\]', 元素)
                if match:
                    role, name = match.groups()
                    return page.get_by_role(role, name=name)
            elif "," in 元素:
                # 格式2: button,name=Submit
                role, name_part = 元素.split(",", 1)
                if name_part.startswith("name="):
                    name = name_part[5:]
                    return page.get_by_role(role, name=name)
            # 格式3: button
            return page.get_by_role(元素)
        elif 定位方式 == "text":
            return page.get_by_text(元素)
        elif 定位方式 == "label":
            return page.get_by_label(元素)
        elif 定位方式 == "placeholder":
            return page.get_by_placeholder(元素)
        elif 定位方式 == "test_id" or 定位方式 == "testid":
            return page.get_by_test_id(元素)
        elif 定位方式 == "alt":
            return page.get_by_alt_text(元素)
        elif 定位方式 == "title":
            return page.get_by_title(元素)
        # 传统定位方式
        elif 定位方式 == "id":
            return page.locator(f"#{元素}")
        elif 定位方式 == "name":
            return page.locator(f"[name='{元素}']")
        elif 定位方式 == "class" or 定位方式 == "class_name":
            return page.locator(f".{元素}")
        elif 定位方式 == "tag" or 定位方式 == "tag_name":
            return page.locator(元素)
        elif 定位方式 == "xpath":
            return page.locator(f"xpath={元素}")
        elif 定位方式 == "css" or 定位方式 == "css_selector":
            return page.locator(元素)
        else:
            raise ValueError(f"不支持的定位方式: {定位方式}")

    def _take_screenshot_on_error(self, filename_prefix="error"):
        """错误时自动截图"""
        try:
            page = self._get_page()
            timestamp = int(time.time())
            filename = f"{filename_prefix}_{timestamp}.png"
            screenshot_path = os.path.join("screenshots", filename)
            os.makedirs("screenshots", exist_ok=True)
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
            浏览器: chromium/firefox/webkit (默认 chromium)
            无头模式: true/false (默认 false)
            超时时间: 超时时间（毫秒，默认 30000）
            窗口大小: maximize/1920x1080/等 (默认 maximize)
            启用追踪: true/false (默认 false)
        """
        kwargs.pop("关键字", None)
        
        browser = kwargs.get("浏览器", "chromium")
        headless = str(kwargs.get("无头模式", "false")).lower() in ["true", "1", "yes"]
        timeout = int(kwargs.get("超时时间", 30000))
        window_size = kwargs.get("窗口大小", "maximize")
        enable_tracing = str(kwargs.get("启用追踪", "false")).lower() in ["true", "1", "yes"]
        
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
            等待条件: load/domcontentloaded/networkidle (默认 load)
            超时时间: 超时时间（毫秒，可选）
        """
        kwargs.pop("关键字", None)
        
        url = kwargs.get("url")
        wait_until = kwargs.get("等待条件", "load")
        timeout = kwargs.get("超时时间")
        
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

    @allure.step("点击元素: {定位方式}={元素}")
    def click_element(self, **kwargs):
        """
        点击元素
        
        参数:
            定位方式: id/name/xpath/css/role/text/label 等
            元素: 元素标识
            超时时间: 超时时间（毫秒，可选）
            强制点击: true/false (默认 false)
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = kwargs.get("超时时间")
        强制点击 = str(kwargs.get("强制点击", "false")).lower() in ["true", "1", "yes"]
        
        locator = self._get_locator(定位方式, 元素)
        
        try:
            if 超时时间:
                locator.click(timeout=int(超时时间), force=强制点击)
            else:
                locator.click(force=强制点击)
            print(f"已点击元素: {定位方式}={元素}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"点击超时_{定位方式}_{元素}")
            raise PlaywrightTimeoutError(f"点击元素超时: {定位方式}={元素}") from e

    @allure.step("输入文本: {文本}")
    def input_text(self, **kwargs):
        """
        输入文本到元素
        
        参数:
            定位方式: id/name/xpath/css/role/text/label 等
            元素: 元素标识
            文本: 要输入的文本
            清空: true/false (默认 true)
            超时时间: 超时时间（毫秒，可选）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        文本 = kwargs.get("文本", "")
        清空 = str(kwargs.get("清空", "true")).lower() in ["true", "1", "yes"]
        超时时间 = kwargs.get("超时时间")
        强制操作 = str(kwargs.get("强制操作", "false")).lower() in ["true", "1", "yes"]

        locator = self._get_locator(定位方式, 元素)

        try:
            # 如果元素隐藏，先尝试点击使其可见
            if 强制操作:
                try:
                    locator.click(force=True, timeout=1000)
                except:
                    pass

            if 清空:
                if 超时时间:
                    locator.fill(文本, timeout=int(超时时间), force=强制操作)
                else:
                    locator.fill(文本, force=强制操作)
            else:
                if 超时时间:
                    locator.type(文本, timeout=int(超时时间))
                else:
                    locator.type(文本)
            print(f"已输入文本: {文本} 到 {定位方式}={元素}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"输入文本超时_{定位方式}_{元素}")
            raise PlaywrightTimeoutError(f"输入文本超时: {定位方式}={元素}") from e

    @allure.step("等待页面加载完成")
    def wait_for_page_load(self, **kwargs):
        """等待页面加载完成"""
        kwargs.pop("关键字", None)
        
        等待条件 = kwargs.get("等待条件", "load")  # load/domcontentloaded/networkidle
        超时时间 = kwargs.get("超时时间", 30000)
        
        page = self._get_page()
        
        try:
            page.wait_for_load_state(等待条件, timeout=int(超时时间))
            print(f"页面加载完成: {等待条件}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error("等待页面加载超时")
            raise PlaywrightTimeoutError(f"等待页面加载超时: {等待条件}") from e

    @allure.step("断言页面标题: {期望标题}")
    def assert_title(self, **kwargs):
        """断言页面标题"""
        kwargs.pop("关键字", None)
        
        期望标题 = kwargs.get("期望标题")
        超时时间 = int(kwargs.get("超时时间", 5000))
        
        page = self._get_page()
        
        try:
            expect(page).to_have_title(期望标题, timeout=超时时间)
            print(f"断言成功: 页面标题为 '{期望标题}'")
        except AssertionError as e:
            actual_title = page.title()
            self._take_screenshot_on_error(f"断言页面标题失败_{期望标题}")
            raise AssertionError(f"断言失败: 期望标题 '{期望标题}'，实际标题 '{actual_title}'") from e

    @allure.step("断言文本包含: {期望文本}")
    def assert_text_contains(self, **kwargs):
        """断言元素文本包含指定内容"""
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        期望文本 = kwargs.get("期望文本")
        超时时间 = int(kwargs.get("超时时间", 5000))
        
        if 定位方式 and 元素:
            locator = self._get_locator(定位方式, 元素)
        else:
            # 如果没有指定元素，则检查整个页面
            page = self._get_page()
            locator = page.locator("body")
        
        try:
            expect(locator).to_contain_text(期望文本, timeout=超时时间)
            print(f"断言成功: 文本包含 '{期望文本}'")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言文本包含失败_{期望文本}")
            raise AssertionError(f"断言失败: 文本不包含 '{期望文本}'") from e

    @allure.step("截图")
    def take_screenshot(self, **kwargs):
        """截图"""
        kwargs.pop("关键字", None)
        
        文件名 = kwargs.get("文件名", f"screenshot_{int(time.time())}")
        全页面 = str(kwargs.get("全页面", "true")).lower() in ["true", "1", "yes"]
        
        page = self._get_page()
        
        # 确保文件名有扩展名
        if not 文件名.endswith('.png'):
            文件名 += '.png'
        
        # 创建截图目录
        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, 文件名)
        
        # 截图
        page.screenshot(path=screenshot_path, full_page=全页面)
        
        # 添加到 Allure 报告
        allure.attach.file(screenshot_path, name=f"截图_{文件名}", attachment_type=allure.attachment_type.PNG)
        
        print(f"截图已保存: {screenshot_path}")
        return screenshot_path

    @allure.step("断言页面标题等于: {期望标题}")
    def assert_title_equals(self, **kwargs):
        """断言页面标题等于指定内容"""
        kwargs.pop("关键字", None)

        期望标题 = kwargs.get("期望标题")
        超时时间 = int(kwargs.get("超时时间", 5000))

        page = self._get_page()

        try:
            expect(page).to_have_title(期望标题, timeout=超时时间)
            print(f"断言成功: 页面标题等于 '{期望标题}'")
        except AssertionError as e:
            actual_title = page.title()
            self._take_screenshot_on_error(f"断言页面标题等于失败_{期望标题}")
            raise AssertionError(f"断言失败: 期望标题 '{期望标题}'，实际标题 '{actual_title}'") from e

    @allure.step("断言页面标题包含: {期望文本}")
    def assert_title_contains(self, **kwargs):
        """断言页面标题包含指定文本"""
        kwargs.pop("关键字", None)

        期望文本 = kwargs.get("期望文本")
        超时时间 = int(kwargs.get("超时时间", 5000))

        page = self._get_page()

        try:
            # Playwright 没有直接的 title contains 断言，我们手动实现
            actual_title = page.title()
            if 期望文本 not in actual_title:
                raise AssertionError(f"断言失败: 页面标题 '{actual_title}' 不包含 '{期望文本}'")
            print(f"断言成功: 页面标题包含 '{期望文本}'")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言页面标题包含失败_{期望文本}")
            raise e

    @allure.step("获取元素属性: {属性名}")
    def get_attribute(self, **kwargs):
        """获取元素属性值"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        属性名 = kwargs.get("属性名")
        变量名 = kwargs.get("变量名")

        locator = self._get_locator(定位方式, 元素)

        try:
            属性值 = locator.get_attribute(属性名)
            print(f"获取属性成功: {定位方式}={元素} 的 {属性名} = {属性值}")

            # 如果指定了变量名，保存到全局上下文
            if 变量名:
                g_context().set_dict(变量名, 属性值)
                print(f"属性值已保存到变量: {变量名} = {属性值}")

            return 属性值
        except Exception as e:
            self._take_screenshot_on_error(f"获取属性失败_{定位方式}_{元素}_{属性名}")
            raise Exception(f"获取元素属性失败: {定位方式}={元素}, 属性={属性名}") from e

    @allure.step("等待: {时间}秒")
    def sleep(self, **kwargs):
        """等待指定时间"""
        kwargs.pop("关键字", None)

        时间 = float(kwargs.get("时间", 1))

        print(f"等待 {时间} 秒...")
        time.sleep(时间)
        print(f"等待完成")

    @allure.step("获取元素文本")
    def get_element_text(self, **kwargs):
        """获取元素文本内容"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        变量名 = kwargs.get("变量名")

        locator = self._get_locator(定位方式, 元素)

        try:
            文本内容 = locator.text_content()
            print(f"获取文本成功: {定位方式}={元素} 的文本 = {文本内容}")

            # 如果指定了变量名，保存到全局上下文
            if 变量名:
                g_context().set_dict(变量名, 文本内容)
                print(f"文本内容已保存到变量: {变量名} = {文本内容}")

            return 文本内容
        except Exception as e:
            self._take_screenshot_on_error(f"获取文本失败_{定位方式}_{元素}")
            raise Exception(f"获取元素文本失败: {定位方式}={元素}") from e

    @allure.step("等待元素可见: {定位方式}={元素}")
    def wait_for_element_visible(self, **kwargs):
        """等待元素可见"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 30000))

        locator = self._get_locator(定位方式, 元素)

        try:
            locator.wait_for(state="visible", timeout=超时时间)
            print(f"元素已可见: {定位方式}={元素}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待元素可见超时_{定位方式}_{元素}")
            raise PlaywrightTimeoutError(f"等待元素可见超时: {定位方式}={元素}") from e

    @allure.step("等待元素隐藏: {定位方式}={元素}")
    def wait_for_element_hidden(self, **kwargs):
        """等待元素隐藏"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 30000))

        locator = self._get_locator(定位方式, 元素)

        try:
            locator.wait_for(state="hidden", timeout=超时时间)
            print(f"元素已隐藏: {定位方式}={元素}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待元素隐藏超时_{定位方式}_{元素}")
            raise PlaywrightTimeoutError(f"等待元素隐藏超时: {定位方式}={元素}") from e

    @allure.step("获取当前URL")
    def get_current_url(self, **kwargs):
        """获取当前页面URL"""
        kwargs.pop("关键字", None)

        变量名 = kwargs.get("变量名")

        page = self._get_page()

        try:
            当前URL = page.url
            print(f"获取当前URL成功: {当前URL}")

            # 如果指定了变量名，保存到全局上下文
            if 变量名:
                g_context().set_dict(变量名, 当前URL)
                print(f"URL已保存到变量: {变量名} = {当前URL}")

            return 当前URL
        except Exception as e:
            self._take_screenshot_on_error("获取当前URL失败")
            raise Exception("获取当前URL失败") from e

    @allure.step("选择下拉框选项")
    def select_dropdown(self, **kwargs):
        """选择下拉框选项"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        选择方式 = kwargs.get("选择方式", "value")  # value/text/index
        选项值 = kwargs.get("选项值")

        locator = self._get_locator(定位方式, 元素)

        try:
            if 选择方式 == "value":
                locator.select_option(value=选项值)
            elif 选择方式 == "text":
                locator.select_option(label=选项值)
            elif 选择方式 == "index":
                locator.select_option(index=int(选项值))
            else:
                raise ValueError(f"不支持的选择方式: {选择方式}")

            print(f"选择下拉框成功: {定位方式}={元素}, {选择方式}={选项值}")
        except Exception as e:
            self._take_screenshot_on_error(f"选择下拉框失败_{定位方式}_{元素}")
            raise Exception(f"选择下拉框失败: {定位方式}={元素}, {选择方式}={选项值}") from e

    @allure.step("断言元素可见: {定位方式}={元素}")
    def assert_element_visible(self, **kwargs):
        """断言元素可见"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 5000))

        locator = self._get_locator(定位方式, 元素)

        try:
            expect(locator).to_be_visible(timeout=超时时间)
            print(f"断言成功: 元素可见 {定位方式}={元素}")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言元素可见失败_{定位方式}_{元素}")
            raise AssertionError(f"断言失败: 元素不可见 {定位方式}={元素}") from e

    @allure.step("断言元素存在: {定位方式}={元素}")
    def assert_element_exists(self, **kwargs):
        """断言元素存在"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 5000))

        locator = self._get_locator(定位方式, 元素)

        try:
            expect(locator).to_be_attached(timeout=超时时间)
            print(f"断言成功: 元素存在 {定位方式}={元素}")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言元素存在失败_{定位方式}_{元素}")
            raise AssertionError(f"断言失败: 元素不存在 {定位方式}={元素}") from e

    @allure.step("双击元素: {定位方式}={元素}")
    def double_click_element(self, **kwargs):
        """双击元素"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = kwargs.get("超时时间")

        locator = self._get_locator(定位方式, 元素)

        try:
            if 超时时间:
                locator.dblclick(timeout=int(超时时间))
            else:
                locator.dblclick()
            print(f"已双击元素: {定位方式}={元素}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"双击超时_{定位方式}_{元素}")
            raise PlaywrightTimeoutError(f"双击元素超时: {定位方式}={元素}") from e

    @allure.step("右键点击元素: {定位方式}={元素}")
    def right_click_element(self, **kwargs):
        """右键点击元素"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = kwargs.get("超时时间")

        locator = self._get_locator(定位方式, 元素)

        try:
            if 超时时间:
                locator.click(button="right", timeout=int(超时时间))
            else:
                locator.click(button="right")
            print(f"已右键点击元素: {定位方式}={元素}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"右键点击超时_{定位方式}_{元素}")
            raise PlaywrightTimeoutError(f"右键点击元素超时: {定位方式}={元素}") from e

    @allure.step("悬停元素: {定位方式}={元素}")
    def hover_element(self, **kwargs):
        """悬停在元素上"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = kwargs.get("超时时间")

        locator = self._get_locator(定位方式, 元素)

        try:
            if 超时时间:
                locator.hover(timeout=int(超时时间))
            else:
                locator.hover()
            print(f"已悬停元素: {定位方式}={元素}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"悬停超时_{定位方式}_{元素}")
            raise PlaywrightTimeoutError(f"悬停元素超时: {定位方式}={元素}") from e

    @allure.step("切换到iframe")
    def switch_to_frame(self, **kwargs):
        """切换到iframe"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")

        page = self._get_page()

        try:
            if 定位方式 and 元素:
                # 切换到指定的iframe
                frame_locator = self._get_locator(定位方式, 元素)
                frame = page.frame_locator(f"#{元素}" if 定位方式 == "id" else f"[{定位方式}='{元素}']")
                # 保存当前frame到上下文
                g_context().set_dict("current_frame", frame)
                print(f"已切换到iframe: {定位方式}={元素}")
            else:
                # 切换回主文档
                g_context().set_dict("current_frame", None)
                print("已切换回主文档")
        except Exception as e:
            self._take_screenshot_on_error(f"切换iframe失败_{定位方式}_{元素}")
            raise Exception(f"切换iframe失败: {定位方式}={元素}") from e

    @allure.step("执行JavaScript脚本")
    def execute_script(self, **kwargs):
        """执行JavaScript脚本"""
        kwargs.pop("关键字", None)

        脚本 = kwargs.get("脚本")
        变量名 = kwargs.get("变量名")

        page = self._get_page()

        try:
            结果 = page.evaluate(脚本)
            print(f"JavaScript执行成功: {脚本}")
            print(f"执行结果: {结果}")

            # 如果指定了变量名，保存到全局上下文
            if 变量名:
                g_context().set_dict(变量名, 结果)
                print(f"结果已保存到变量: {变量名} = {结果}")

            return 结果
        except Exception as e:
            self._take_screenshot_on_error("JavaScript执行失败")
            raise Exception(f"JavaScript执行失败: {脚本}") from e

    @allure.step("清空输入框")
    def clear_element(self, **kwargs):
        """清空输入框"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")

        locator = self._get_locator(定位方式, 元素)

        try:
            locator.clear()
            print(f"已清空输入框: {定位方式}={元素}")
        except Exception as e:
            self._take_screenshot_on_error(f"清空输入框失败_{定位方式}_{元素}")
            raise Exception(f"清空输入框失败: {定位方式}={元素}") from e

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

    @allure.step("等待元素存在: {定位方式}={元素}")
    def wait_for_element(self, **kwargs):
        """等待元素存在（attached）"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 30000))

        locator = self._get_locator(定位方式, 元素)

        try:
            locator.wait_for(state="attached", timeout=超时时间)
            print(f"元素已存在: {定位方式}={元素}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待元素存在超时_{定位方式}_{元素}")
            raise PlaywrightTimeoutError(f"等待元素存在超时: {定位方式}={元素}") from e

    @allure.step("等待元素可点击: {定位方式}={元素}")
    def wait_for_element_clickable(self, **kwargs):
        """等待元素可点击"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 30000))

        locator = self._get_locator(定位方式, 元素)

        try:
            # Playwright 中可点击意味着元素可见且启用
            locator.wait_for(state="visible", timeout=超时时间)
            expect(locator).to_be_enabled(timeout=超时时间)
            print(f"元素已可点击: {定位方式}={元素}")
        except (PlaywrightTimeoutError, AssertionError) as e:
            self._take_screenshot_on_error(f"等待元素可点击超时_{定位方式}_{元素}")
            raise PlaywrightTimeoutError(f"等待元素可点击超时: {定位方式}={元素}") from e

    @allure.step("滚动到元素: {定位方式}={元素}")
    def scroll_to_element(self, **kwargs):
        """滚动到元素"""
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")

        locator = self._get_locator(定位方式, 元素)

        try:
            locator.scroll_into_view_if_needed()
            print(f"已滚动到元素: {定位方式}={元素}")
        except Exception as e:
            self._take_screenshot_on_error(f"滚动到元素失败_{定位方式}_{元素}")
            raise Exception(f"滚动到元素失败: {定位方式}={元素}") from e

    @allure.step("等待文本出现: {期望文本}")
    def wait_for_text(self, **kwargs):
        """等待页面中出现指定文本"""
        kwargs.pop("关键字", None)

        期望文本 = kwargs.get("期望文本")
        超时时间 = int(kwargs.get("超时时间", 30000))
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")

        page = self._get_page()

        try:
            if 定位方式 and 元素:
                # 在指定元素中等待文本
                locator = self._get_locator(定位方式, 元素)
                expect(locator).to_contain_text(期望文本, timeout=超时时间)
            else:
                # 在整个页面中等待文本
                page.wait_for_selector(f"text={期望文本}", timeout=超时时间)

            print(f"文本已出现: {期望文本}")
        except (PlaywrightTimeoutError, AssertionError) as e:
            self._take_screenshot_on_error(f"等待文本出现超时_{期望文本}")
            raise PlaywrightTimeoutError(f"等待文本出现超时: {期望文本}") from e

    @allure.step("等待页面加载")
    def wait_for_page_load(self, **kwargs):
        """等待页面加载完成"""
        kwargs.pop("关键字", None)

        等待条件 = kwargs.get("等待条件", "load")  # load, domcontentloaded, networkidle
        超时时间 = int(kwargs.get("超时时间", 30000))

        page = self._get_page()

        try:
            if 等待条件 == "networkidle":
                page.wait_for_load_state("networkidle", timeout=超时时间)
            elif 等待条件 == "domcontentloaded":
                page.wait_for_load_state("domcontentloaded", timeout=超时时间)
            else:  # load
                page.wait_for_load_state("load", timeout=超时时间)

            print(f"页面加载完成: {等待条件}")
        except PlaywrightTimeoutError as e:
            self._take_screenshot_on_error(f"等待页面加载超时_{等待条件}")
            raise PlaywrightTimeoutError(f"等待页面加载超时: {等待条件}") from e
