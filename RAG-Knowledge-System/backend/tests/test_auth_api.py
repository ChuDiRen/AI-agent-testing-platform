"""
认证 API 测试

测试用户登录、注册、登出、token验证等功能
"""
import pytest
from fastapi.testclient import TestClient


class TestAuthAPI:
    """认证API测试类"""

    def test_login_success(self, client, test_admin_user):
        """测试成功登录"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin_test",
                "password": "admin123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "admin_test"

    def test_login_wrong_password(self, client, test_admin_user):
        """测试密码错误"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin_test",
                "password": "wrong_password"
            }
        )

        assert response.status_code == 401

    def test_login_user_not_found(self, client):
        """测试用户不存在"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent_user",
                "password": "password123"
            }
        )

        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        """测试缺少字段"""
        # 缺少用户名
        response = client.post(
            "/api/v1/auth/login",
            json={"password": "password123"}
        )
        assert response.status_code == 422

        # 缺少密码
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin_test"}
        )
        assert response.status_code == 422

    def test_register_success(self, client):
        """测试成功注册"""
        user_data = {
            "username": "new_user",
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "新用户"
        }

        response = client.post(
            "/api/v1/auth/register",
            json=user_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "new_user"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data  # 密码不应返回

    def test_register_duplicate_username(self, client, test_admin_user):
        """测试用户名重复"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "admin_test",  # 已存在的用户名
                "email": "different@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 400

    def test_register_duplicate_email(self, client, test_admin_user):
        """测试邮箱重复"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "different_user",
                "email": test_admin_user.email,  # 已存在的邮箱
                "password": "password123"
            }
        )

        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        """测试无效邮箱格式"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "test_user",
                "email": "invalid_email",
                "password": "password123"
            }
        )

        assert response.status_code == 422

    def test_register_short_password(self, client):
        """测试密码过短"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "test_user",
                "email": "test@example.com",
                "password": "123"  # 过短
            }
        )

        assert response.status_code == 422

    def test_logout_success(self, client, admin_auth_headers):
        """测试成功登出"""
        response = client.post(
            "/api/v1/auth/logout",
            headers=admin_auth_headers
        )

        assert response.status_code == 200

    def test_logout_without_token(self, client):
        """测试未登录时登出"""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 401

    def test_verify_token_success(self, client, admin_auth_headers):
        """测试token验证成功"""
        response = client.get(
            "/api/v1/auth/verify-token",
            headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert "user" in data

    def test_verify_token_invalid(self, client):
        """测试无效token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get(
            "/api/v1/auth/verify-token",
            headers=headers
        )

        assert response.status_code == 401

    def test_verify_token_missing(self, client):
        """测试缺少token"""
        response = client.get("/api/v1/auth/verify-token")

        assert response.status_code == 401


class TestAuthAuthorization:
    """认证授权测试类"""

    def test_protected_route_without_token(self, client):
        """测试未授权访问受保护路由"""
        response = client.get("/api/v1/users/me")

        assert response.status_code == 401

    def test_protected_route_with_valid_token(self, client, admin_auth_headers):
        """测试有效token访问受保护路由"""
        response = client.get(
            "/api/v1/users/me",
            headers=admin_auth_headers
        )

        assert response.status_code == 200

    def test_protected_route_with_expired_token(self, client):
        """测试过期token"""
        # 使用明显过期的token格式
        headers = {"Authorization": "Bearer expired.token.here"}
        response = client.get("/api/v1/users/me", headers=headers)

        # 应该返回401，token验证失败
        assert response.status_code == 401
