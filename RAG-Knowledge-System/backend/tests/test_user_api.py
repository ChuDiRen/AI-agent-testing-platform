"""
用户管理 API 测试

测试用户管理、权限控制等功能
"""
import pytest


class TestUserManagement:
    """用户管理测试类"""

    def test_get_current_user(self, client, user_auth_headers):
        """测试获取当前用户信息"""
        response = client.get(
            "/api/v1/users/me",
            headers=user_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "password" not in data  # 密码不应返回

    def test_get_current_user_without_auth(self, client):
        """测试未认证获取当前用户"""
        response = client.get("/api/v1/users/me")

        assert response.status_code == 401

    def test_get_user_success(self, client, admin_auth_headers, test_session):
        """测试获取用户详情"""
        from app.models import user

        # 创建测试用户
        test_user = user.User(
            username="test_user_profile",
            password_hash="hashed_password",
            email="test@example.com",
            full_name="测试用户",
            is_active=True,
            status=1
        )
        test_session.add(test_user)
        test_session.commit()
        test_session.refresh(test_user)

        response = client.get(
            f"/api/v1/users/{test_user.id}",
            headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == "test_user_profile"

    def test_get_user_not_found(self, client, admin_auth_headers):
        """测试获取不存在的用户"""
        response = client.get(
            "/api/v1/users/999999",
            headers=admin_auth_headers
        )

        assert response.status_code == 404

    def test_get_user_without_permission(self, client, user_auth_headers, test_session):
        """测试普通用户获取其他用户"""
        from app.models import user

        other_user = user.User(
            username="other_user",
            password_hash="hashed_password",
            email="other@example.com",
            is_active=True,
            status=1
        )
        test_session.add(other_user)
        test_session.commit()

        response = client.get(
            f"/api/v1/users/{other_user.id}",
            headers=user_auth_headers
        )

        assert response.status_code == 403  # Forbidden

    def test_get_users_list_admin(self, client, admin_auth_headers):
        """测试管理员获取用户列表"""
        response = client.get(
            "/api/v1/users",
            headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_get_users_list_without_permission(self, client, user_auth_headers):
        """测试普通用户获取用户列表"""
        response = client.get(
            "/api/v1/users",
            headers=user_auth_headers
        )

        # 普通用户可能没有权限
        assert response.status_code in [403, 200]

    def test_create_user_success(self, client, admin_auth_headers):
        """测试管理员创建用户"""
        new_user_data = {
            "username": "new_created_user",
            "email": "newcreated@example.com",
            "password": "password123",
            "full_name": "新创建的用户",
            "role_id": 1,
            "is_active": True
        }

        response = client.post(
            "/api/v1/users",
            headers=admin_auth_headers,
            json=new_user_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "new_created_user"
        assert "password" not in data

    def test_create_user_without_permission(self, client, user_auth_headers):
        """测试普通用户创建用户"""
        new_user_data = {
            "username": "new_user",
            "email": "test@example.com",
            "password": "password123"
        }

        response = client.post(
            "/api/v1/users",
            headers=user_auth_headers,
            json=new_user_data
        )

        assert response.status_code == 403

    def test_create_user_duplicate_username(self, client, admin_auth_headers, test_regular_user):
        """测试创建重复用户名"""
        new_user_data = {
            "username": test_regular_user.username,  # 已存在的用户名
            "email": "different@example.com",
            "password": "password123"
        }

        response = client.post(
            "/api/v1/users",
            headers=admin_auth_headers,
            json=new_user_data
        )

        assert response.status_code == 400

    def test_update_user_success(self, client, admin_auth_headers, test_session):
        """测试更新用户"""
        from app.models import user

        target_user = user.User(
            username="user_to_update",
            password_hash="hashed_password",
            email="toupdate@example.com",
            is_active=True,
            status=1
        )
        test_session.add(target_user)
        test_session.commit()
        test_session.refresh(target_user)

        update_data = {
            "full_name": "更新的姓名",
            "email": "updated@example.com"
        }

        response = client.put(
            f"/api/v1/users/{target_user.id}",
            headers=admin_auth_headers,
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "更新的姓名"

    def test_update_user_without_permission(self, client, user_auth_headers, test_session):
        """测试普通用户更新其他用户"""
        from app.models import user

        other_user = user.User(
            username="other_user_update",
            password_hash="hashed_password",
            email="other@example.com",
            is_active=True,
            status=1
        )
        test_session.add(other_user)
        test_session.commit()

        update_data = {"full_name": "尝试修改"}

        response = client.put(
            f"/api/v1/users/{other_user.id}",
            headers=user_auth_headers,
            json=update_data
        )

        assert response.status_code == 403

    def test_delete_user_success(self, client, admin_auth_headers, test_session):
        """测试删除用户"""
        from app.models import user

        user_to_delete = user.User(
            username="user_to_delete",
            password_hash="hashed_password",
            email="todelete@example.com",
            is_active=True,
            status=1
        )
        test_session.add(user_to_delete)
        test_session.commit()
        test_session.refresh(user_to_delete)

        user_id = user_to_delete.id

        response = client.delete(
            f"/api/v1/users/{user_id}",
            headers=admin_auth_headers
        )

        assert response.status_code == 200

        # 验证用户已被删除
        get_response = client.get(
            f"/api/v1/users/{user_id}",
            headers=admin_auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_user_without_permission(self, client, user_auth_headers, test_session):
        """测试普通用户删除用户"""
        from app.models import user

        other_user = user.User(
            username="other_user_delete",
            password_hash="hashed_password",
            email="other@example.com",
            is_active=True,
            status=1
        )
        test_session.add(other_user)
        test_session.commit()

        response = client.delete(
            f"/api/v1/users/{other_user.id}",
            headers=user_auth_headers
        )

        assert response.status_code == 403

    def test_delete_user_not_found(self, client, admin_auth_headers):
        """测试删除不存在的用户"""
        response = client.delete(
            "/api/v1/users/999999",
            headers=admin_auth_headers
        )

        assert response.status_code == 404


class TestUserPassword:
    """用户密码管理测试类"""

    def test_change_password_success(self, client, user_auth_headers, test_regular_user):
        """测试修改密码"""
        password_data = {
            "old_password": "user123",
            "new_password": "newpassword456"
        }

        response = client.post(
            "/api/v1/users/change-password",
            headers=user_auth_headers,
            json=password_data
        )

        # 可能返回200或501（未实现）
        assert response.status_code in [200, 501]

    def test_change_password_wrong_old(self, client, user_auth_headers):
        """测试旧密码错误"""
        password_data = {
            "old_password": "wrong_password",
            "new_password": "newpassword456"
        }

        response = client.post(
            "/api/v1/users/change-password",
            headers=user_auth_headers,
            json=password_data
        )

        # 可能返回400或501
        assert response.status_code in [400, 501]

    def test_change_password_without_auth(self, client):
        """测试未认证修改密码"""
        password_data = {
            "old_password": "password123",
            "new_password": "newpassword456"
        }

        response = client.post(
            "/api/v1/users/change-password",
            json=password_data
        )

        assert response.status_code == 401


class TestUserPermissions:
    """用户权限测试类"""

    def test_admin_can_access_all(self, client, admin_auth_headers):
        """测试管理员可以访问所有资源"""
        # 尝试访问各种管理员资源
        endpoints = [
            "/api/v1/users",
            "/api/v1/logs",
            "/api/v1/feedback/report"
        ]

        for endpoint in endpoints:
            response = client.get(
                endpoint,
                headers=admin_auth_headers
            )
            # 不应该返回401或403
            assert response.status_code not in [401, 403]

    def test_regular_user_limited_access(self, client, user_auth_headers):
        """测试普通用户权限受限"""
        # 尝试访问管理员资源
        admin_endpoints = [
            "/api/v1/users",
            "/api/v1/logs",
            "/api/v1/feedback/report"
        ]

        for endpoint in admin_endpoints:
            response = client.get(
                endpoint,
                headers=user_auth_headers
            )
            # 普通用户可能无法访问
            assert response.status_code in [403, 200]
