"""
API Engine Pytest 配置文件
提供测试 fixtures 和配置
"""
import pytest
import allure
from apirun.extend.keywords import Keywords


@pytest.fixture(scope="function")
def api_keywords():
    """
    提供 API 关键字实例
    
    用法:
        def test_example(api_keywords):
            api_keywords.send_request(...)
    """
    keywords = Keywords()
    yield keywords
    # 清理工作（如果需要）


# Pytest 配置
def pytest_configure(config):
    """Pytest 配置钩子"""
    # 注册自定义标记
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "regression: 回归测试")
    config.addinivalue_line("markers", "api: API 测试")

