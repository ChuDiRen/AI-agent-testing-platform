"""
Web 自动化测试关键字
基于 Selenium WebDriver 实现
"""
import os
import time

import allure
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from ..core.globalContext import g_context
from ..utils.DriverManager import DriverManager


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
            # 获取项目根目录下的 reports/screenshots 目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            screenshot_dir = os.path.join(project_root, "reports", "screenshots")
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")
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

    def _close_common_popups(self):
        """检测并关闭常见页面弹窗（如百度登录提示）"""
        driver = self._get_driver()
        try:
            # 百度登录弹窗关闭按钮选择器列表
            popup_close_selectors = [
                (By.CSS_SELECTOR, ".tang-pass-loginPop-close"),  # 百度登录弹窗关闭按钮
                (By.CSS_SELECTOR, ".guide-close"),  # 百度引导弹窗
                (By.XPATH, "//div[contains(@class, 'dialog')]//span[contains(@class, 'close')]"),  # 通用弹窗
                (By.XPATH, "//div[contains(@class, 'modal')]//button[contains(@class, 'close')]"),  # 模态框
            ]
            
            for by, selector in popup_close_selectors:
                try:
                    close_btn = WebDriverWait(driver, 0.5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    close_btn.click()
                    time.sleep(0.3)  # 等待弹窗关闭动画
                    print(f"已关闭弹窗: {selector}")
                except:
                    continue  # 未找到该弹窗，继续检查下一个
        except Exception as e:
            pass  # 关闭弹窗失败不影响主流程

    @allure.step("点击元素: {定位方式}={元素}")
    def click_element(self, **kwargs):
        """
        点击元素（全面优化版，支持智能降级）
        
        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            等待时间: 显式等待时间（秒，可选）
            点击策略: 标准点击/JS点击/ActionChains点击（可选，默认：智能降级）
        """
        kwargs.pop("关键字", None)
        
        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        等待时间 = kwargs.get("等待时间")
        点击策略 = kwargs.get("点击策略", "智能降级")
        
        driver = self._get_driver()
        element = self._find_element(定位方式, 元素, 等待时间)
        
        # 预处理：关闭常见弹窗
        self._close_common_popups()
        
        # 预处理：滚动元素至可视区域中心
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", 
                element
            )
            time.sleep(0.3)  # 等待滚动动画完成
        except Exception as e:
            print(f"滚动元素时出现警告: {e}")
        
        # 点击策略执行
        click_success = False
        error_msg = ""
        
        if 点击策略 == "JS点击":
            # 策略1：强制使用 JavaScript 点击
            try:
                driver.execute_script("arguments[0].click();", element)
                click_success = True
                print(f"已点击元素(JS点击): {定位方式}={元素}")
            except Exception as e:
                error_msg = f"JS点击失败: {str(e)}"
        
        elif 点击策略 == "ActionChains点击":
            # 策略2：强制使用 ActionChains 点击
            try:
                ActionChains(driver).move_to_element(element).click().perform()
                click_success = True
                print(f"已点击元素(ActionChains点击): {定位方式}={元素}")
            except Exception as e:
                error_msg = f"ActionChains点击失败: {str(e)}"
        
        elif 点击策略 == "标准点击":
            # 策略3：强制使用标准点击
            try:
                element.click()
                click_success = True
                print(f"已点击元素(标准点击): {定位方式}={元素}")
            except Exception as e:
                error_msg = f"标准点击失败: {str(e)}"
        
        else:
            # 默认策略：智能降级（标准点击 -> JS点击 -> ActionChains点击）
            # 尝试1：标准点击
            try:
                element.click()
                click_success = True
                print(f"已点击元素(标准点击): {定位方式}={元素}")
            except Exception as e1:
                print(f"⚠ 标准点击失败: {str(e1)[:50]}...，尝试降级为JS点击")
                
                # 尝试2：JS点击
                try:
                    driver.execute_script("arguments[0].click();", element)
                    click_success = True
                    print(f"✓ 已点击元素(JS点击-降级策略): {定位方式}={元素}")
                except Exception as e2:
                    print(f"⚠ JS点击失败: {str(e2)[:50]}...，尝试降级为ActionChains点击")
                    
                    # 尝试3：ActionChains点击
                    try:
                        ActionChains(driver).move_to_element(element).click().perform()
                        click_success = True
                        print(f"✓ 已点击元素(ActionChains点击-降级策略): {定位方式}={元素}")
                    except Exception as e3:
                        error_msg = f"所有点击策略均失败 - 标准点击: {str(e1)[:30]}, JS点击: {str(e2)[:30]}, ActionChains点击: {str(e3)[:30]}"
        
        # 点击失败处理
        if not click_success:
            self._take_screenshot_on_error(f"点击元素失败_{定位方式}_{元素}")
            raise Exception(f"点击元素失败: {定位方式}={元素}. {error_msg}")

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
            超时时间: 超时时间（秒，默认 15）
        """
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 15))  # 默认超时时间增加到15秒

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
            超时时间: 超时时间（秒，默认 15）
        """
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 15))  # 默认超时时间增加到15秒

        driver = self._get_driver()
        by, locator = self._get_locator(定位方式, 元素)

        try:
            # 使用更智能的等待策略：先等待元素存在，再等待可见
            WebDriverWait(driver, 超时时间).until(
                EC.presence_of_element_located((by, locator))
            )
            WebDriverWait(driver, 超时时间).until(
                EC.visibility_of_element_located((by, locator))
            )
            print(f"元素已可见: {定位方式}={元素}")
        except TimeoutException as e:
            # 提供更详细的错误信息
            try:
                # 尝试查找元素是否存在但不可见
                element = driver.find_element(by, locator)
                error_msg = f"等待元素可见超时: {定位方式}={元素} (元素存在但不可见，display={element.value_of_css_property('display')})"
            except:
                error_msg = f"等待元素可见超时: {定位方式}={元素} (元素不存在)"

            self._take_screenshot_on_error(f"等待元素可见超时_{定位方式}_{元素}")
            raise TimeoutException(error_msg) from e

    @allure.step("等待元素可点击")
    def wait_for_element_clickable(self, **kwargs):
        """
        等待元素可点击

        参数:
            定位方式: id/name/xpath/css 等
            元素: 元素标识
            超时时间: 超时时间（秒，默认 15）
        """
        kwargs.pop("关键字", None)

        定位方式 = kwargs.get("定位方式")
        元素 = kwargs.get("元素")
        超时时间 = int(kwargs.get("超时时间", 15))  # 默认超时时间增加到15秒

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
        
        # 获取项目根目录下的 reports/screenshots 目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        screenshot_dir = os.path.join(project_root, "reports", "screenshots")
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

    # ==================== AI 驱动操作 ====================

    def _ai_click(self, bbox):
        """
        根据边界框坐标点击元素中心
        
        :param bbox: 边界框坐标 [xmin, ymin, xmax, ymax]
        """
        from selenium.webdriver.common.actions.action_builder import ActionBuilder
        
        # 计算中心点坐标
        x_coordinate = (bbox[0] + bbox[2]) / 2
        y_coordinate = (bbox[1] + bbox[3]) / 2
        print(f"元素中心点坐标信息: {x_coordinate}, {y_coordinate}")
        
        driver = self._get_driver()
        action_builder = ActionBuilder(driver)
        action_builder.pointer_action.move_to_location(x_coordinate, y_coordinate).click()
        action_builder.perform()

    def _ai_input(self, bbox, text):
        """
        点击并在元素位置输入文本
        
        :param bbox: 边界框坐标 [xmin, ymin, xmax, ymax]
        :param text: 要输入的文本
        """
        self._ai_click(bbox)
        # 在当前焦点元素输入文本
        driver = self._get_driver()
        driver.switch_to.active_element.send_keys(text)

    def _ai_extract_text(self, text):
        """
        将提取的文本保存到全局上下文
        
        :param text: 提取的文本内容
        """
        g_context().set_dict("ai_extracted_text", text)
        print(f"已提取文本到全局变量 ai_extracted_text: {text}")

    def _call_ai_vision(self, user_description, actions):
        """
        调用 Qwen-VL API 进行截图分析
        
        :param user_description: 用户的操作描述
        :param actions: 支持的操作类型列表
        :return: AI 返回的结果字典
        """
        import base64
        import json
        import os
        import re
        import uuid
        from openai import OpenAI
        from PIL import Image
        from qwen_vl_utils import smart_resize

        # 初始化 OpenAI 客户端（百炼API）
        ai_client = OpenAI(
            api_key="sk-aeb8d69039b14320b0fe58cb8285d8b1",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        # 提示词模板
        prompt = """
## 目标
- 识别屏幕截图和文本中与用户描述匹配的元素。

## 输出格式
```json
{{
  "bbox": [xmin, ymin, xmax, ymax],
  "action": "用户的操作类型（{actions}）",
  "text": "提取的文本内容或要输入的文本",
  "errors"?: "如果你无法找到，就把你的原因写在这里"
}}
```

## 工作流程
1. 接受用户描述的文字以及提供的截图。请注意，文本可能包含非英文字符（例如中文），这表明程序可能是非英文的。
2. 分析用户的文字内容，提取其中关于元素的描述信息。根据关于元素的描述信息，找到屏幕截图中目标元素。
3. 返回元素在截图中的 bbox 具体位置信息。

## 用户描述
{user_text}
"""

        ai_prompt = prompt.format(
            user_text=user_description,
            actions=", ".join(actions)
        )

        # 调用 driver 进行界面截图
        driver = self._get_driver()
        image_base64 = driver.get_screenshot_as_base64()

        # 保存临时截图文件
        image_path = os.path.join(
            os.path.dirname(__file__),
            f"{str(uuid.uuid4()).replace('-', '')}.png"
        )
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(image_base64))

        # 获取图片尺寸
        width, height = Image.open(image_path).size
        print(f"截图尺寸：{width}, {height}")

        # AI 模型的图片处理尺寸（通义千问VL模型标准配置）
        min_pixels = 512 * 28 * 28  # 最小像素数：约400K
        max_pixels = 2048 * 28 * 28  # 最大像素数：约1.6M
        factor = 28  # 通义千问VL模型推荐的分块因子
        
        # 自适应调整：当截图超大时自动调整 factor，避免内存溢出
        total_pixels = width * height
        if total_pixels > 10_000_000:  # 超过1000万像素（约3840x2600）
            factor = 14  # 使用更小的因子
            print(f"⚠ 检测到超大截图({total_pixels}像素)，自动调整factor={factor}")
        
        input_height, input_width = smart_resize(
            height, width,
            factor=factor,
            min_pixels=min_pixels,
            max_pixels=max_pixels
        )
        print(f"输入尺寸：{input_height}, {input_width} (factor={factor})")

        # 删除临时图片
        os.remove(image_path)

        print(f'AI提示词: {ai_prompt}')

        # 调用 AI 模型
        completion = ai_client.chat.completions.create(
            model="qwen-vl-max-latest",
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
            }]
        )

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

    @allure.step("AI操作: {操作描述}")
    def ai_operation(self, **kwargs):
        """
        AI 驱动的主操作调度器
        
        参数:
            操作描述: 自然语言描述的操作，如"点击登录按钮"、"在用户名输入框输入admin"
        
        示例:
            - 操作描述: "点击红色的提交按钮"
            - 操作描述: "在密码框输入123456"
            - 操作描述: "提取页面标题文本"
        """
        kwargs.pop("关键字", None)
        操作描述 = kwargs.get("操作描述")
        
        if not 操作描述:
            raise ValueError("操作描述不能为空")

        # 支持的操作类型
        actions = ['点击', '输入', '文本提取', '滚动', '悬停', '拖拽']
        
        try:
            # 调用 AI 视觉分析
            result = self._call_ai_vision(操作描述, actions)
            
            # 根据操作类型执行相应操作
            action = result.get('action')
            bbox = result.get('bbox')
            text = result.get('text', '')
            
            if action == '点击':
                self._ai_click(bbox)
                print(f"✓ AI操作成功: 点击元素")
            elif action == '输入':
                self._ai_input(bbox, text)
                print(f"✓ AI操作成功: 输入文本 '{text}'")
            elif action == '文本提取':
                self._ai_extract_text(text)
                print(f"✓ AI操作成功: 提取文本 '{text}'")
            elif action == '滚动':
                driver = self._get_driver()
                x = (bbox[0] + bbox[2]) / 2
                y = (bbox[1] + bbox[3]) / 2
                driver.execute_script(f"window.scrollTo({x}, {y});")
                print(f"✓ AI操作成功: 滚动到元素")
            elif action == '悬停':
                driver = self._get_driver()
                from selenium.webdriver.common.actions.action_builder import ActionBuilder
                x = (bbox[0] + bbox[2]) / 2
                y = (bbox[1] + bbox[3]) / 2
                action_builder = ActionBuilder(driver)
                action_builder.pointer_action.move_to_location(x, y)
                action_builder.perform()
                print(f"✓ AI操作成功: 鼠标悬停")
            elif action == '拖拽':
                # 拖拽需要两个元素，这里简化处理
                raise NotImplementedError("拖拽操作需要使用 ai_drag 方法")
            else:
                raise ValueError(f"不支持的操作类型: {action}")
                
        except Exception as e:
            self._take_screenshot_on_error(f"AI操作失败_{操作描述}")
            raise e

    @allure.step("AI点击: {元素描述}")
    def ai_click(self, **kwargs):
        """
        AI 驱动的点击操作
        
        参数:
            元素描述: 元素的自然语言描述，如"红色的提交按钮"、"登录链接"
        """
        kwargs.pop("关键字", None)
        元素描述 = kwargs.get("元素描述")
        
        if not 元素描述:
            raise ValueError("元素描述不能为空")
        
        操作描述 = f"点击{元素描述}"
        self.ai_operation(操作描述=操作描述)

    @allure.step("AI输入: {文本}")
    def ai_input(self, **kwargs):
        """
        AI 驱动的输入操作
        
        参数:
            元素描述: 输入框的自然语言描述，如"用户名输入框"、"搜索框"
            文本: 要输入的文本内容
        """
        kwargs.pop("关键字", None)
        元素描述 = kwargs.get("元素描述")
        文本 = kwargs.get("文本", "")
        
        if not 元素描述:
            raise ValueError("元素描述不能为空")
        
        操作描述 = f"在{元素描述}输入{文本}"
        
        try:
            actions = ['输入']
            result = self._call_ai_vision(操作描述, actions)
            self._ai_input(result['bbox'], 文本)
            print(f"✓ AI输入成功: 在{元素描述}输入 '{文本}'")
        except Exception as e:
            self._take_screenshot_on_error(f"AI输入失败_{元素描述}")
            raise e

    @allure.step("AI提取文本: {文本描述}")
    def ai_extract_text(self, **kwargs):
        """
        AI 驱动的文本提取
        
        参数:
            文本描述: 要提取文本的描述，如"页面标题"、"错误提示信息"
            变量名: 保存到的变量名（可选，默认保存到 ai_extracted_text）
        """
        kwargs.pop("关键字", None)
        文本描述 = kwargs.get("文本描述")
        变量名 = kwargs.get("变量名", "ai_extracted_text")
        
        if not 文本描述:
            raise ValueError("文本描述不能为空")
        
        操作描述 = f"提取{文本描述}的文本内容"
        
        try:
            actions = ['文本提取']
            result = self._call_ai_vision(操作描述, actions)
            text = result.get('text', '')
            g_context().set_dict(变量名, text)
            print(f"✓ AI文本提取成功: 已提取 '{text}' 并保存到变量 {变量名}")
        except Exception as e:
            self._take_screenshot_on_error(f"AI文本提取失败_{文本描述}")
            raise e

    @allure.step("AI滚动: {元素描述}")
    def ai_scroll(self, **kwargs):
        """
        AI 驱动的滚动操作
        
        参数:
            元素描述: 要滚动到的元素描述，如"页面底部"、"评论区"
        """
        kwargs.pop("关键字", None)
        元素描述 = kwargs.get("元素描述")
        
        if not 元素描述:
            raise ValueError("元素描述不能为空")
        
        操作描述 = f"滚动到{元素描述}"
        
        try:
            actions = ['滚动']
            result = self._call_ai_vision(操作描述, actions)
            bbox = result['bbox']
            
            driver = self._get_driver()
            x = (bbox[0] + bbox[2]) / 2
            y = (bbox[1] + bbox[3]) / 2
            driver.execute_script(f"window.scrollTo({x}, {y});")
            print(f"✓ AI滚动成功: 滚动到{元素描述}")
        except Exception as e:
            self._take_screenshot_on_error(f"AI滚动失败_{元素描述}")
            raise e

    @allure.step("AI悬停: {元素描述}")
    def ai_hover(self, **kwargs):
        """
        AI 驱动的鼠标悬停操作
        
        参数:
            元素描述: 要悬停的元素描述，如"用户菜单"、"导航栏"
        """
        kwargs.pop("关键字", None)
        元素描述 = kwargs.get("元素描述")
        
        if not 元素描述:
            raise ValueError("元素描述不能为空")
        
        操作描述 = f"鼠标悬停在{元素描述}"
        
        try:
            actions = ['悬停']
            result = self._call_ai_vision(操作描述, actions)
            bbox = result['bbox']
            
            driver = self._get_driver()
            from selenium.webdriver.common.actions.action_builder import ActionBuilder
            x = (bbox[0] + bbox[2]) / 2
            y = (bbox[1] + bbox[3]) / 2
            action_builder = ActionBuilder(driver)
            action_builder.pointer_action.move_to_location(x, y)
            action_builder.perform()
            print(f"✓ AI悬停成功: 鼠标悬停在{元素描述}")
        except Exception as e:
            self._take_screenshot_on_error(f"AI悬停失败_{元素描述}")
            raise e

    @allure.step("AI拖拽: {源元素描述} -> {目标元素描述}")
    def ai_drag(self, **kwargs):
        """
        AI 驱动的拖拽操作
        
        参数:
            源元素描述: 要拖拽的元素描述，如"待办事项"
            目标元素描述: 拖拽目标的描述，如"已完成区域"
        """
        kwargs.pop("关键字", None)
        源元素描述 = kwargs.get("源元素描述")
        目标元素描述 = kwargs.get("目标元素描述")
        
        if not 源元素描述 or not 目标元素描述:
            raise ValueError("源元素描述和目标元素描述不能为空")
        
        try:
            # 先找到源元素
            操作描述1 = f"找到{源元素描述}"
            actions = ['拖拽']
            result1 = self._call_ai_vision(操作描述1, actions)
            源bbox = result1['bbox']
            源x = (源bbox[0] + 源bbox[2]) / 2
            源y = (源bbox[1] + 源bbox[3]) / 2
            
            # 再找到目标元素
            操作描述2 = f"找到{目标元素描述}"
            result2 = self._call_ai_vision(操作描述2, actions)
            目标bbox = result2['bbox']
            目标x = (目标bbox[0] + 目标bbox[2]) / 2
            目标y = (目标bbox[1] + 目标bbox[3]) / 2
            
            # 执行拖拽
            driver = self._get_driver()
            from selenium.webdriver.common.actions.action_builder import ActionBuilder
            action_builder = ActionBuilder(driver)
            action_builder.pointer_action.move_to_location(源x, 源y)
            action_builder.pointer_action.pointer_down()
            action_builder.pointer_action.move_to_location(目标x, 目标y)
            action_builder.pointer_action.pointer_up()
            action_builder.perform()
            
            print(f"✓ AI拖拽成功: {源元素描述} -> {目标元素描述}")
        except Exception as e:
            self._take_screenshot_on_error(f"AI拖拽失败_{源元素描述}_to_{目标元素描述}")
            raise e

    @allure.step("AI断言可见: {元素描述}")
    def ai_assert_visible(self, **kwargs):
        """
        AI 驱动的可见性断言
        
        参数:
            元素描述: 要断言可见的元素描述，如"成功提示消息"、"登录按钮"
        """
        kwargs.pop("关键字", None)
        元素描述 = kwargs.get("元素描述")
        
        if not 元素描述:
            raise ValueError("元素描述不能为空")
        
        操作描述 = f"找到{元素描述}"
        
        try:
            actions = ['点击']  # 使用点击操作来定位元素
            result = self._call_ai_vision(操作描述, actions)
            
            # 如果 AI 能找到元素，说明元素可见
            if result.get('bbox'):
                print(f"✓ AI断言成功: {元素描述} 可见")
            else:
                raise AssertionError(f"AI断言失败: {元素描述} 不可见")
        except Exception as e:
            self._take_screenshot_on_error(f"AI断言失败_{元素描述}")
            raise AssertionError(f"AI断言失败: {元素描述} 不可见") from e

