# Copyright (c) 2025 左岚. All rights reserved.
"""
浏览器自动化测试引擎
"""
import asyncio
import json
import time
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("警告: Selenium未安装，浏览器自动化功能不可用")

try:
    from PIL import Image
    from io import BytesIO
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("警告: Pillow未安装，截图功能不可用")


class BrowserEngine:
    """浏览器自动化测试引擎"""

    def __init__(self, config: Dict = None):
        """
        初始化浏览器引擎

        Args:
            config: 浏览器配置
        """
        self.config = config or {}
        self.driver = None
        self.wait = None
        self.action_chains = None
        self.screenshots = []
        self.logs = []
        self.current_step = 0

        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium未安装，无法使用浏览器自动化功能")

    def setup_driver(self) -> bool:
        """设置浏览器驱动"""
        try:
            browser_type = self.config.get('browser_type', 'chrome').lower()
            headless = self.config.get('headless', True)
            window_size = self.config.get('window_size', '1920x1080')
            timeout = self.config.get('timeout', 30)

            width, height = map(int, window_size.split('x'))

            if browser_type == 'chrome':
                options = ChromeOptions()
                if headless:
                    options.add_argument('--headless')
                options.add_argument(f'--window-size={width},{height}')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-web-security')
                options.add_argument('--allow-running-insecure-content')

                # 添加自定义能力配置
                capabilities = self.config.get('capabilities', {})
                if capabilities:
                    for key, value in capabilities.items():
                        options.set_capability(key, value)

                # 创建驱动服务
                service_config = self.config.get('service_config', {})
                if service_config:
                    service = ChromeService(**service_config)
                    self.driver = webdriver.Chrome(service=service, options=options)
                else:
                    self.driver = webdriver.Chrome(options=options)

            elif browser_type == 'firefox':
                options = FirefoxOptions()
                if headless:
                    options.add_argument('-headless')
                options.add_argument(f'--width={width}')
                options.add_argument(f'--height={height}')

                self.driver = webdriver.Firefox(options=options)

            else:
                raise ValueError(f"不支持的浏览器类型: {browser_type}")

            # 设置等待和动作链
            self.wait = WebDriverWait(self.driver, timeout)
            self.action_chains = ActionChains(self.driver)

            # 设置隐式等待
            self.driver.implicitly_wait(timeout)

            self.log(f"✅ 浏览器驱动初始化成功: {browser_type}")
            return True

        except Exception as e:
            self.log(f"❌ 浏览器驱动初始化失败: {str(e)}")
            return False

    def navigate_to_url(self, url: str) -> bool:
        """导航到指定URL"""
        try:
            self.log(f"🌐 导航到URL: {url}")
            self.driver.get(url)
            self.log(f"✅ 页面加载完成: {self.driver.title}")
            return True
        except Exception as e:
            self.log(f"❌ 页面导航失败: {str(e)}")
            return False

    def find_element(self, locator: Dict, timeout: int = None) -> Optional[Any]:
        """查找元素"""
        try:
            by_type = self._get_by_type(locator.get('type', 'css'))
            by_value = locator.get('value')

            if timeout:
                wait = WebDriverWait(self.driver, timeout)
                element = wait.until(EC.presence_of_element_located((by_type, by_value)))
            else:
                element = self.driver.find_element(by_type, by_value)

            self.log(f"🔍 找到元素: {locator}")
            return element
        except Exception as e:
            self.log(f"❌ 元素查找失败: {locator}, 错误: {str(e)}")
            return None

    def find_elements(self, locator: Dict) -> List[Any]:
        """查找多个元素"""
        try:
            by_type = self._get_by_type(locator.get('type', 'css'))
            by_value = locator.get('value')
            elements = self.driver.find_elements(by_type, by_value)
            self.log(f"🔍 找到 {len(elements)} 个元素: {locator}")
            return elements
        except Exception as e:
            self.log(f"❌ 元素查找失败: {locator}, 错误: {str(e)}")
            return []

    def click_element(self, locator: Dict, timeout: int = None) -> bool:
        """点击元素"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                element.click()
                self.log(f"🖱️  点击元素: {locator}")
                return True
            return False
        except Exception as e:
            self.log(f"❌ 元素点击失败: {locator}, 错误: {str(e)}")
            return False

    def input_text(self, locator: Dict, text: str, clear_first: bool = True) -> bool:
        """输入文本"""
        try:
            element = self.find_element(locator)
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                self.log(f"⌨️  输入文本: {locator} -> '{text}'")
                return True
            return False
        except Exception as e:
            self.log(f"❌ 文本输入失败: {locator}, 错误: {str(e)}")
            return False

    def get_element_text(self, locator: Dict) -> Optional[str]:
        """获取元素文本"""
        try:
            element = self.find_element(locator)
            if element:
                text = element.text
                self.log(f"📄 获取元素文本: {locator} -> '{text}'")
                return text
            return None
        except Exception as e:
            self.log(f"❌ 获取文本失败: {locator}, 错误: {str(e)}")
            return None

    def get_element_attribute(self, locator: Dict, attribute: str) -> Optional[str]:
        """获取元素属性"""
        try:
            element = self.find_element(locator)
            if element:
                value = element.get_attribute(attribute)
                self.log(f"🏷️  获取元素属性: {locator}.{attribute} -> '{value}'")
                return value
            return None
        except Exception as e:
            self.log(f"❌ 获取属性失败: {locator}.{attribute}, 错误: {str(e)}")
            return None

    def wait_for_element(self, locator: Dict, timeout: int = None) -> bool:
        """等待元素出现"""
        try:
            timeout = timeout or self.config.get('timeout', 30)
            by_type = self._get_by_type(locator.get('type', 'css'))
            by_value = locator.get('value')

            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by_type, by_value))
            )
            self.log(f"⏳ 等待元素出现: {locator}")
            return True
        except TimeoutException:
            self.log(f"⏰ 等待元素超时: {locator}")
            return False
        except Exception as e:
            self.log(f"❌ 等待元素失败: {locator}, 错误: {str(e)}")
            return False

    def wait_for_element_visible(self, locator: Dict, timeout: int = None) -> bool:
        """等待元素可见"""
        try:
            timeout = timeout or self.config.get('timeout', 30)
            by_type = self._get_by_type(locator.get('type', 'css'))
            by_value = locator.get('value')

            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by_type, by_value))
            )
            self.log(f"👁️  等待元素可见: {locator}")
            return True
        except TimeoutException:
            self.log(f"⏰ 等待元素可见超时: {locator}")
            return False
        except Exception as e:
            self.log(f"❌ 等待元素可见失败: {locator}, 错误: {str(e)}")
            return False

    def wait_for_text_in_element(self, locator: Dict, text: str, timeout: int = None) -> bool:
        """等待元素中包含指定文本"""
        try:
            timeout = timeout or self.config.get('timeout', 30)
            by_type = self._get_by_type(locator.get('type', 'css'))
            by_value = locator.get('value')

            WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element((by_type, by_value), text)
            )
            self.log(f"📝 等待文本出现: {locator} 包含 '{text}'")
            return True
        except TimeoutException:
            self.log(f"⏰ 等待文本超时: {locator} 包含 '{text}'")
            return False
        except Exception as e:
            self.log(f"❌ 等待文本失败: {locator} 包含 '{text}', 错误: {str(e)}")
            return False

    def scroll_to_element(self, locator: Dict) -> bool:
        """滚动到元素"""
        try:
            element = self.find_element(locator)
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                self.log(f"📜 滚动到元素: {locator}")
                return True
            return False
        except Exception as e:
            self.log(f"❌ 滚动失败: {locator}, 错误: {str(e)}")
            return False

    def take_screenshot(self, filename: str = None) -> Optional[str]:
        """截图"""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"screenshot_{timestamp}.png"

            screenshot_dir = self.config.get('screenshot_dir', 'screenshots')
            os.makedirs(screenshot_dir, exist_ok=True)
            file_path = os.path.join(screenshot_dir, filename)

            self.driver.save_screenshot(file_path)
            self.screenshots.append(file_path)
            self.log(f"📸 截图保存: {file_path}")
            return file_path
        except Exception as e:
            self.log(f"❌ 截图失败: {str(e)}")
            return None

    def execute_javascript(self, script: str, *args) -> Any:
        """执行JavaScript"""
        try:
            result = self.driver.execute_script(script, *args)
            self.log(f"⚙️  执行JavaScript: {script}")
            return result
        except Exception as e:
            self.log(f"❌ JavaScript执行失败: {script}, 错误: {str(e)}")
            return None

    def switch_to_frame(self, frame_locator: Union[str, int, Dict] = None) -> bool:
        """切换到框架"""
        try:
            if frame_locator is None:
                self.driver.switch_to.default_content()
                self.log("🔄 切换到默认内容")
                return True
            elif isinstance(frame_locator, int):
                self.driver.switch_to.frame(frame_locator)
                self.log(f"🔄 切换到框架索引: {frame_locator}")
                return True
            elif isinstance(frame_locator, str):
                self.driver.switch_to.frame(frame_locator)
                self.log(f"🔄 切换到框架: {frame_locator}")
                return True
            elif isinstance(frame_locator, dict):
                element = self.find_element(frame_locator)
                if element:
                    self.driver.switch_to.frame(element)
                    self.log(f"🔄 切换到框架元素: {frame_locator}")
                    return True
            return False
        except Exception as e:
            self.log(f"❌ 框架切换失败: {frame_locator}, 错误: {str(e)}")
            return False

    def switch_to_window(self, window_handle: str = None, window_index: int = None) -> bool:
        """切换窗口"""
        try:
            if window_handle:
                self.driver.switch_to.window(window_handle)
                self.log(f"🔄 切换到窗口: {window_handle}")
                return True
            elif window_index is not None:
                windows = self.driver.window_handles
                if 0 <= window_index < len(windows):
                    self.driver.switch_to.window(windows[window_index])
                    self.log(f"🔄 切换到窗口索引: {window_index}")
                    return True
            return False
        except Exception as e:
            self.log(f"❌ 窗口切换失败, 错误: {str(e)}")
            return False

    def close_current_window(self) -> bool:
        """关闭当前窗口"""
        try:
            self.driver.close()
            self.log("🔒 关闭当前窗口")
            return True
        except Exception as e:
            self.log(f"❌ 关闭窗口失败: {str(e)}")
            return False

    def refresh_page(self) -> bool:
        """刷新页面"""
        try:
            self.driver.refresh()
            self.log("🔄 页面刷新")
            return True
        except Exception as e:
            self.log(f"❌ 页面刷新失败: {str(e)}")
            return False

    def go_back(self) -> bool:
        """后退"""
        try:
            self.driver.back()
            self.log("⬅️  后退")
            return True
        except Exception as e:
            self.log(f"❌ 后退失败: {str(e)}")
            return False

    def go_forward(self) -> bool:
        """前进"""
        try:
            self.driver.forward()
            self.log("➡️  前进")
            return True
        except Exception as e:
            self.log(f"❌ 前进失败: {str(e)}")
            return False

    def maximize_window(self) -> bool:
        """最大化窗口"""
        try:
            self.driver.maximize_window()
            self.log("📐 窗口最大化")
            return True
        except Exception as e:
            self.log(f"❌ 窗口最大化失败: {str(e)}")
            return False

    def execute_test_steps(self, test_steps: List[Dict], variables: Dict = None) -> Dict:
        """执行测试步骤"""
        variables = variables or {}
        step_results = []
        start_time = time.time()

        for i, step in enumerate(test_steps):
            self.current_step = i + 1
            step_start_time = time.time()

            step_result = {
                "step_number": self.current_step,
                "step_name": step.get("name", f"步骤 {self.current_step}"),
                "step_type": step.get("type", "unknown"),
                "status": "pending",
                "start_time": step_start_time,
                "duration": 0,
                "error_message": None,
                "screenshot": None
            }

            try:
                # 执行步骤
                success = self._execute_single_step(step, variables)
                step_result["status"] = "success" if success else "failed"

                # 截图配置
                screenshot_config = step.get("screenshot", {})
                if screenshot_config.get("enabled", False):
                    filename = f"step_{self.current_step}_{step.get('name', 'step').replace(' ', '_')}.png"
                    step_result["screenshot"] = self.take_screenshot(filename)

            except Exception as e:
                step_result["status"] = "error"
                step_result["error_message"] = str(e)
                self.log(f"❌ 步骤执行异常: {step.get('name', '未知步骤')}, 错误: {str(e)}")

            step_result["duration"] = time.time() - step_start_time
            step_results.append(step_result)

            # 检查是否需要停止执行
            if step_result["status"] in ["failed", "error"] and step.get("stop_on_failure", True):
                self.log(f"⛔ 步骤失败，停止执行: {step.get('name', '未知步骤')}")
                break

        total_duration = time.time() - start_time

        return {
            "total_steps": len(test_steps),
            "completed_steps": len(step_results),
            "step_results": step_results,
            "total_duration": total_duration,
            "screenshots": self.screenshots,
            "logs": self.logs
        }

    def _execute_single_step(self, step: Dict, variables: Dict) -> bool:
        """执行单个步骤"""
        step_type = step.get("type", "").lower()
        action_config = step.get("action", {})
        wait_config = step.get("wait", {})
        validation_config = step.get("validation", {})

        # 处理变量替换
        action_config = self._replace_variables(action_config, variables)
        wait_config = self._replace_variables(wait_config, variables)
        validation_config = self._replace_variables(validation_config, variables)

        self.log(f"🚀 执行步骤: {step.get('name', '未知步骤')} ({step_type})")

        # 执行动作
        success = self._execute_action(step_type, action_config)
        if not success:
            return False

        # 等待
        if wait_config.get("enabled", True):
            wait_time = wait_config.get("time", 1)
            if wait_time > 0:
                time.sleep(wait_time)
                self.log(f"⏳ 等待 {wait_time} 秒")

        # 验证
        if validation_config.get("enabled", True):
            return self._execute_validation(validation_config)

        return True

    def _execute_action(self, action_type: str, config: Dict) -> bool:
        """执行动作"""
        try:
            if action_type == "navigate":
                return self.navigate_to_url(config.get("url", ""))

            elif action_type == "click":
                return self.click_element(config.get("locator", {}), config.get("timeout"))

            elif action_type == "input":
                return self.input_text(
                    config.get("locator", {}),
                    config.get("text", ""),
                    config.get("clear_first", True)
                )

            elif action_type == "scroll":
                return self.scroll_to_element(config.get("locator", {}))

            elif action_type == "screenshot":
                return self.take_screenshot(config.get("filename")) is not None

            elif action_type == "javascript":
                return self.execute_javascript(
                    config.get("script", ""),
                    *config.get("args", [])
                ) is not None

            elif action_type == "wait":
                wait_type = config.get("wait_type", "time")
                if wait_type == "time":
                    time.sleep(config.get("duration", 1))
                    return True
                elif wait_type == "element":
                    return self.wait_for_element(
                        config.get("locator", {}),
                        config.get("timeout")
                    )
                elif wait_type == "visible":
                    return self.wait_for_element_visible(
                        config.get("locator", {}),
                        config.get("timeout")
                    )
                elif wait_type == "text":
                    return self.wait_for_text_in_element(
                        config.get("locator", {}),
                        config.get("text", ""),
                        config.get("timeout")
                    )

            elif action_type == "switch_frame":
                return self.switch_to_frame(config.get("frame_locator"))

            elif action_type == "switch_window":
                return self.switch_to_window(
                    config.get("window_handle"),
                    config.get("window_index")
                )

            elif action_type == "close_window":
                return self.close_current_window()

            elif action_type == "refresh":
                return self.refresh_page()

            elif action_type == "back":
                return self.go_back()

            elif action_type == "forward":
                return self.go_forward()

            elif action_type == "maximize":
                return self.maximize_window()

            else:
                self.log(f"❌ 不支持的动作类型: {action_type}")
                return False

        except Exception as e:
            self.log(f"❌ 动作执行失败: {action_type}, 错误: {str(e)}")
            return False

    def _execute_validation(self, config: Dict) -> bool:
        """执行验证"""
        try:
            validation_type = config.get("type", "").lower()
            locator = config.get("locator", {})
            expected_value = config.get("expected_value")
            operator = config.get("operator", "equals")

            if validation_type == "element_exists":
                element = self.find_element(locator)
                success = element is not None
                self.log(f"✅ 元素存在验证: {locator} -> {success}")
                return success

            elif validation_type == "element_visible":
                element = self.find_element(locator)
                if element:
                    success = element.is_displayed()
                    self.log(f"✅ 元素可见验证: {locator} -> {success}")
                    return success
                return False

            elif validation_type == "text_contains":
                actual_text = self.get_element_text(locator)
                if actual_text:
                    success = expected_value in actual_text
                    self.log(f"✅ 文本包含验证: '{expected_value}' in '{actual_text}' -> {success}")
                    return success
                return False

            elif validation_type == "text_equals":
                actual_text = self.get_element_text(locator)
                if actual_text:
                    success = actual_text == expected_value
                    self.log(f"✅ 文本相等验证: '{actual_text}' == '{expected_value}' -> {success}")
                    return success
                return False

            elif validation_type == "attribute_equals":
                actual_value = self.get_element_attribute(locator, config.get("attribute", ""))
                if actual_value is not None:
                    success = actual_value == expected_value
                    self.log(f"✅ 属性相等验证: {config.get('attribute')} '{actual_value}' == '{expected_value}' -> {success}")
                    return success
                return False

            elif validation_type == "title_contains":
                actual_title = self.driver.title
                success = expected_value in actual_title
                self.log(f"✅ 标题包含验证: '{expected_value}' in '{actual_title}' -> {success}")
                return success

            elif validation_type == "url_contains":
                actual_url = self.driver.current_url
                success = expected_value in actual_url
                self.log(f"✅ URL包含验证: '{expected_value}' in '{actual_url}' -> {success}")
                return success

            else:
                self.log(f"❌ 不支持的验证类型: {validation_type}")
                return False

        except Exception as e:
            self.log(f"❌ 验证执行失败: {config.get('type', 'unknown')}, 错误: {str(e)}")
            return False

    def _replace_variables(self, config: Any, variables: Dict) -> Any:
        """替换配置中的变量"""
        if isinstance(config, str):
            # 简单的变量替换 ${variable_name}
            for var_name, var_value in variables.items():
                config = config.replace(f"${{{var_name}}}", str(var_value))
            return config
        elif isinstance(config, dict):
            return {k: self._replace_variables(v, variables) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_variables(item, variables) for item in config]
        else:
            return config

    def _get_by_type(self, by_type: str) -> Any:
        """获取By类型"""
        by_type = by_type.lower()
        if by_type == "id":
            return By.ID
        elif by_type == "name":
            return By.NAME
        elif by_type == "class":
            return By.CLASS_NAME
        elif by_type == "tag":
            return By.TAG_NAME
        elif by_type == "css":
            return By.CSS_SELECTOR
        elif by_type == "xpath":
            return By.XPATH
        elif by_type == "link_text":
            return By.LINK_TEXT
        elif by_type == "partial_link_text":
            return By.PARTIAL_LINK_TEXT
        else:
            return By.CSS_SELECTOR

    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

    def quit(self):
        """退出浏览器"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None
                self.action_chains = None
                self.log("🔒 浏览器已退出")
        except Exception as e:
            self.log(f"❌ 浏览器退出失败: {str(e)}")

    def get_session_info(self) -> Dict:
        """获取会话信息"""
        if not self.driver:
            return {}

        return {
            "browser_type": self.config.get('browser_type', 'chrome'),
            "browser_version": self.driver.capabilities.get('browserVersion', 'unknown'),
            "current_url": self.driver.current_url,
            "title": self.driver.title,
            "window_handles": len(self.driver.window_handles),
            "session_id": self.driver.session_id,
            "capabilities": self.driver.capabilities
        }