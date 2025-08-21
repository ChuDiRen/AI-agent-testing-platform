"""
用户Controller测试
测试用户相关的API端点
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.entity.user import User
from app.tests.test_base import BaseTestCase


class TestUserController(BaseTestCase):
    """
    用户Controller测试类
    """
    
    def test_create_user_success(self, client: TestClient, sample_user_data: dict):
        """
        测试创建用户成功
        """
        response = client.post("/api/v1/users/", json=sample_user_data)
        
        self.assert_response_success(response, 201)
        self.assert_response_contains(response, "id", "username", "email")
        
        data = response.json()["data"]
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert data["full_name"] == sample_user_data["full_name"]
    
    def test_create_user_validation_error(self, client: TestClient):
        """
        测试创建用户验证错误
        """
        invalid_data = {
            "username": "ab",  # 太短
            "email": "invalid-email",  # 无效邮箱
            "password": "123"  # 密码太短
        }
        
        response = client.post("/api/v1/users/", json=invalid_data)
        self.assert_validation_error(response)
    
    def test_create_user_duplicate_username(self, client: TestClient, test_user: User):
        """
        测试创建用户用户名重复
        """
        duplicate_data = {
            "username": test_user.username,
            "email": "different@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/users/", json=duplicate_data)
        self.assert_response_error(response, 409)
    
    def test_get_user_success(self, client: TestClient, test_user: User):
        """
        测试获取用户成功
        """
        response = client.get(f"/api/v1/users/{test_user.id}")
        
        self.assert_response_success(response)
        self.assert_response_data(response, {
            "id": test_user.id,
            "username": test_user.username,
            "email": test_user.email
        })
    
    def test_get_user_not_found(self, client: TestClient):
        """
        测试获取不存在的用户
        """
        response = client.get("/api/v1/users/99999")
        self.assert_not_found_error(response)
    
    def test_update_user_success(self, client: TestClient, test_user: User, auth_headers: dict):
        """
        测试更新用户成功
        """
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio"
        }
        
        response = self.make_authenticated_request(
            client, "PUT", f"/api/v1/users/{test_user.id}",
            auth_headers, json=update_data
        )
        
        self.assert_response_success(response)
        self.assert_response_data(response, update_data)
    
    def test_update_user_not_found(self, client: TestClient, auth_headers: dict):
        """
        测试更新不存在的用户
        """
        update_data = {"full_name": "Updated Name"}
        
        response = self.make_authenticated_request(
            client, "PUT", "/api/v1/users/99999",
            auth_headers, json=update_data
        )
        
        self.assert_not_found_error(response)
    
    def test_delete_user_success(self, client: TestClient, test_user: User, auth_headers: dict):
        """
        测试删除用户成功
        """
        response = self.make_authenticated_request(
            client, "DELETE", f"/api/v1/users/{test_user.id}",
            auth_headers
        )
        
        self.assert_response_success(response)
    
    def test_delete_user_not_found(self, client: TestClient, auth_headers: dict):
        """
        测试删除不存在的用户
        """
        response = self.make_authenticated_request(
            client, "DELETE", "/api/v1/users/99999",
            auth_headers
        )
        
        self.assert_not_found_error(response)
    
    def test_list_users_success(self, client: TestClient, test_user: User):
        """
        测试获取用户列表成功
        """
        response = client.get("/api/v1/users/")
        
        self.assert_response_success(response)
        self.assert_pagination_response(response)
        
        data = response.json()["data"]
        assert len(data["items"]) >= 1
        
        # 检查用户是否在列表中
        user_ids = [item["id"] for item in data["items"]]
        assert test_user.id in user_ids
    
    def test_list_users_pagination(self, client: TestClient):
        """
        测试用户列表分页
        """
        # 测试第一页
        response = client.get("/api/v1/users/?page=1&page_size=5")
        self.assert_response_success(response)
        self.assert_pagination_response(response)
        
        data = response.json()["data"]
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 5
    
    def test_login_success(self, client: TestClient, test_user: User):
        """
        测试用户登录成功
        """
        login_data = {
            "identifier": test_user.username,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/users/login", json=login_data)
        
        self.assert_response_success(response)
        self.assert_response_contains(response, "access_token", "refresh_token", "user")
        
        data = response.json()["data"]
        assert data["token_type"] == "bearer"
        assert data["user"]["id"] == test_user.id
    
    def test_login_invalid_credentials(self, client: TestClient, test_user: User):
        """
        测试用户登录凭据无效
        """
        login_data = {
            "identifier": test_user.username,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/users/login", json=login_data)
        self.assert_authentication_error(response)
    
    def test_login_user_not_found(self, client: TestClient):
        """
        测试登录用户不存在
        """
        login_data = {
            "identifier": "nonexistentuser",
            "password": "password123"
        }
        
        response = client.post("/api/v1/users/login", json=login_data)
        self.assert_authentication_error(response)
    
    def test_change_password_success(self, client: TestClient, test_user: User, auth_headers: dict):
        """
        测试修改密码成功
        """
        password_data = {
            "old_password": "testpassword123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        response = self.make_authenticated_request(
            client, "POST", f"/api/v1/users/{test_user.id}/change-password",
            auth_headers, json=password_data
        )
        
        self.assert_response_success(response)
    
    def test_change_password_wrong_old_password(self, client: TestClient, test_user: User, auth_headers: dict):
        """
        测试修改密码旧密码错误
        """
        password_data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        response = self.make_authenticated_request(
            client, "POST", f"/api/v1/users/{test_user.id}/change-password",
            auth_headers, json=password_data
        )
        
        self.assert_authentication_error(response)
    
    def test_change_password_mismatch(self, client: TestClient, test_user: User, auth_headers: dict):
        """
        测试修改密码确认密码不匹配
        """
        password_data = {
            "old_password": "testpassword123",
            "new_password": "newpassword123",
            "confirm_password": "differentpassword123"
        }
        
        response = self.make_authenticated_request(
            client, "POST", f"/api/v1/users/{test_user.id}/change-password",
            auth_headers, json=password_data
        )
        
        self.assert_validation_error(response)
    
    def test_search_users_success(self, client: TestClient, test_user: User):
        """
        测试搜索用户成功
        """
        search_data = {
            "keyword": test_user.username[:3],  # 搜索用户名前3个字符
            "page": 1,
            "page_size": 10
        }
        
        response = client.post("/api/v1/users/search", json=search_data)
        
        self.assert_response_success(response)
        self.assert_pagination_response(response)
        
        data = response.json()["data"]
        # 应该能找到测试用户
        user_ids = [item["id"] for item in data["items"]]
        assert test_user.id in user_ids
    
    def test_search_users_no_results(self, client: TestClient):
        """
        测试搜索用户无结果
        """
        search_data = {
            "keyword": "nonexistentkeyword",
            "page": 1,
            "page_size": 10
        }
        
        response = client.post("/api/v1/users/search", json=search_data)
        
        self.assert_response_success(response)
        self.assert_pagination_response(response, 0)
        
        data = response.json()["data"]
        assert len(data["items"]) == 0
    
    @pytest.mark.auth
    def test_unauthorized_access(self, client: TestClient, test_user: User):
        """
        测试未授权访问
        """
        # 尝试不带认证头访问需要认证的端点
        response = client.put(f"/api/v1/users/{test_user.id}", json={"full_name": "New Name"})
        self.assert_authentication_error(response)
        
        response = client.delete(f"/api/v1/users/{test_user.id}")
        self.assert_authentication_error(response)
        
        response = client.post(f"/api/v1/users/{test_user.id}/change-password", json={
            "old_password": "old",
            "new_password": "new123",
            "confirm_password": "new123"
        })
        self.assert_authentication_error(response)


# 导出测试类
__all__ = ["TestUserController"]
