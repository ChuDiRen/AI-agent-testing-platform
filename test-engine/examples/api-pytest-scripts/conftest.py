"""
API Pytest 测试配置文件
提供公共的 fixtures 和配置
"""
from typing import Dict

import pytest
import requests


# ===========================
# 测试环境配置
# ===========================

@pytest.fixture(scope="session")
def base_url() -> str:
    """
    API 基础 URL
    可通过环境变量或配置文件覆盖
    """
    return "http://shop-xo.hctestedu.com"


@pytest.fixture(scope="session")
def api_headers() -> Dict[str, str]:
    """
    API 请求的通用 Headers
    """
    return {
        "Content-Type": "application/json",
        "User-Agent": "TestEngine-API/1.0"
    }


# ===========================
# Session 级别的 Fixtures
# ===========================

@pytest.fixture(scope="session")
def api_session(base_url: str, api_headers: Dict[str, str]) -> requests.Session:
    """
    创建一个可复用的 requests Session
    自动维护 cookies，提高测试效率
    """
    session = requests.Session()
    session.headers.update(api_headers)
    yield session
    session.close()


@pytest.fixture(scope="session")
def login_token(api_session: requests.Session, base_url: str) -> str:
    """
    登录并获取 token
    在整个测试会话中复用
    """
    login_url = f"{base_url}/index.php?s=/api/user/login"
    login_data = {
        "accounts": "hami",
        "pwd": "123456",
        "type": "username"
    }
    
    response = api_session.post(login_url, json=login_data)
    assert response.status_code == 200, f"登录失败: {response.text}"
    
    result = response.json()
    assert result.get("code") == 0, f"登录失败: {result.get('msg')}"
    
    return result.get("data", {}).get("token", "")


# ===========================
# Function 级别的 Fixtures
# ===========================

@pytest.fixture
def api_client(api_session: requests.Session, base_url: str, login_token: str):
    """
    已认证的 API 客户端
    每个测试函数都会创建新的客户端实例
    """
    class APIClient:
        def __init__(self, session: requests.Session, base_url: str, token: str):
            self.session = session
            self.base_url = base_url
            self.token = token
        
        def get(self, endpoint: str, **kwargs) -> requests.Response:
            """发送 GET 请求"""
            url = f"{self.base_url}{endpoint}"
            return self.session.get(url, **kwargs)
        
        def post(self, endpoint: str, **kwargs) -> requests.Response:
            """发送 POST 请求"""
            url = f"{self.base_url}{endpoint}"
            return self.session.post(url, **kwargs)
        
        def put(self, endpoint: str, **kwargs) -> requests.Response:
            """发送 PUT 请求"""
            url = f"{self.base_url}{endpoint}"
            return self.session.put(url, **kwargs)
        
        def delete(self, endpoint: str, **kwargs) -> requests.Response:
            """发送 DELETE 请求"""
            url = f"{self.base_url}{endpoint}"
            return self.session.delete(url, **kwargs)
    
    return APIClient(api_session, base_url, login_token)


# ===========================
# Pytest Hooks（可选）
# ===========================

def pytest_configure(config):
    """
    Pytest 配置钩子
    可以在这里添加自定义标记等
    """
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试用例"
    )
    config.addinivalue_line(
        "markers", "regression: 回归测试用例"
    )
    config.addinivalue_line(
        "markers", "slow: 运行较慢的测试用例"
    )


def pytest_collection_modifyitems(items):
    """
    修改测试用例集合
    解决中文测试名称显示问题
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

