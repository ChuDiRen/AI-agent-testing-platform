"""
测试配置文件
提供通用的 fixtures 和测试工具
"""
import os
import sys
from datetime import datetime

import pytest

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# API 测试配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
WEB_BASE_URL = os.getenv("WEB_BASE_URL", "http://localhost:5173")
TEST_USERNAME = os.getenv("TEST_USERNAME", "admin")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "admin123")


class APIClient:
    """API 测试客户端"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        import requests
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def login(self, username: str = TEST_USERNAME, password: str = TEST_PASSWORD):
        """登录获取 token"""
        response = self.session.post(
            f"{self.base_url}/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                self.token = data.get("data", {}).get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        return response
    
    def get(self, path: str, params: dict = None):
        """GET 请求"""
        return self.session.get(f"{self.base_url}{path}", params=params)
    
    def post(self, path: str, json: dict = None, data: dict = None):
        """POST 请求"""
        return self.session.post(f"{self.base_url}{path}", json=json, data=data)
    
    def put(self, path: str, json: dict = None):
        """PUT 请求"""
        return self.session.put(f"{self.base_url}{path}", json=json)
    
    def delete(self, path: str, params: dict = None):
        """DELETE 请求"""
        return self.session.delete(f"{self.base_url}{path}", params=params)
    
    def assert_success(self, response):
        """断言请求成功"""
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 200, f"API 返回错误: {data.get('msg')}"
        return data
    
    def close(self):
        """关闭会话"""
        self.session.close()


@pytest.fixture
def api_client():
    """提供已登录的 API 客户端"""
    client = APIClient()
    client.login()
    yield client
    client.close()


@pytest.fixture
def api_client_no_auth():
    """提供未登录的 API 客户端"""
    client = APIClient()
    yield client
    client.close()


@pytest.fixture
def unique_name():
    """生成唯一名称"""
    return f"test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
