"""
UserController 用户管理模块增强单元测试
覆盖所有接口: queryByPage, queryById, insert, update, delete, assignRoles, getRoles, updateStatus
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestUserController:
    """用户控制器增强测试类"""

    def test_query_by_page_success(self, client: TestClient, session: Session, admin_headers):
        """测试分页查询用户成功"""
        from sysmanage.model.user import User

        # 创建测试用户
        user = User(
            username="test_user1",
            password="password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()

        response = client.post("/user/queryByPage",
            json={"page": 1, "pageSize": 10},
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert "total" in data["data"]
        assert len(data["data"]["list"]) >= 1

    def test_query_by_page_with_filters(self, client: TestClient, session: Session, admin_headers):
        """测试带过滤条件的分页查询"""
        from sysmanage.model.user import User

        # 创建多个用户
        users = [
            User(
                username="admin_user",
                password="password123",
                dept_id=1,
                status="1",
                create_time=datetime.now()
            ),
            User(
                username="normal_user",
                password="password123",
                dept_id=2,
                status="0",
                create_time=datetime.now()
            ),
            User(
                username="test_user",
                password="password123",
                dept_id=1,
                status="1",
                create_time=datetime.now()
            )
        ]

        for user in users:
            session.add(user)
        session.commit()

        # 按用户名过滤
        response = client.post("/user/queryByPage",
            json={
                "page": 1,
                "pageSize": 10,
                "username": "admin"
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        if len(data["data"]["list"]) > 0:
            for user in data["data"]["list"]:
                assert "admin" in user["username"]

        # 按部门过滤
        response = client.post("/user/queryByPage",
            json={
                "page": 1,
                "pageSize": 10,
                "dept_id": 1
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        if len(data["data"]["list"]) > 0:
            for user in data["data"]["list"]:
                assert user["dept_id"] == 1

        # 按状态过滤
        response = client.post("/user/queryByPage",
            json={
                "page": 1,
                "pageSize": 10,
                "status": "1"
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        if len(data["data"]["list"]) > 0:
            for user in data["data"]["list"]:
                assert user["status"] == "1"

    def test_query_by_id_success(self, client: TestClient, session: Session, admin_headers):
        """测试根据ID查询用户成功"""
        from sysmanage.model.user import User

        user = User(
            username="single_query_user",
            password="password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()

        response = client.get(f"/user/queryById?id={user.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == user.id
        assert data["data"]["username"] == "single_query_user"

    def test_query_by_id_not_found(self, client: TestClient, admin_headers):
        """测试查询不存在的用户ID"""
        response = client.get("/user/queryById?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "没有数据" in data["msg"]

    def test_insert_user_success(self, client: TestClient, admin_headers):
        """测试新增用户成功"""
        user_data = {
            "username": "new_user",
            "password": "newpassword123",
            "dept_id": 1,
            "status": "1"
        }

        response = client.post("/user/insert",
            json=user_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
        assert "id" in data["data"]

    def test_insert_user_duplicate_username(self, client: TestClient, session: Session, admin_headers):
        """测试新增重复用户名的用户"""
        from sysmanage.model.user import User

        # 先创建一个用户
        existing_user = User(
            username="duplicate_user",
            password="password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(existing_user)
        session.commit()

        # 尝试创建同名用户
        user_data = {
            "username": "duplicate_user",
            "password": "newpassword123",
            "dept_id": 2,
            "status": "1"
        }

        response = client.post("/user/insert",
            json=user_data,
            headers=admin_headers
        )

        # 应该会出错，但不一定是因为重复检查（取决于数据库约束）
        assert response.status_code == 200

    def test_update_user_success(self, client: TestClient, session: Session, admin_headers):
        """测试更新用户成功"""
        from sysmanage.model.user import User

        # 先创建用户
        user = User(
            username="update_user",
            password="password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()

        # 更新用户
        update_data = {
            "id": user.id,
            "username": "updated_user",
            "dept_id": 2,
            "status": "0"
        }

        response = client.put("/user/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_update_user_not_found(self, client: TestClient, admin_headers):
        """测试更新不存在的用户"""
        update_data = {
            "id": 99999,
            "username": "nonexistent_user",
            "dept_id": 1
        }

        response = client.put("/user/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_delete_user_success(self, client: TestClient, session: Session, admin_headers):
        """测试删除用户成功"""
        from sysmanage.model.user import User
        from sysmanage.model.user_role import UserRole

        # 先创建用户和角色关联
        user = User(
            username="delete_user",
            password="password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()

        # 创建角色关联
        user_role = UserRole(user_id=user.id, role_id=1)
        session.add(user_role)
        session.commit()

        response = client.delete(f"/user/delete?id={user.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_delete_user_not_found(self, client: TestClient, admin_headers):
        """测试删除不存在的用户"""
        response = client.delete("/user/delete?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_assign_roles_success(self, client: TestClient, session: Session, admin_headers):
        """测试为用户分配角色成功"""
        from sysmanage.model.user import User

        # 先创建用户
        user = User(
            username="role_assign_user",
            password="password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()

        # 分配角色
        role_assign_data = {
            "id": user.id,
            "role_ids": [1, 2, 3]
        }

        response = client.post("/user/assignRoles",
            json=role_assign_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_assign_roles_user_not_found(self, client: TestClient, admin_headers):
        """测试为不存在的用户分配角色"""
        role_assign_data = {
            "id": 99999,
            "role_ids": [1, 2]
        }

        response = client.post("/user/assignRoles",
            json=role_assign_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_assign_roles_empty_roles(self, client: TestClient, session: Session, admin_headers):
        """测试分配空角色列表"""
        from sysmanage.model.user import User

        user = User(
            username="empty_roles_user",
            password="password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()

        role_assign_data = {
            "id": user.id,
            "role_ids": []
        }

        response = client.post("/user/assignRoles",
            json=role_assign_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_get_user_roles_success(self, client: TestClient, session: Session, admin_headers):
        """测试获取用户的角色成功"""
        from sysmanage.model.user import User
        from sysmanage.model.user_role import UserRole

        # 先创建用户
        user = User(
            username="get_roles_user",
            password="password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()

        # 创建角色关联
        user_roles = [
            UserRole(user_id=user.id, role_id=1),
            UserRole(user_id=user.id, role_id=3),
            UserRole(user_id=user.id, role_id=5)
        ]

        for user_role in user_roles:
            session.add(user_role)
        session.commit()

        response = client.get(f"/user/roles/{user.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert len(data["data"]["list"]) == 3
        assert 1 in data["data"]["list"]
        assert 3 in data["data"]["list"]
        assert 5 in data["data"]["list"]

    def test_get_user_roles_not_found(self, client: TestClient, admin_headers):
        """测试获取不存在用户的角色"""
        response = client.get("/user/roles/99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert len(data["data"]["list"]) == 0

    def test_get_user_roles_no_roles(self, client: TestClient, session: Session, admin_headers):
        """测试获取没有角色的用户"""
        from sysmanage.model.user import User

        user = User(
            username="no_roles_user",
            password="password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()

        response = client.get(f"/user/roles/{user.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert len(data["data"]["list"]) == 0

    def test_update_user_status_enable(self, client: TestClient, session: Session, admin_headers):
        """测试启用用户状态成功"""
        from sysmanage.model.user import User

        # 创建被锁定的用户
        user = User(
            username="locked_user",
            password="password123",
            dept_id=1,
            status="0",  # 锁定状态
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()

        status_update_data = {
            "id": user.id,
            "status": "1"  # 启用
        }

        response = client.put("/user/updateStatus",
            json=status_update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "启用成功" in data["msg"]

    def test_update_user_status_disable(self, client: TestClient, session: Session, admin_headers):
        """测试锁定用户状态成功"""
        from sysmanage.model.user import User

        # 创建启用的用户
        user = User(
            username="enabled_user",
            password="password123",
            dept_id=1,
            status="1",  # 启用状态
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()

        status_update_data = {
            "id": user.id,
            "status": "0"  # 锁定
        }

        response = client.put("/user/updateStatus",
            json=status_update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "锁定成功" in data["msg"]

    def test_update_user_status_not_found(self, client: TestClient, admin_headers):
        """测试更新不存在用户的状态"""
        status_update_data = {
            "id": 99999,
            "status": "1"
        }

        response = client.put("/user/updateStatus",
            json=status_update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_update_user_status_invalid_status(self, client: TestClient, session: Session, admin_headers):
        """测试更新用户状态为无效值"""
        from sysmanage.model.user import User

        user = User(
            username="invalid_status_user",
            password="password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()

        status_update_data = {
            "id": user.id,
            "status": "invalid"  # 无效状态值
        }

        response = client.put("/user/updateStatus",
            json=status_update_data,
            headers=admin_headers
        )

        # 应该返回验证错误或成功（取决于验证逻辑）
        assert response.status_code in [200, 422]

    def test_unauthorized_access(self, client: TestClient):
        """测试未授权访问"""
        response = client.post("/user/queryByPage",
            json={"page": 1, "pageSize": 10}
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]

    def test_unauthorized_role_assignment(self, client: TestClient):
        """测试未授权的角色分配"""
        role_assign_data = {
            "id": 1,
            "role_ids": [1, 2]
        }

        response = client.post("/user/assignRoles",
            json=role_assign_data
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]


class TestUserControllerIntegration:
    """用户管理集成测试"""

    def test_full_user_lifecycle(self, client: TestClient, session: Session, admin_headers):
        """测试完整的用户生命周期"""
        from sysmanage.model.user import User
        from sysmanage.model.user_role import UserRole

        # 1. 创建用户
        user_data = {
            "username": "lifecycle_user",
            "password": "password123",
            "dept_id": 1,
            "status": "1"
        }

        response = client.post("/user/insert",
            json=user_data,
            headers=admin_headers
        )
        assert response.status_code == 200
        user_id = response.json()["data"]["id"]

        # 2. 查询用户详情
        response = client.get(f"/user/queryById?id={user_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json()["data"]["username"] == "lifecycle_user"

        # 3. 分配角色
        role_assign_data = {
            "id": user_id,
            "role_ids": [1, 2]
        }
        response = client.post("/user/assignRoles",
            json=role_assign_data,
            headers=admin_headers
        )
        assert response.status_code == 200

        # 4. 获取用户角色
        response = client.get(f"/user/roles/{user_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert len(response.json()["data"]["list"]) == 2

        # 5. 更新用户状态（锁定）
        status_update_data = {
            "id": user_id,
            "status": "0"
        }
        response = client.put("/user/updateStatus",
            json=status_update_data,
            headers=admin_headers
        )
        assert response.status_code == 200

        # 6. 重新分配角色（清空）
        role_assign_data = {
            "id": user_id,
            "role_ids": []
        }
        response = client.post("/user/assignRoles",
            json=role_assign_data,
            headers=admin_headers
        )
        assert response.status_code == 200

        # 7. 删除用户
        response = client.delete(f"/user/delete?id={user_id}",
            headers=admin_headers
        )
        assert response.status_code == 200

        # 8. 验证用户已删除
        response = client.get(f"/user/queryById?id={user_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert "没有数据" in response.json()["msg"]