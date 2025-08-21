# Copyright (c) 2025 左岚. All rights reserved.
"""
RBAC API接口测试用例
测试角色、菜单、部门、用户等API接口
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestRoleAPI:
    """角色API测试"""

    def test_create_role(self, client: TestClient):
        """测试创建角色API"""
        role_data = {
            "role_name": "API测试角色",
            "remark": "通过API创建的测试角色"
        }
        
        response = client.post("/api/v1/roles/", json=role_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["role_name"] == "API测试角色"
        assert data["data"]["remark"] == "通过API创建的测试角色"

    def test_get_roles(self, client: TestClient):
        """测试获取角色列表API"""
        # 先创建一个角色
        role_data = {"role_name": "列表测试角色", "remark": "用于列表测试"}
        client.post("/api/v1/roles/", json=role_data)
        
        # 获取角色列表
        response = client.get("/api/v1/roles/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "roles" in data["data"]
        assert "total" in data["data"]

    def test_get_role_by_id(self, client: TestClient):
        """测试根据ID获取角色API"""
        # 先创建一个角色
        role_data = {"role_name": "ID测试角色", "remark": "用于ID查询测试"}
        create_response = client.post("/api/v1/roles/", json=role_data)
        role_id = create_response.json()["data"]["role_id"]
        
        # 根据ID获取角色
        response = client.get(f"/api/v1/roles/{role_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["role_id"] == role_id
        assert data["data"]["role_name"] == "ID测试角色"

    def test_update_role(self, client: TestClient):
        """测试更新角色API"""
        # 先创建一个角色
        role_data = {"role_name": "更新前角色", "remark": "更新前描述"}
        create_response = client.post("/api/v1/roles/", json=role_data)
        role_id = create_response.json()["data"]["role_id"]
        
        # 更新角色
        update_data = {"role_name": "更新后角色", "remark": "更新后描述"}
        response = client.put(f"/api/v1/roles/{role_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["role_name"] == "更新后角色"
        assert data["data"]["remark"] == "更新后描述"

    def test_delete_role(self, client: TestClient):
        """测试删除角色API"""
        # 先创建一个角色
        role_data = {"role_name": "待删除角色", "remark": "将被删除的角色"}
        create_response = client.post("/api/v1/roles/", json=role_data)
        role_id = create_response.json()["data"]["role_id"]
        
        # 删除角色
        response = client.delete(f"/api/v1/roles/{role_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] is True
        
        # 验证角色已被删除
        get_response = client.get(f"/api/v1/roles/{role_id}")
        assert get_response.status_code == 404


class TestMenuAPI:
    """菜单API测试"""

    def test_create_menu(self, client: TestClient):
        """测试创建菜单API"""
        menu_data = {
            "parent_id": 0,
            "menu_name": "API测试菜单",
            "menu_type": "0",
            "path": "/api-test",
            "component": "ApiTest",
            "icon": "el-icon-test",
            "order_num": 1
        }
        
        response = client.post("/api/v1/menus/", json=menu_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["menu_name"] == "API测试菜单"
        assert data["data"]["menu_type"] == "0"

    def test_get_menu_tree(self, client: TestClient):
        """测试获取菜单树API"""
        # 先创建一些菜单
        parent_menu = {
            "parent_id": 0,
            "menu_name": "父菜单",
            "menu_type": "0",
            "path": "/parent"
        }
        parent_response = client.post("/api/v1/menus/", json=parent_menu)
        parent_id = parent_response.json()["data"]["menu_id"]
        
        child_menu = {
            "parent_id": parent_id,
            "menu_name": "子菜单",
            "menu_type": "0",
            "path": "/parent/child"
        }
        client.post("/api/v1/menus/", json=child_menu)
        
        # 获取菜单树
        response = client.get("/api/v1/menus/tree")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "tree" in data["data"]


class TestDepartmentAPI:
    """部门API测试"""

    def test_create_department(self, client: TestClient):
        """测试创建部门API"""
        dept_data = {
            "parent_id": 0,
            "dept_name": "API测试部门",
            "order_num": 1
        }
        
        response = client.post("/api/v1/departments/", json=dept_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["dept_name"] == "API测试部门"

    def test_get_department_tree(self, client: TestClient):
        """测试获取部门树API"""
        # 先创建一些部门
        parent_dept = {
            "parent_id": 0,
            "dept_name": "父部门",
            "order_num": 1
        }
        parent_response = client.post("/api/v1/departments/", json=parent_dept)
        parent_id = parent_response.json()["data"]["dept_id"]
        
        child_dept = {
            "parent_id": parent_id,
            "dept_name": "子部门",
            "order_num": 1
        }
        client.post("/api/v1/departments/", json=child_dept)
        
        # 获取部门树
        response = client.get("/api/v1/departments/tree")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "tree" in data["data"]


class TestUserAPI:
    """用户API测试"""

    def test_create_user(self, client: TestClient):
        """测试创建用户API"""
        user_data = {
            "username": "apiuser",
            "password": "123456",
            "email": "apiuser@example.com",
            "mobile": "13900139000",
            "ssex": "0",
            "description": "API测试用户"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "apiuser"
        assert data["data"]["email"] == "apiuser@example.com"

    def test_user_login(self, client: TestClient):
        """测试用户登录API"""
        # 先创建用户
        user_data = {
            "username": "loginuser",
            "password": "123456",
            "email": "login@example.com"
        }
        client.post("/api/v1/users/", json=user_data)
        
        # 登录
        login_data = {
            "username": "loginuser",
            "password": "123456"
        }
        response = client.post("/api/v1/users/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "user_info" in data["data"]
        assert data["data"]["user_info"]["username"] == "loginuser"

    def test_get_users(self, client: TestClient):
        """测试获取用户列表API"""
        # 先创建一个用户
        user_data = {"username": "listuser", "password": "123456"}
        client.post("/api/v1/users/", json=user_data)
        
        # 获取用户列表
        response = client.get("/api/v1/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "users" in data["data"]

    def test_assign_roles_to_user(self, client: TestClient):
        """测试为用户分配角色API"""
        # 创建用户
        user_data = {"username": "roleassignuser", "password": "123456"}
        user_response = client.post("/api/v1/users/", json=user_data)
        user_id = user_response.json()["data"]["user_id"]
        
        # 创建角色
        role_data = {"role_name": "分配测试角色", "remark": "用于分配测试"}
        role_response = client.post("/api/v1/roles/", json=role_data)
        role_id = role_response.json()["data"]["role_id"]
        
        # 分配角色
        assign_data = {"role_ids": [role_id]}
        response = client.post(f"/api/v1/users/{user_id}/roles", json=assign_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] is True
        
        # 验证角色分配
        roles_response = client.get(f"/api/v1/users/{user_id}/roles")
        assert roles_response.status_code == 200
        roles_data = roles_response.json()
        assert len(roles_data["data"]["roles"]) == 1
        assert roles_data["data"]["roles"][0]["role_name"] == "分配测试角色"


class TestRBACAPIIntegration:
    """RBAC API集成测试"""

    def test_complete_rbac_api_flow(self, client: TestClient):
        """测试完整的RBAC API流程"""
        # 1. 创建部门
        dept_data = {"parent_id": 0, "dept_name": "API集成测试部门", "order_num": 1}
        dept_response = client.post("/api/v1/departments/", json=dept_data)
        dept_id = dept_response.json()["data"]["dept_id"]
        
        # 2. 创建角色
        role_data = {"role_name": "API集成测试角色", "remark": "用于API集成测试"}
        role_response = client.post("/api/v1/roles/", json=role_data)
        role_id = role_response.json()["data"]["role_id"]
        
        # 3. 创建菜单
        menu_data = {
            "parent_id": 0,
            "menu_name": "API集成测试菜单",
            "menu_type": "0",
            "path": "/api-integration",
            "perms": "api:test"
        }
        menu_response = client.post("/api/v1/menus/", json=menu_data)
        menu_id = menu_response.json()["data"]["menu_id"]
        
        # 4. 为角色分配菜单权限
        assign_menu_data = {"menu_ids": [menu_id]}
        assign_response = client.post(f"/api/v1/roles/{role_id}/menus", json=assign_menu_data)
        assert assign_response.status_code == 200
        
        # 5. 创建用户
        user_data = {
            "username": "apiintegrationuser",
            "password": "123456",
            "email": "apiintegration@example.com",
            "dept_id": dept_id
        }
        user_response = client.post("/api/v1/users/", json=user_data)
        user_id = user_response.json()["data"]["user_id"]
        
        # 6. 为用户分配角色
        assign_role_data = {"role_ids": [role_id]}
        assign_role_response = client.post(f"/api/v1/users/{user_id}/roles", json=assign_role_data)
        assert assign_role_response.status_code == 200
        
        # 7. 用户登录
        login_data = {"username": "apiintegrationuser", "password": "123456"}
        login_response = client.post("/api/v1/users/login", json=login_data)
        assert login_response.status_code == 200
        
        login_result = login_response.json()["data"]
        assert "access_token" in login_result
        assert "permissions" in login_result
        assert "api:test" in login_result["permissions"]
        
        # 8. 获取用户菜单
        user_menu_response = client.get(f"/api/v1/menus/user/{user_id}")
        assert user_menu_response.status_code == 200
        
        menu_result = user_menu_response.json()["data"]
        assert len(menu_result["menus"]) >= 1
        assert "api:test" in menu_result["permissions"]
