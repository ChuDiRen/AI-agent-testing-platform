from __future__ import annotations

from typing import Any

from appium import webdriver
from appium.options.common import AppiumOptions

from ..core.globalContext import g_context


class AppiumManager:
    _driver = None

    @classmethod
    def create_driver(cls, server_url: str, capabilities: dict[str, Any]):
        options = AppiumOptions()
        options.load_capabilities(capabilities)
        cls._driver = webdriver.Remote(command_executor=server_url, options=options)
        g_context().set_dict("current_driver", cls._driver)
        return cls._driver

    @classmethod
    def get_driver(cls):
        driver = g_context().get_dict("current_driver")
        if driver is not None:
            cls._driver = driver
        return cls._driver

    @classmethod
    def close(cls) -> None:
        driver = cls.get_driver()
        if driver is None:
            return
        try:
            driver.quit()
        finally:
            cls._driver = None
            g_context().set_dict("current_driver", None)
