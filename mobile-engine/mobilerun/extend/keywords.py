from __future__ import annotations

import os
import time
from typing import Any

import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from ..core.globalContext import g_context
from ..utils.AppiumManager import AppiumManager


class Keywords:
    """Mobile 自动化测试关键字类 (Appium 版本)"""
    def _get_driver(self):
        driver = AppiumManager.get_driver()
        if driver is None:
            raise RuntimeError("Appium session 未启动，请先使用 open_app 关键字")
        return driver

    def _get_by(self, locator_type: str):
        t = (locator_type or "").lower()
        if t in ("id", "resource_id"):
            return AppiumBy.ID
        if t in ("accessibility_id", "accessibility", "aid"):
            return AppiumBy.ACCESSIBILITY_ID
        if t == "xpath":
            return AppiumBy.XPATH
        if t in ("class", "class_name"):
            return AppiumBy.CLASS_NAME
        if t in ("android_uiautomator", "uiautomator"):
            return AppiumBy.ANDROID_UIAUTOMATOR
        if t in ("ios_predicate", "predicate"):
            return AppiumBy.IOS_PREDICATE
        if t in ("ios_class_chain", "class_chain"):
            return AppiumBy.IOS_CLASS_CHAIN
        if t in ("name",):
            return AppiumBy.NAME
        return AppiumBy.XPATH

    def _find_element(self, locator_type: str, element: str, timeout: int | None = None):
        driver = self._get_driver()
        by = self._get_by(locator_type)
        if timeout is not None:
            wait = WebDriverWait(driver, timeout)
            return wait.until(lambda d: d.find_element(by, element))
        return driver.find_element(by, element)

    def _attach_screenshot(self, name: str) -> None:
        try:
            driver = self._get_driver()
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            screenshot_dir = os.path.join(project_root, "reports", "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            ts = time.strftime("%Y%m%d_%H%M%S")
            safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in name)
            path = os.path.join(screenshot_dir, f"{safe}_{ts}.png")
            driver.get_screenshot_as_file(path)
            with open(path, "rb") as f:
                allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)
        except Exception:
            pass

    def _attach_page_source(self, name: str) -> None:
        try:
            driver = self._get_driver()
            source = driver.page_source
            allure.attach(source, name=name, attachment_type=allure.attachment_type.XML)
        except Exception:
            pass

    @allure.step("启动 App")
    def open_app(self, **kwargs: Any):
        if AppiumManager.get_driver() is not None:
            return

        platform = (kwargs.get("platform") or g_context().get_dict("PLATFORM") or g_context().get_dict("platform") or "android").lower()
        server = kwargs.get("server") or g_context().get_dict("APPIUM_SERVER") or g_context().get_dict("server") or "http://127.0.0.1:4723"
        device_name = kwargs.get("deviceName") or g_context().get_dict("deviceName") or g_context().get_dict("DEVICE_NAME")
        udid = kwargs.get("udid") or g_context().get_dict("udid") or g_context().get_dict("UDID")
        app = kwargs.get("app") or g_context().get_dict("app") or g_context().get_dict("APP")
        bundle_id = kwargs.get("bundleId") or g_context().get_dict("bundleId") or g_context().get_dict("BUNDLE_ID")
        no_reset_raw = kwargs.get("noReset", g_context().get_dict("noReset"))
        no_reset = True if no_reset_raw is None else (no_reset_raw if isinstance(no_reset_raw, bool) else str(no_reset_raw).lower() in ("true", "1", "yes"))
        automation_name = kwargs.get("automationName")

        caps: dict[str, Any] = {}
        if platform == "android":
            caps["platformName"] = "Android"
            caps["appium:automationName"] = automation_name or "uiautomator2"
            if app:
                caps["appium:app"] = app
        elif platform == "ios":
            caps["platformName"] = "iOS"
            caps["appium:automationName"] = automation_name or "xcuitest"
            if bundle_id:
                caps["appium:bundleId"] = bundle_id
            if app:
                caps["appium:app"] = app
        else:
            raise ValueError(f"不支持的平台: {platform}")

        if device_name:
            caps["appium:deviceName"] = device_name
        if udid:
            caps["appium:udid"] = udid
        caps["appium:noReset"] = no_reset
        if (nct := kwargs.get("newCommandTimeout")) is not None:
            caps["appium:newCommandTimeout"] = int(nct)

        g_context().set_dict("APPIUM_SERVER", server)
        g_context().set_dict("PLATFORM", platform)
        g_context().set_dict("_caps", caps)

        AppiumManager.create_driver(server, caps)

    @allure.step("关闭 App")
    def close_app(self, **kwargs: Any):
        AppiumManager.close()

    @allure.step("点击元素")
    def tap_element(self, **kwargs: Any):
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        wait_time = kwargs.get("wait_time")
        timeout = int(wait_time) if wait_time is not None else None

        try:
            el = self._find_element(locator_type, element, timeout=timeout)
            el.click()
        except Exception as e:
            self._attach_screenshot(f"点击失败_{locator_type}_{element}")
            self._attach_page_source(f"页面源码_{locator_type}_{element}")
            raise e

    @allure.step("输入文本")
    def input_text(self, **kwargs: Any):
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        text = "" if kwargs.get("text") is None else str(kwargs.get("text"))
        clear_raw = kwargs.get("clear", True)
        clear = clear_raw if isinstance(clear_raw, bool) else str(clear_raw).lower() in ("true", "1", "yes")
        wait_time = kwargs.get("wait_time")
        timeout = int(wait_time) if wait_time is not None else None

        try:
            el = self._find_element(locator_type, element, timeout=timeout)
            if clear:
                try:
                    el.clear()
                except Exception:
                    pass
            el.send_keys(text)
        except Exception as e:
            self._attach_screenshot(f"输入失败_{locator_type}_{element}")
            self._attach_page_source(f"页面源码_{locator_type}_{element}")
            raise e

    @allure.step("等待元素")
    def wait_for_element(self, **kwargs: Any):
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 15))
        self._find_element(locator_type, element, timeout=timeout)

    @allure.step("滑动")
    def swipe(self, **kwargs: Any):
        direction = (kwargs.get("direction") or "up").lower()
        percent = float(kwargs.get("percent", 0.7))
        duration = int(kwargs.get("duration", 600))

        driver = self._get_driver()
        size = driver.get_window_size()
        w, h = size["width"], size["height"]

        if direction == "up":
            start_x, start_y = w // 2, int(h * 0.8)
            end_x, end_y = w // 2, int(h * (0.8 - percent))
        elif direction == "down":
            start_x, start_y = w // 2, int(h * 0.2)
            end_x, end_y = w // 2, int(h * (0.2 + percent))
        elif direction == "left":
            start_x, start_y = int(w * 0.8), h // 2
            end_x, end_y = int(w * (0.8 - percent)), h // 2
        elif direction == "right":
            start_x, start_y = int(w * 0.2), h // 2
            end_x, end_y = int(w * (0.2 + percent)), h // 2
        else:
            raise ValueError(f"不支持的方向: {direction}")

        driver.swipe(start_x, start_y, end_x, end_y, duration)

    @allure.step("返回")
    def back(self, **kwargs: Any):
        self._get_driver().back()

    @allure.step("截图")
    def take_screenshot(self, **kwargs: Any):
        filename = kwargs.get("filename")
        driver = self._get_driver()

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        screenshot_dir = os.path.join(project_root, "reports", "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        if not filename:
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{ts}.png"

        if not str(filename).endswith(".png"):
            filename = f"{filename}.png"

        path = os.path.join(screenshot_dir, str(filename))
        driver.get_screenshot_as_file(path)
        with open(path, "rb") as f:
            allure.attach(f.read(), name=str(filename), attachment_type=allure.attachment_type.PNG)

    @allure.step("断言元素可见")
    def assert_element_visible(self, **kwargs: Any):
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 10))

        try:
            self._find_element(locator_type, element, timeout=timeout)
            print(f"✓ 断言成功: 元素可见 {locator_type}={element}")
        except Exception as e:
            self._attach_screenshot(f"断言失败_{locator_type}_{element}")
            self._attach_page_source(f"页面源码_{locator_type}_{element}")
            raise AssertionError(f"断言失败: 元素不可见 {locator_type}={element}") from e

    # ==================== 元素操作扩展 ====================

    @allure.step("清空文本")
    def clear_text(self, **kwargs: Any):
        """清空元素文本"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        wait_time = kwargs.get("wait_time")
        timeout = int(wait_time) if wait_time is not None else None

        try:
            el = self._find_element(locator_type, element, timeout=timeout)
            el.clear()
            print(f"已清空文本: {locator_type}={element}")
        except Exception as e:
            self._attach_screenshot(f"清空失败_{locator_type}_{element}")
            raise e

    @allure.step("获取文本")
    def get_text(self, **kwargs: Any):
        """获取元素文本并保存到变量"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        variable_name = kwargs.get("variable_name")
        wait_time = kwargs.get("wait_time")
        timeout = int(wait_time) if wait_time is not None else None

        el = self._find_element(locator_type, element, timeout=timeout)
        text = el.text or ""

        if variable_name:
            g_context().set_dict(variable_name, text)
            print(f"已获取文本并保存到变量 {variable_name}: {text}")
        else:
            print(f"已获取文本: {text}")

        return text

    @allure.step("获取属性")
    def get_attribute(self, **kwargs: Any):
        """获取元素属性并保存到变量"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        attribute_name = kwargs.get("attribute_name")
        variable_name = kwargs.get("variable_name")
        wait_time = kwargs.get("wait_time")
        timeout = int(wait_time) if wait_time is not None else None

        el = self._find_element(locator_type, element, timeout=timeout)
        attr_value = el.get_attribute(attribute_name)

        if variable_name:
            g_context().set_dict(variable_name, attr_value)
            print(f"已获取属性 {attribute_name} 并保存到变量 {variable_name}: {attr_value}")
        else:
            print(f"已获取属性 {attribute_name}: {attr_value}")

        return attr_value

    @allure.step("长按元素")
    def long_press(self, **kwargs: Any):
        """长按元素"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        duration = int(kwargs.get("duration", 1000))
        wait_time = kwargs.get("wait_time")
        timeout = int(wait_time) if wait_time is not None else None

        try:
            el = self._find_element(locator_type, element, timeout=timeout)
            # 使用 TouchAction 或 W3C Actions
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.webdriver.common.actions.pointer_input import PointerInput
            from selenium.webdriver.common.actions import interaction

            driver = self._get_driver()
            actions = ActionChains(driver)
            actions.click_and_hold(el).pause(duration / 1000).release().perform()
            print(f"已长按元素: {locator_type}={element}, 持续 {duration}ms")
        except Exception as e:
            self._attach_screenshot(f"长按失败_{locator_type}_{element}")
            raise e

    @allure.step("双击元素")
    def double_tap(self, **kwargs: Any):
        """双击元素"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        wait_time = kwargs.get("wait_time")
        timeout = int(wait_time) if wait_time is not None else None

        try:
            el = self._find_element(locator_type, element, timeout=timeout)
            from selenium.webdriver.common.action_chains import ActionChains
            driver = self._get_driver()
            actions = ActionChains(driver)
            actions.double_click(el).perform()
            print(f"已双击元素: {locator_type}={element}")
        except Exception as e:
            self._attach_screenshot(f"双击失败_{locator_type}_{element}")
            raise e

    @allure.step("滚动到元素")
    def scroll_to_element(self, **kwargs: Any):
        """滚动直到元素可见"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        max_swipes = int(kwargs.get("max_swipes", 10))
        direction = (kwargs.get("direction") or "up").lower()

        driver = self._get_driver()
        by = self._get_by(locator_type)

        for i in range(max_swipes):
            try:
                el = driver.find_element(by, element)
                if el.is_displayed():
                    print(f"已滚动到元素: {locator_type}={element}")
                    return el
            except Exception:
                pass
            self.swipe(direction=direction, percent=0.5)

        raise Exception(f"滚动 {max_swipes} 次后仍未找到元素: {locator_type}={element}")

    @allure.step("拖拽元素")
    def drag_and_drop(self, **kwargs: Any):
        """拖拽元素"""
        source_locator_type = kwargs.get("source_locator_type")
        source_element = kwargs.get("source_element")
        target_locator_type = kwargs.get("target_locator_type")
        target_element = kwargs.get("target_element")

        source = self._find_element(source_locator_type, source_element)
        target = self._find_element(target_locator_type, target_element)

        driver = self._get_driver()
        driver.drag_and_drop(source, target)
        print(f"已拖拽: {source_locator_type}={source_element} -> {target_locator_type}={target_element}")

    @allure.step("坐标点击")
    def tap_coordinates(self, **kwargs: Any):
        """点击指定坐标"""
        x = int(kwargs.get("x", 0))
        y = int(kwargs.get("y", 0))

        driver = self._get_driver()
        driver.tap([(x, y)])
        print(f"已点击坐标: ({x}, {y})")

    @allure.step("坐标滑动")
    def swipe_coordinates(self, **kwargs: Any):
        """从坐标滑动到坐标"""
        start_x = int(kwargs.get("start_x", 0))
        start_y = int(kwargs.get("start_y", 0))
        end_x = int(kwargs.get("end_x", 0))
        end_y = int(kwargs.get("end_y", 0))
        duration = int(kwargs.get("duration", 600))

        driver = self._get_driver()
        driver.swipe(start_x, start_y, end_x, end_y, duration)
        print(f"已滑动: ({start_x}, {start_y}) -> ({end_x}, {end_y})")

    @allure.step("捏合缩放")
    def pinch(self, **kwargs: Any):
        """捏合缩放（缩小）"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        percent = int(kwargs.get("percent", 200))
        steps = int(kwargs.get("steps", 50))

        el = self._find_element(locator_type, element) if locator_type and element else None
        driver = self._get_driver()

        if el:
            driver.pinch(el, percent, steps)
        else:
            # 全屏捏合
            size = driver.get_window_size()
            driver.pinch(element=None, percent=percent, steps=steps)
        print(f"已执行捏合缩放")

    @allure.step("放大")
    def zoom(self, **kwargs: Any):
        """放大"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        percent = int(kwargs.get("percent", 200))
        steps = int(kwargs.get("steps", 50))

        el = self._find_element(locator_type, element) if locator_type and element else None
        driver = self._get_driver()

        if el:
            driver.zoom(el, percent, steps)
        else:
            driver.zoom(element=None, percent=percent, steps=steps)
        print(f"已执行放大")

    # ==================== 等待操作扩展 ====================

    @allure.step("等待元素可见")
    def wait_for_element_visible(self, **kwargs: Any):
        """等待元素可见"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 15))

        driver = self._get_driver()
        by = self._get_by(locator_type)

        from selenium.webdriver.support import expected_conditions as EC
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.visibility_of_element_located((by, element)))
        print(f"元素已可见: {locator_type}={element}")

    @allure.step("等待元素消失")
    def wait_for_element_gone(self, **kwargs: Any):
        """等待元素消失"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 15))

        driver = self._get_driver()
        by = self._get_by(locator_type)

        from selenium.webdriver.support import expected_conditions as EC
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.invisibility_of_element_located((by, element)))
        print(f"元素已消失: {locator_type}={element}")

    @allure.step("等待元素可点击")
    def wait_for_element_clickable(self, **kwargs: Any):
        """等待元素可点击"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 15))

        driver = self._get_driver()
        by = self._get_by(locator_type)

        from selenium.webdriver.support import expected_conditions as EC
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.element_to_be_clickable((by, element)))
        print(f"元素已可点击: {locator_type}={element}")

    @allure.step("等待: {time}秒")
    def sleep(self, **kwargs: Any):
        """强制等待"""
        sleep_time = float(kwargs.get("time", 1))
        import time as time_module
        time_module.sleep(sleep_time)
        print(f"已等待 {sleep_time} 秒")

    # ==================== 断言操作扩展 ====================

    @allure.step("断言元素不可见")
    def assert_element_not_visible(self, **kwargs: Any):
        """断言元素不可见"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 5))

        driver = self._get_driver()
        by = self._get_by(locator_type)

        try:
            from selenium.webdriver.support import expected_conditions as EC
            wait = WebDriverWait(driver, timeout)
            wait.until(EC.invisibility_of_element_located((by, element)))
            print(f"✓ 断言成功: 元素不可见 {locator_type}={element}")
        except Exception as e:
            self._attach_screenshot(f"断言失败_元素可见_{locator_type}_{element}")
            raise AssertionError(f"断言失败: 元素可见 {locator_type}={element}") from e

    @allure.step("断言文本相等")
    def assert_text_equals(self, **kwargs: Any):
        """断言元素文本相等"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        expected_text = str(kwargs.get("expected_text", ""))
        wait_time = kwargs.get("wait_time")
        timeout = int(wait_time) if wait_time is not None else None

        el = self._find_element(locator_type, element, timeout=timeout)
        actual_text = el.text or ""

        if actual_text == expected_text:
            print(f"✓ 断言成功: 文本相等 '{expected_text}'")
        else:
            self._attach_screenshot(f"断言失败_文本不相等_{locator_type}_{element}")
            raise AssertionError(f"文本不相等: 期望'{expected_text}', 实际'{actual_text}'")

    @allure.step("断言文本包含")
    def assert_text_contains(self, **kwargs: Any):
        """断言元素文本包含指定内容"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        expected_text = str(kwargs.get("expected_text", ""))
        wait_time = kwargs.get("wait_time")
        timeout = int(wait_time) if wait_time is not None else None

        el = self._find_element(locator_type, element, timeout=timeout)
        actual_text = el.text or ""

        if expected_text in actual_text:
            print(f"✓ 断言成功: 文本包含 '{expected_text}'")
        else:
            self._attach_screenshot(f"断言失败_文本不包含_{locator_type}_{element}")
            raise AssertionError(f"文本不包含: 期望包含'{expected_text}', 实际'{actual_text}'")

    @allure.step("断言元素存在")
    def assert_element_exists(self, **kwargs: Any):
        """断言元素存在（DOM 中存在，不一定可见）"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 10))

        try:
            self._find_element(locator_type, element, timeout=timeout)
            print(f"✓ 断言成功: 元素存在 {locator_type}={element}")
        except Exception as e:
            self._attach_screenshot(f"断言失败_元素不存在_{locator_type}_{element}")
            raise AssertionError(f"断言失败: 元素不存在 {locator_type}={element}") from e

    @allure.step("断言元素不存在")
    def assert_element_not_exists(self, **kwargs: Any):
        """断言元素不存在"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 3))

        driver = self._get_driver()
        by = self._get_by(locator_type)

        try:
            driver.implicitly_wait(timeout)
            elements = driver.find_elements(by, element)
            driver.implicitly_wait(0)
            if len(elements) == 0:
                print(f"✓ 断言成功: 元素不存在 {locator_type}={element}")
            else:
                self._attach_screenshot(f"断言失败_元素存在_{locator_type}_{element}")
                raise AssertionError(f"断言失败: 元素存在 {locator_type}={element}")
        except Exception as e:
            if "断言失败" in str(e):
                raise
            print(f"✓ 断言成功: 元素不存在 {locator_type}={element}")

    @allure.step("断言元素启用")
    def assert_element_enabled(self, **kwargs: Any):
        """断言元素启用（可交互）"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 10))

        el = self._find_element(locator_type, element, timeout=timeout)
        if el.is_enabled():
            print(f"✓ 断言成功: 元素启用 {locator_type}={element}")
        else:
            self._attach_screenshot(f"断言失败_元素禁用_{locator_type}_{element}")
            raise AssertionError(f"断言失败: 元素禁用 {locator_type}={element}")

    @allure.step("断言元素选中")
    def assert_element_selected(self, **kwargs: Any):
        """断言元素选中"""
        locator_type = kwargs.get("locator_type")
        element = kwargs.get("element")
        timeout = int(kwargs.get("timeout", 10))

        el = self._find_element(locator_type, element, timeout=timeout)
        if el.is_selected():
            print(f"✓ 断言成功: 元素选中 {locator_type}={element}")
        else:
            self._attach_screenshot(f"断言失败_元素未选中_{locator_type}_{element}")
            raise AssertionError(f"断言失败: 元素未选中 {locator_type}={element}")

    # ==================== 设备操作 ====================

    @allure.step("Home 键")
    def press_home(self, **kwargs: Any):
        """按 Home 键"""
        driver = self._get_driver()
        platform = (g_context().get_dict("PLATFORM") or "android").lower()
        if platform == "android":
            driver.press_keycode(3)  # KEYCODE_HOME
        else:
            # iOS 使用 mobile: pressButton
            driver.execute_script("mobile: pressButton", {"name": "home"})
        print("已按 Home 键")

    @allure.step("锁屏")
    def lock_device(self, **kwargs: Any):
        """锁定设备"""
        duration = int(kwargs.get("duration", 0))
        driver = self._get_driver()
        driver.lock(duration)
        print(f"设备已锁定 {duration}秒")

    @allure.step("解锁")
    def unlock_device(self, **kwargs: Any):
        """解锁设备"""
        driver = self._get_driver()
        driver.unlock()
        print("设备已解锁")

    @allure.step("摇一摇")
    def shake_device(self, **kwargs: Any):
        """摇一摇设备"""
        driver = self._get_driver()
        driver.shake()
        print("已摇一摇")

    @allure.step("旋转屏幕")
    def rotate_screen(self, **kwargs: Any):
        """旋转屏幕"""
        orientation = (kwargs.get("orientation") or "PORTRAIT").upper()
        driver = self._get_driver()
        driver.orientation = orientation
        print(f"屏幕已旋转到: {orientation}")

    @allure.step("获取屏幕方向")
    def get_orientation(self, **kwargs: Any):
        """获取屏幕方向"""
        variable_name = kwargs.get("variable_name")
        driver = self._get_driver()
        orientation = driver.orientation

        if variable_name:
            g_context().set_dict(variable_name, orientation)
            print(f"屏幕方向已保存到变量 {variable_name}: {orientation}")
        else:
            print(f"屏幕方向: {orientation}")

        return orientation

    @allure.step("隐藏键盘")
    def hide_keyboard(self, **kwargs: Any):
        """隐藏软键盘"""
        driver = self._get_driver()
        try:
            driver.hide_keyboard()
            print("键盘已隐藏")
        except Exception:
            print("键盘已隐藏或不存在")

    @allure.step("检查键盘是否显示")
    def is_keyboard_shown(self, **kwargs: Any):
        """检查键盘是否显示"""
        variable_name = kwargs.get("variable_name")
        driver = self._get_driver()
        shown = driver.is_keyboard_shown()

        if variable_name:
            g_context().set_dict(variable_name, shown)
            print(f"键盘状态已保存到变量 {variable_name}: {shown}")
        else:
            print(f"键盘是否显示: {shown}")

        return shown

    @allure.step("按键")
    def press_keycode(self, **kwargs: Any):
        """按指定键码（Android）"""
        keycode = int(kwargs.get("keycode", 0))
        metastate = kwargs.get("metastate")

        driver = self._get_driver()
        if metastate:
            driver.press_keycode(keycode, metastate=int(metastate))
        else:
            driver.press_keycode(keycode)
        print(f"已按键码: {keycode}")

    @allure.step("长按键")
    def long_press_keycode(self, **kwargs: Any):
        """长按指定键码（Android）"""
        keycode = int(kwargs.get("keycode", 0))
        metastate = kwargs.get("metastate")

        driver = self._get_driver()
        if metastate:
            driver.long_press_keycode(keycode, metastate=int(metastate))
        else:
            driver.long_press_keycode(keycode)
        print(f"已长按键码: {keycode}")

    # ==================== App 操作 ====================

    @allure.step("启动 Activity")
    def start_activity(self, **kwargs: Any):
        """启动指定 Activity（Android）"""
        app_package = kwargs.get("app_package")
        app_activity = kwargs.get("app_activity")

        driver = self._get_driver()
        driver.start_activity(app_package, app_activity)
        print(f"已启动 Activity: {app_package}/{app_activity}")

    @allure.step("获取当前 Activity")
    def get_current_activity(self, **kwargs: Any):
        """获取当前 Activity（Android）"""
        variable_name = kwargs.get("variable_name")
        driver = self._get_driver()
        activity = driver.current_activity

        if variable_name:
            g_context().set_dict(variable_name, activity)
            print(f"当前 Activity 已保存到变量 {variable_name}: {activity}")
        else:
            print(f"当前 Activity: {activity}")

        return activity

    @allure.step("获取当前 Package")
    def get_current_package(self, **kwargs: Any):
        """获取当前 Package（Android）"""
        variable_name = kwargs.get("variable_name")
        driver = self._get_driver()
        package = driver.current_package

        if variable_name:
            g_context().set_dict(variable_name, package)
            print(f"当前 Package 已保存到变量 {variable_name}: {package}")
        else:
            print(f"当前 Package: {package}")

        return package

    @allure.step("后台运行 App")
    def background_app(self, **kwargs: Any):
        """将 App 放到后台"""
        duration = int(kwargs.get("duration", 5))
        driver = self._get_driver()
        driver.background_app(duration)
        print(f"App 已后台运行 {duration} 秒")

    @allure.step("重置 App")
    def reset_app(self, **kwargs: Any):
        """重置 App"""
        driver = self._get_driver()
        driver.reset()
        print("App 已重置")

    @allure.step("安装 App")
    def install_app(self, **kwargs: Any):
        """安装 App"""
        app_path = kwargs.get("app_path")
        driver = self._get_driver()
        driver.install_app(app_path)
        print(f"App 已安装: {app_path}")

    @allure.step("卸载 App")
    def remove_app(self, **kwargs: Any):
        """卸载 App"""
        app_id = kwargs.get("app_id")
        driver = self._get_driver()
        driver.remove_app(app_id)
        print(f"App 已卸载: {app_id}")

    @allure.step("检查 App 是否安装")
    def is_app_installed(self, **kwargs: Any):
        """检查 App 是否安装"""
        app_id = kwargs.get("app_id")
        variable_name = kwargs.get("variable_name")
        driver = self._get_driver()
        installed = driver.is_app_installed(app_id)

        if variable_name:
            g_context().set_dict(variable_name, installed)
            print(f"App 安装状态已保存到变量 {variable_name}: {installed}")
        else:
            print(f"App {app_id} 是否安装: {installed}")

        return installed

    @allure.step("终止 App")
    def terminate_app(self, **kwargs: Any):
        """终止 App"""
        app_id = kwargs.get("app_id")
        driver = self._get_driver()
        driver.terminate_app(app_id)
        print(f"App 已终止: {app_id}")

    @allure.step("激活 App")
    def activate_app(self, **kwargs: Any):
        """激活 App（切换到前台）"""
        app_id = kwargs.get("app_id")
        driver = self._get_driver()
        driver.activate_app(app_id)
        print(f"App 已激活: {app_id}")

    @allure.step("获取 App 状态")
    def query_app_state(self, **kwargs: Any):
        """获取 App 状态"""
        app_id = kwargs.get("app_id")
        variable_name = kwargs.get("variable_name")
        driver = self._get_driver()
        state = driver.query_app_state(app_id)

        if variable_name:
            g_context().set_dict(variable_name, state)
            print(f"App 状态已保存到变量 {variable_name}: {state}")
        else:
            print(f"App {app_id} 状态: {state}")

        return state

    # ==================== Context 切换 ====================

    @allure.step("获取所有 Context")
    def get_contexts(self, **kwargs: Any):
        """获取所有可用 Context"""
        variable_name = kwargs.get("variable_name")
        driver = self._get_driver()
        contexts = driver.contexts

        if variable_name:
            g_context().set_dict(variable_name, contexts)
            print(f"Contexts 已保存到变量 {variable_name}: {contexts}")
        else:
            print(f"可用 Contexts: {contexts}")

        return contexts

    @allure.step("切换 Context")
    def switch_context(self, **kwargs: Any):
        """切换 Context（Native/WebView）"""
        context_name = kwargs.get("context_name")
        driver = self._get_driver()
        driver.switch_to.context(context_name)
        print(f"已切换到 Context: {context_name}")

    @allure.step("获取当前 Context")
    def get_current_context(self, **kwargs: Any):
        """获取当前 Context"""
        variable_name = kwargs.get("variable_name")
        driver = self._get_driver()
        context = driver.current_context

        if variable_name:
            g_context().set_dict(variable_name, context)
            print(f"当前 Context 已保存到变量 {variable_name}: {context}")
        else:
            print(f"当前 Context: {context}")

        return context

    # ==================== 通知与剪贴板 ====================

    @allure.step("打开通知栏")
    def open_notifications(self, **kwargs: Any):
        """打开通知栏（Android）"""
        driver = self._get_driver()
        driver.open_notifications()
        print("已打开通知栏")

    @allure.step("获取剪贴板")
    def get_clipboard(self, **kwargs: Any):
        """获取剪贴板内容"""
        variable_name = kwargs.get("variable_name")
        driver = self._get_driver()
        content = driver.get_clipboard_text()

        if variable_name:
            g_context().set_dict(variable_name, content)
            print(f"剪贴板内容已保存到变量 {variable_name}: {content}")
        else:
            print(f"剪贴板内容: {content}")

        return content

    @allure.step("设置剪贴板")
    def set_clipboard(self, **kwargs: Any):
        """设置剪贴板内容"""
        content = str(kwargs.get("content", ""))
        driver = self._get_driver()
        driver.set_clipboard_text(content)
        print(f"已设置剪贴板: {content}")

    # ==================== 文件操作 ====================

    @allure.step("推送文件")
    def push_file(self, **kwargs: Any):
        """推送文件到设备"""
        remote_path = kwargs.get("remote_path")
        local_path = kwargs.get("local_path")

        import base64
        with open(local_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")

        driver = self._get_driver()
        driver.push_file(remote_path, data)
        print(f"已推送文件: {local_path} -> {remote_path}")

    @allure.step("拉取文件")
    def pull_file(self, **kwargs: Any):
        """从设备拉取文件"""
        remote_path = kwargs.get("remote_path")
        local_path = kwargs.get("local_path")

        driver = self._get_driver()
        data = driver.pull_file(remote_path)

        import base64
        with open(local_path, "wb") as f:
            f.write(base64.b64decode(data))

        print(f"已拉取文件: {remote_path} -> {local_path}")

    # ==================== 页面源码与截图 ====================

    @allure.step("获取页面源码")
    def get_page_source(self, **kwargs: Any):
        """获取页面源码"""
        variable_name = kwargs.get("variable_name")
        save_to_file = kwargs.get("save_to_file")

        driver = self._get_driver()
        source = driver.page_source

        if variable_name:
            g_context().set_dict(variable_name, source)
            print(f"页面源码已保存到变量 {variable_name}")

        if save_to_file:
            with open(save_to_file, "w", encoding="utf-8") as f:
                f.write(source)
            print(f"页面源码已保存到文件: {save_to_file}")

        # 附加到 Allure 报告
        allure.attach(source, name="page_source", attachment_type=allure.attachment_type.XML)

        return source

    @allure.step("全屏截图")
    def take_full_screenshot(self, **kwargs: Any):
        """全屏截图并附加到报告"""
        filename = kwargs.get("filename")
        driver = self._get_driver()

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        screenshot_dir = os.path.join(project_root, "reports", "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        if not filename:
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = f"fullscreen_{ts}.png"

        if not str(filename).endswith(".png"):
            filename = f"{filename}.png"

        path = os.path.join(screenshot_dir, str(filename))
        driver.get_screenshot_as_file(path)

        with open(path, "rb") as f:
            allure.attach(f.read(), name=str(filename), attachment_type=allure.attachment_type.PNG)

        print(f"已截图: {path}")
        return path

    # ==================== 变量操作 ====================

    @allure.step("设置变量")
    def set_variable(self, **kwargs: Any):
        """设置全局变量"""
        variable_name = kwargs.get("variable_name")
        value = kwargs.get("value")
        g_context().set_dict(variable_name, value)
        print(f"已设置变量 {variable_name} = {value}")

    @allure.step("获取变量")
    def get_variable(self, **kwargs: Any):
        """获取全局变量"""
        variable_name = kwargs.get("variable_name")
        value = g_context().get_dict(variable_name)
        print(f"变量 {variable_name} = {value}")
        return value

    @allure.step("断言变量相等")
    def assert_variable_equals(self, **kwargs: Any):
        """断言变量值相等"""
        variable_name = kwargs.get("variable_name")
        expected_value = kwargs.get("expected_value")

        actual_value = g_context().get_dict(variable_name)

        if str(actual_value) == str(expected_value):
            print(f"✓ 断言成功: 变量 {variable_name} = {expected_value}")
        else:
            raise AssertionError(f"断言失败: 变量 {variable_name} 期望'{expected_value}', 实际'{actual_value}'")

    # ==================== Python 脚本执行 ====================

    @allure.step("执行Python脚本: {script_path}")
    def run_script(self, **kwargs):
        """
        执行 Python 脚本文件
        
        参数:
            script_path: 脚本文件路径（绝对路径或相对于用例目录的路径）
            function_name: 要调用的函数名（可选，如果不指定则执行整个脚本）
            variable_name: 保存返回值到变量（可选）
            其他参数: 将作为函数参数传递
        """
        from .script.run_script import exec_script_file
        
        script_path = kwargs.pop("script_path", None)
        function_name = kwargs.pop("function_name", None)
        variable_name = kwargs.pop("variable_name", None)
        kwargs.pop("关键字", None)
        
        if not script_path:
            raise ValueError("必须指定 script_path 参数")
        
        # 获取上下文
        context = g_context().show_dict()
        
        # 执行脚本
        result = exec_script_file(
            script_path=script_path,
            context=context,
            caseinfo=None,
            function_name=function_name,
            **kwargs
        )
        
        # 保存返回值
        if variable_name and result is not None:
            g_context().set_dict(variable_name, result)
            print(f"脚本返回值已保存到变量 {variable_name}: {result}")
        
        return result

    @allure.step("执行Python代码")
    def run_code(self, **kwargs):
        """
        执行 Python 代码片段
        
        参数:
            code: Python 代码字符串
            variable_name: 保存返回值到变量（可选，代码中使用 __result__ = xxx 设置返回值）
        """
        from .script.run_script import exec_script
        
        code = kwargs.get("code", "")
        variable_name = kwargs.get("variable_name")
        
        if not code:
            raise ValueError("必须指定 code 参数")
        
        # 获取上下文
        context = g_context().show_dict()
        
        # 执行代码
        result = exec_script(code, context)
        
        # 保存返回值
        if variable_name and result is not None:
            g_context().set_dict(variable_name, result)
            print(f"代码返回值已保存到变量 {variable_name}: {result}")
        
        return result
