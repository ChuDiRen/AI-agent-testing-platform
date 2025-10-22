"""
Web 自动化测试关键字
基于 Selenium WebDriver 实现
"""
import os
import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from webrun.core.globalContext import g_context
from webrun.utils.DriverManager import DriverManager


class Keywords:
    """Web 自动化测试关键字类"""

    # 定位方式映射
    LOCATOR_MAP = {
        "id": By.ID,
        "name": By.NAME,
        "class": By.CLASS_NAME,
        "class_name": By.CLASS_NAME,
        "tag": By.TAG_NAME,
        "tag_name": By.TAG_NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR,
        "css_selector": By.CSS_SELECTOR,
        "link": By.LINK_TEXT,
        "link_text": By.LINK_TEXT,
        "partial_link": By.PARTIAL_LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
    }

    def _get_driver(self):
        """获取当前 driver 实例"""
        driver = g_context().get_dict("current_driver")
        if driver is None:
            raise RuntimeError("浏览器未启动，请先使用 open_browser 关键字打开浏览器")
        return driver

    def _get_locator(self, 定位方式, 元素):
        """
        获取元素定位器
        
        :param 定位方式: 定位方式字符串
        :param 元素: 元素标识
        :return: (By, locator) 元组
        """
        by = self.LOCATOR_MAP.get(定位方式.lower())
        if by is None:
            raise ValueError(f"不支持的定位方式: {定位方式}")
        return by, 元素

    def _find_element(self, 定位方式, 元素, wait_time=None):
        """
        查找元素
        
        :param 定位方式: 定位方式
        :param 元素: 元素标识
        :param wait_time: 显式等待时间（秒），None 则使用隐式等待
        :return: WebElement
        """
        driver = self._get_driver()
        by, locator = self._get_locator(定位方式, 元素)
        
        try:
            if wait_time:
                element = WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((by, locator))
                )
            else:
                element = driver.find_element(by, locator)
            return element
        except (TimeoutException, NoSuchElementException) as e:
            # 截图保存
            self._take_screenshot_on_error(f"元素未找到_{定位方式}_{元素}")
            raise NoSuchElementException(f"未找到元素: {定位方式}={元素}") from e

    def _take_screenshot_on_error(self, name):
        """错误时截图"""
        try:
            driver = self._get_driver()
            screenshot_dir = "screenshots"
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{screenshot_dir}/{name}_{timestamp}.png"
            driver.save_screenshot(filename)
            
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
            浏览器: chrome/firefox/edge (默认 chrome)
            无头模式: true/false (默认 false)
            隐式等待: 等待时间（秒，默认 10）
            窗口大小: maximize/1920x1080/等 (默认 maximize)
        """
        kwargs.pop("关键字", None)
        
        browser = kwargs.get("浏览器", "chrome")
        headless = str(kwargs.get("无头模式", "false")).lower() in ["true", "1", "yes"]
        implicit_wait = int(kwargs.get("隐式等待", 10))
        window_size = kwargs.get("窗口大小", "maximize")
        
        print(f"正在启动浏览器: {browser}, 无头模式: {headless}")
        
        driver = DriverManager.create_driver(
            browser=browser,
            headless=headless,
            implicit_wait=implicit_wait,
            window_size=window_size
        )
        
        g_context().set_dict("current_driver", driver)
        print(f"浏览器启动成功: {browser}")

    @allure.step("关闭浏览器")
    def close_browser(self, **kwargs):
        """关闭浏览器"""
        kwargs.pop("关键字", None)
        
        driver = g_context().get_dict("current_driver")
        if driver:
            driver.quit()
            g_context().set_dict("current_driver", None)
            print("浏览器已关闭")

    @allure.step("导航到: {url}")
    def navigate_to(self, **kwargs):
        """
        导航到指定 URL
        
        参数:
            url: 目标 URL
        """
        kwargs.pop("关键字", None)
        url = kwargs.get("url")
        
        driver = self._get_driver()
        driver.get(url)
        print(f"已导航到: {url}")

    @allure.step("刷新页面")
    def refresh_page(self, **kwargs):
        """刷新当前页面"""
        kwargs.pop("关键字", None)
        driver = self._get_driver()
        driver.refresh()
        print("页面已刷新")

    @allure.step("后退")
    def back(self, **kwargs):
        """浏览器后退"""
        kwargs.pop("关键字", None)
        driver = self._get_driver()
        driver.back()
        print("已后退")

    @allure.step("前进")
    def forward(self, **kwargs):
        """浏览器前进"""
        kwargs.pop("关键字", None)
        driver = self._get_driver()
        driver.forward()
        print("已前进")

    # ==================== 元素操作 ====================

    @allure.step("点击元素: {定位方式}={元素}")
    def click_element(self, **kwargs):
        """
        点击元素
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            等待时间: 显式等待时间（秒，可选）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        等待时间 = kwargs.get("等待时间")
        
        element = self._find_element(定位方式, 元素, 等待时间)
        element.click()
        print(f"已点击元素: {定位方式}={元素}")

    @allure.step("输入文本: {文本}")
    def input_text(self, **kwargs):
        """
        输入文本
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            文本: 要输入的文本
            清空: true/false (是否先清空，默认 true)
            等待时间: 显式等待时间（秒，可选）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        文本 = kwargs.get("文本", "")
        清空 = str(kwargs.get("清空", "true")).lower() in ["true", "1", "yes"]
        等待时间 = kwargs.get("等待时间")
        
        element = self._find_element(定位方式, 元素, 等待时间)
        
        if 清空:
            element.clear()
        
        element.send_keys(文本)
        print(f"已输入文本: {文本}")

    @allure.step("清空文本")
    def clear_text(self, **kwargs):
        """
        清空文本
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            等待时间: 显式等待时间（秒，可选）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        等待时间 = kwargs.get("等待时间")
        
        element = self._find_element(定位方式, 元素, 等待时间)
        element.clear()
        print(f"已清空文本: {定位方式}={元素}")

    @allure.step("获取文本")
    def get_text(self, **kwargs):
        """
        获取元素文本并保存到变量
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            变量名: 保存到的变量名
            等待时间: 显式等待时间（秒，可选）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        变量名 = kwargs.get("变量名")
        等待时间 = kwargs.get("等待时间")
        
        element = self._find_element(定位方式, 元素, 等待时间)
        text = element.text
        
        if 变量名:
            g_context().set_dict(变量名, text)
            print(f"已获取文本并保存到变量 {变量名}: {text}")
        else:
            print(f"已获取文本: {text}")
        
        return text

    @allure.step("获取属性")
    def get_attribute(self, **kwargs):
        """
        获取元素属性并保存到变量
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            属性名: 要获取的属性名
            变量名: 保存到的变量名
            等待时间: 显式等待时间（秒，可选）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        属性名 = kwargs.get("属性名")
        变量名 = kwargs.get("变量名")
        等待时间 = kwargs.get("等待时间")
        
        element = self._find_element(定位方式, 元素, 等待时间)
        attr_value = element.get_attribute(属性名)
        
        if 变量名:
            g_context().set_dict(变量名, attr_value)
            print(f"已获取属性 {属性名} 并保存到变量 {变量名}: {attr_value}")
        else:
            print(f"已获取属性 {属性名}: {attr_value}")
        
        return attr_value

    @allure.step("选择下拉框")
    def select_dropdown(self, **kwargs):
        """
        选择下拉框选项
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            选择方式: value/text/index
            选项值: 选项的值/文本/索引
            等待时间: 显式等待时间（秒，可选）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        选择方式 = kwargs.get("选择方式", "value")
        选项值 = kwargs.get("选项值")
        等待时间 = kwargs.get("等待时间")
        
        element = self._find_element(定位方式, 元素, 等待时间)
        select = Select(element)
        
        if 选择方式 == "value":
            select.select_by_value(选项值)
        elif 选择方式 == "text":
            select.select_by_visible_text(选项值)
        elif 选择方式 == "index":
            select.select_by_index(int(选项值))
        else:
            raise ValueError(f"不支持的选择方式: {选择方式}")
        
        print(f"已选择下拉框选项: {选择方式}={选项值}")

    # ==================== 等待操作 ====================

    @allure.step("等待元素出现")
    def wait_for_element(self, **kwargs):
        """
        等待元素出现
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            超时时间: 超时时间（秒，默认 10）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 10))
        
        driver = self._get_driver()
        by, locator = self._get_locator(定位方式, 元素)
        
        try:
            WebDriverWait(driver, 超时时间).until(
                EC.presence_of_element_located((by, locator))
            )
            print(f"元素已出现: {定位方式}={元素}")
        except TimeoutException as e:
            self._take_screenshot_on_error(f"等待元素超时_{定位方式}_{元素}")
            raise TimeoutException(f"等待元素超时: {定位方式}={元素}") from e

    @allure.step("等待元素可见")
    def wait_for_element_visible(self, **kwargs):
        """
        等待元素可见
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            超时时间: 超时时间（秒，默认 10）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 10))
        
        driver = self._get_driver()
        by, locator = self._get_locator(定位方式, 元素)
        
        try:
            WebDriverWait(driver, 超时时间).until(
                EC.visibility_of_element_located((by, locator))
            )
            print(f"元素已可见: {定位方式}={元素}")
        except TimeoutException as e:
            self._take_screenshot_on_error(f"等待元素可见超时_{定位方式}_{元素}")
            raise TimeoutException(f"等待元素可见超时: {定位方式}={元素}") from e

    @allure.step("等待元素可点击")
    def wait_for_element_clickable(self, **kwargs):
        """
        等待元素可点击
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            超时时间: 超时时间（秒，默认 10）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 10))
        
        driver = self._get_driver()
        by, locator = self._get_locator(定位方式, 元素)
        
        try:
            WebDriverWait(driver, 超时时间).until(
                EC.element_to_be_clickable((by, locator))
            )
            print(f"元素已可点击: {定位方式}={元素}")
        except TimeoutException as e:
            self._take_screenshot_on_error(f"等待元素可点击超时_{定位方式}_{元素}")
            raise TimeoutException(f"等待元素可点击超时: {定位方式}={元素}") from e

    @allure.step("等待: {时间}秒")
    def sleep(self, **kwargs):
        """
        强制等待
        
        参数:
            时间: 等待时间（秒）
        """
        kwargs.pop("关键字", None)
        时间 = float(kwargs.get("时间", 1))
        time.sleep(时间)
        print(f"已等待 {时间} 秒")

    # ==================== 断言操作 ====================

    @allure.step("断言元素可见")
    def assert_element_visible(self, **kwargs):
        """
        断言元素可见
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            超时时间: 超时时间（秒，默认 10）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 10))
        
        driver = self._get_driver()
        by, locator = self._get_locator(定位方式, 元素)
        
        try:
            element = WebDriverWait(driver, 超时时间).until(
                EC.visibility_of_element_located((by, locator))
            )
            assert element.is_displayed(), f"元素不可见: {定位方式}={元素}"
            print(f"✓ 断言成功: 元素可见 {定位方式}={元素}")
        except Exception as e:
            self._take_screenshot_on_error(f"断言失败_元素不可见_{定位方式}_{元素}")
            raise AssertionError(f"断言失败: 元素不可见 {定位方式}={元素}") from e

    @allure.step("断言元素不可见")
    def assert_element_not_visible(self, **kwargs):
        """
        断言元素不可见
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            超时时间: 超时时间（秒，默认 10）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 10))
        
        driver = self._get_driver()
        by, locator = self._get_locator(定位方式, 元素)
        
        try:
            WebDriverWait(driver, 超时时间).until(
                EC.invisibility_of_element_located((by, locator))
            )
            print(f"✓ 断言成功: 元素不可见 {定位方式}={元素}")
        except Exception as e:
            self._take_screenshot_on_error(f"断言失败_元素可见_{定位方式}_{元素}")
            raise AssertionError(f"断言失败: 元素可见 {定位方式}={元素}") from e

    @allure.step("断言文本相等")
    def assert_text_equals(self, **kwargs):
        """
        断言元素文本相等
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            期望文本: 期望的文本
            等待时间: 显式等待时间（秒，可选）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        期望文本 = kwargs.get("期望文本", "")
        等待时间 = kwargs.get("等待时间")
        
        element = self._find_element(定位方式, 元素, 等待时间)
        实际文本 = element.text
        
        try:
            assert 实际文本 == 期望文本, f"文本不相等: 期望'{期望文本}', 实际'{实际文本}'"
            print(f"✓ 断言成功: 文本相等 '{实际文本}'")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言失败_文本不相等_{定位方式}_{元素}")
            raise e

    @allure.step("断言文本包含")
    def assert_text_contains(self, **kwargs):
        """
        断言元素文本包含指定内容
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            期望文本: 期望包含的文本
            等待时间: 显式等待时间（秒，可选）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        期望文本 = kwargs.get("期望文本", "")
        等待时间 = kwargs.get("等待时间")
        
        element = self._find_element(定位方式, 元素, 等待时间)
        实际文本 = element.text
        
        try:
            assert 期望文本 in 实际文本, f"文本不包含: 期望包含'{期望文本}', 实际'{实际文本}'"
            print(f"✓ 断言成功: 文本包含 '{期望文本}'")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言失败_文本不包含_{定位方式}_{元素}")
            raise e

    @allure.step("断言标题相等")
    def assert_title_equals(self, **kwargs):
        """
        断言页面标题相等
        
        参数:
            期望标题: 期望的标题
        """
        kwargs.pop("关键字", None)
        期望标题 = kwargs.get("期望标题", "")
        
        driver = self._get_driver()
        实际标题 = driver.title
        
        try:
            assert 实际标题 == 期望标题, f"标题不相等: 期望'{期望标题}', 实际'{实际标题}'"
            print(f"✓ 断言成功: 标题相等 '{实际标题}'")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言失败_标题不相等")
            raise e

    @allure.step("断言标题包含")
    def assert_title_contains(self, **kwargs):
        """
        断言页面标题包含指定内容
        
        参数:
            期望文本: 期望包含的文本
        """
        kwargs.pop("关键字", None)
        期望文本 = kwargs.get("期望文本", "")
        
        driver = self._get_driver()
        实际标题 = driver.title
        
        try:
            assert 期望文本 in 实际标题, f"标题不包含: 期望包含'{期望文本}', 实际'{实际标题}'"
            print(f"✓ 断言成功: 标题包含 '{期望文本}'")
        except AssertionError as e:
            self._take_screenshot_on_error(f"断言失败_标题不包含")
            raise e

    # ==================== 高级操作 ====================

    @allure.step("切换到Frame")
    def switch_to_frame(self, **kwargs):
        """
        切换到 iframe
        
        参数:
            定位方式: id/name/xpath/css 等 (可选)
            元素: 元素标识 (可选)
            索引: frame 索引 (可选)
        """
        kwargs.pop("关键字", None)
        
        driver = self._get_driver()
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        索引 = kwargs.get("索引")
        
        if 索引 is not None:
            driver.switch_to.frame(int(索引))
            print(f"已切换到 frame 索引: {索引}")
        elif 定位方式 and 元素:
            frame_element = self._find_element(定位方式, 元素)
            driver.switch_to.frame(frame_element)
            print(f"已切换到 frame: {定位方式}={元素}")
        else:
            driver.switch_to.default_content()
            print("已切换回主文档")

    @allure.step("切换到窗口")
    def switch_to_window(self, **kwargs):
        """
        切换到窗口
        
        参数:
            索引: 窗口索引 (从 0 开始)
            句柄: 窗口句柄 (可选)
        """
        kwargs.pop("关键字", None)
        
        driver = self._get_driver()
        索引 = kwargs.get("索引")
        句柄 = kwargs.get("句柄")
        
        if 句柄:
            driver.switch_to.window(句柄)
            print(f"已切换到窗口句柄: {句柄}")
        elif 索引 is not None:
            handles = driver.window_handles
            driver.switch_to.window(handles[int(索引)])
            print(f"已切换到窗口索引: {索引}")

    @allure.step("执行JavaScript")
    def execute_script(self, **kwargs):
        """
        执行 JavaScript 代码
        
        参数:
            脚本: JavaScript 代码
            变量名: 保存返回值到变量 (可选)
        """
        kwargs.pop("关键字", None)
        
        脚本 = kwargs.get("脚本", "")
        变量名 = kwargs.get("变量名")
        
        driver = self._get_driver()
        result = driver.execute_script(脚本)
        
        if 变量名:
            g_context().set_dict(变量名, result)
            print(f"已执行脚本并保存结果到 {变量名}: {result}")
        else:
            print(f"已执行脚本: {脚本}")
        
        return result

    @allure.step("截图")
    def take_screenshot(self, **kwargs):
        """
        截图
        
        参数:
            文件名: 截图文件名 (可选，默认自动生成)
        """
        kwargs.pop("关键字", None)
        
        文件名 = kwargs.get("文件名")
        driver = self._get_driver()
        
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        if not 文件名:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            文件名 = f"screenshot_{timestamp}.png"
        
        if not 文件名.endswith(".png"):
            文件名 += ".png"
        
        filepath = os.path.join(screenshot_dir, 文件名)
        driver.save_screenshot(filepath)
        
        # 附加到 Allure 报告
        with open(filepath, "rb") as f:
            allure.attach(f.read(), name=文件名, attachment_type=allure.attachment_type.PNG)
        
        print(f"已截图: {filepath}")

    @allure.step("滚动到元素")
    def scroll_to_element(self, **kwargs):
        """
        滚动到元素
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            等待时间: 显式等待时间（秒，可选）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        等待时间 = kwargs.get("等待时间")
        
        driver = self._get_driver()
        element = self._find_element(定位方式, 元素, 等待时间)
        
        driver.execute_script("arguments[0].scrollIntoView();", element)
        print(f"已滚动到元素: {定位方式}={元素}")

    @allure.step("鼠标悬停")
    def hover_element(self, **kwargs):
        """
        鼠标悬停到元素
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            等待时间: 显式等待时间（秒，可选）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        等待时间 = kwargs.get("等待时间")
        
        driver = self._get_driver()
        element = self._find_element(定位方式, 元素, 等待时间)
        
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        print(f"已鼠标悬停: {定位方式}={元素}")

    @allure.step("获取当前URL")
    def get_current_url(self, **kwargs):
        """
        获取当前 URL 并保存到变量
        
        参数:
            变量名: 保存到的变量名 (可选)
        """
        kwargs.pop("关键字", None)
        变量名 = kwargs.get("变量名")
        
        driver = self._get_driver()
        current_url = driver.current_url
        
        if 变量名:
            g_context().set_dict(变量名, current_url)
            print(f"已获取当前URL并保存到 {变量名}: {current_url}")
        else:
            print(f"当前URL: {current_url}")
        
        return current_url

