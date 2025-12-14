"""
登录模块 API 接口测试
接口清单:
- POST /login - 用户登录
- GET /userinfo - 获取当前用户信息
- POST /refreshToken - 刷新Token
"""
import pytest
from tests.conftest import APIClient, API_BASE_URL, TEST_USERNAME, TEST_PASSWORD


class TestLoginAPI:
    """登录接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        yield
        self.client.close()
    
    # ==================== POST /login 登录接口测试 ====================
    
    def test_login_success(self):
        """登录 - 正确的用户名密码"""
        response = self.client.post("/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]
    
    def test_login_wrong_password(self):
        """登录 - 错误的密码"""
        response = self.client.post("/login", json={
            "username": TEST_USERNAME,
            "password": "wrong_password"
        })
        data = response.json()
        assert data["code"] == -1 or "错误" in data.get("msg", "")
    
    def test_login_wrong_username(self):
        """登录 - 不存在的用户名"""
        response = self.client.post("/login", json={
            "username": "nonexistent_user_xyz",
            "password": TEST_PASSWORD
        })
        data = response.json()
        assert data["code"] == -1 or "错误" in data.get("msg", "")
    
    def test_login_empty_username(self):
        """登录 - 空用户名"""
        response = self.client.post("/login", json={
            "username": "",
            "password": TEST_PASSWORD
        })
        assert response.status_code in [200, 422]
    
    def test_login_empty_password(self):
        """登录 - 空密码"""
        response = self.client.post("/login", json={
            "username": TEST_USERNAME,
            "password": ""
        })
        assert response.status_code in [200, 422]
    
    def test_login_missing_username(self):
        """登录 - 缺少用户名字段"""
        response = self.client.post("/login", json={
            "password": TEST_PASSWORD
        })
        assert response.status_code == 422
    
    def test_login_missing_password(self):
        """登录 - 缺少密码字段"""
        response = self.client.post("/login", json={
            "username": TEST_USERNAME
        })
        assert response.status_code == 422
    
    # ==================== GET /userinfo 获取用户信息测试 ====================
    
    def test_userinfo_success(self):
        """获取用户信息 - 已登录"""
        self.client.login()
        response = self.client.get("/userinfo")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "username" in data["data"]
    
    def test_userinfo_unauthorized(self):
        """获取用户信息 - 未登录"""
        response = self.client.get("/userinfo")
        data = response.json()
        assert data["code"] == -1 or "登录" in data.get("msg", "")
    
    def test_userinfo_invalid_token(self):
        """获取用户信息 - 无效Token"""
        self.client.session.headers.update({"Authorization": "Bearer invalid_token"})
        response = self.client.get("/userinfo")
        data = response.json()
        assert data["code"] == -1 or "无效" in data.get("msg", "") or "登录" in data.get("msg", "")
    
    # ==================== POST /refreshToken 刷新Token测试 ====================
    
    def test_refresh_token_success(self):
        """刷新Token - 有效Token"""
        self.client.login()
        response = self.client.post("/refreshToken")
        assert response.status_code == 200
        data = response.json()
        if data["code"] == 200:
            assert "access_token" in data["data"]
    
    def test_refresh_token_unauthorized(self):
        """刷新Token - 未提供Token"""
        response = self.client.post("/refreshToken")
        data = response.json()
        assert data["code"] == -1 or "认证" in data.get("msg", "") or "缺少" in data.get("msg", "")
    
    def test_refresh_token_invalid(self):
        """刷新Token - 无效Token"""
        self.client.session.headers.update({"Authorization": "Bearer invalid_token"})
        response = self.client.post("/refreshToken")
        data = response.json()
        assert data["code"] == -1 or "失败" in data.get("msg", "")
