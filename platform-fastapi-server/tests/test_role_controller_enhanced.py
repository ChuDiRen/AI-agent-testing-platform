"""
RoleController 角色管理模块增强单元测试
覆盖所有接口: queryByPage, queryById, insert, update, delete, assignMenus, getMenus
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestRoleController:
    """角色控制器增强测试类"""

    def test_query_by_page_success(self, client: TestClient, session: Session, admin_headers):
        """测试分页查询角色成功"""
        from sysmanage.model.role import Role

        # 创建测试角色
        role = Role(
            role_name="test_role1",
            role_key="TEST_ROLE_1",
            role_sort=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()

        response = client.post("/role/queryByPage",
            json={"page": 1, "pageSize": 10},
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert "total" in data["data"]
        assert len(data["data"]["list"]) >= 1

    def test_query_by_page_with_filter(self, client: TestClient, session: Session, admin_headers):
        """测试带过滤条件的分页查询"""
        from sysmanage.model.role import Role

        # 创建多个角色
        roles = [
            Role(
                role_name="admin_role",
                role_key="ADMIN_ROLE",
                role_sort=1,
                status="1",
                create_time=datetime.now()
            ),
            Role(
                role_name="user_role",
                role_key="USER_ROLE",
                role_sort=2,
                status="1",
                create_time=datetime.now()
            ),
            Role(
                role_name="test_admin_role",
                role_key="TEST_ADMIN",
                role_sort=3,
                status="0",
                create_time=datetime.now()
            )
        ]

        for role in roles:
            session.add(role)
        session.commit()

        # 按角色名过滤
        response = client.post("/role/queryByPage",
            json={
                "page": 1,
                "pageSize": 10,
                "role_name": "admin"
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        if len(data["data"]["list"]) > 0:
            for role in data["data"]["list"]:
                assert "admin" in role["role_name"]

    def test_query_by_id_success(self, client: TestClient, session: Session, admin_headers):
        """测试根据ID查询角色成功"""
        from sysmanage.model.role import Role

        role = Role(
            role_name="single_query_role",
            role_key="SINGLE_QUERY",
            role_sort=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()

        response = client.get(f"/role/queryById?id={role.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == role.id
        assert data["data"]["role_name"] == "single_query_role"

    def test_query_by_id_not_found(self, client: TestClient, admin_headers):
        """测试查询不存在的角色ID"""
        response = client.get("/role/queryById?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_insert_role_success(self, client: TestClient, admin_headers):
        """测试新增角色成功"""
        role_data = {
            "role_name": "new_role",
            "role_key": "NEW_ROLE",
            "role_sort": 10,
            "status": "1",
            "remark": "新创建的角色"
        }

        response = client.post("/role/insert",
            json=role_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
        assert data["data"]["role_name"] == "new_role"

    def test_insert_role_duplicate_name(self, client: TestClient, session: Session, admin_headers):
        """测试新增重复角色名的角色"""
        from sysmanage.model.role import Role

        # 先创建一个角色
        existing_role = Role(
            role_name="duplicate_role",
            role_key="DUPLICATE_ROLE",
            role_sort=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(existing_role)
        session.commit()

        # 尝试创建同名角色
        role_data = {
            "role_name": "duplicate_role",
            "role_key=": "DIFFERENT_KEY",
            "role_sort": 2,
            "status": "1"
        }

        response = client.post("/role/insert",
            json=role_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "已存在" in data["msg"]

    def test_update_role_success(self, client: TestClient, session: Session, admin_headers):
        """测试更新角色成功"""
        from sysmanage.model.role import Role

        # 先创建角色
        role = Role(
            role_name="update_role",
            role_key="UPDATE_ROLE",
            role_sort=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()

        # 更新角色
        update_data = {
            "id": role.id,
            "role_name": "updated_role",
            "role_key": "UPDATED_ROLE",
            "role_sort": 5,
            "status": "0",
            "remark": "更新后的角色"
        }

        response = client.put("/role/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_update_role_not_found(self, client: TestClient, admin_headers):
        """测试更新不存在的角色"""
        update_data = {
            "id": 99999,
            "role_name": "nonexistent_role",
            "role_key": "NONEXISTENT"
        }

        response = client.put("/role/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_delete_role_success(self, client: TestClient, session: Session, admin_headers):
        """测试删除角色成功"""
        from sysmanage.model.role import Role
        from sysmanage.model.role_menu import RoleMenu

        # 先创建角色和菜单关联
        role = Role(
            role_name="delete_role",
            role_key="DELETE_ROLE",
            role_sort=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()

        # 创建菜单关联
        role_menu = RoleMenu(role_id=role.id, menu_id=1)
        session.add(role_menu)
        session.commit()

        response = client.delete(f"/role/delete?id={role.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_delete_role_not_found(self, client: TestClient, admin_headers):
        """测试删除不存在的角色"""
        response = client.delete("/role/delete?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_assign_menus_success(self, client: TestClient, session: Session, admin_headers):
        """测试为角色分配菜单权限成功"""
        from sysmanage.model.role import Role

        # 先创建角色
        role = Role(
            role_name="menu_assign_role",
            role_key="MENU_ASSIGN_ROLE",
            role_sort=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()

        # 分配菜单权限
        menu_assign_data = {
            "id": role.id,
            "menu_ids": [1, 2, 3, 5, 8]
        }

        response = client.post("/role/assignMenus",
            json=menu_assign_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_assign_menus_role_not_found(self, client: TestClient, admin_headers):
        """测试为不存在的角色分配菜单权限"""
        menu_assign_data = {
            "id": 99999,
            "menu_ids": [1, 2, 3]
        }

        response = client.post("/role/assignMenus",
            json=menu_assign_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_assign_menus_empty_menus(self, client: TestClient, session: Session, admin_headers):
        """测试分配空菜单权限列表"""
        from sysmanage.model.role import Role

        role = Role(
            role_name="empty_menus_role",
            role_key="EMPTY_MENUS_ROLE",
            role_sort=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()

        menu_assign_data = {
            "id": role.id,
            "menu_ids": []
        }

        response = client.post("/role/assignMenus",
            json=menu_assign_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_assign_menus_replace_existing(self, client: TestClient, session: Session, admin_headers):
        """测试替换现有的菜单权限"""
        from sysmanage.model.role import Role
        from sysmanage.model.role_menu import RoleMenu

        # 先创建角色
        role = Role(
            role_name="replace_menus_role",
            role_key="REPLACE_MENUS_ROLE",
            role_sort=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()

        # 先分配一些菜单权限
        existing_menus = [1, 2, 3]
        for menu_id in existing_menus:
            role_menu = RoleMenu(role_id=role.id, menu_id=menu_id)
            session.add(role_menu)
        session.commit()

        # 重新分配菜单权限（应该替换原有的）
        menu_assign_data = {
            "id": role.id,
            "menu_ids": [4, 5, 6]
        }

        response = client.post("/role/assignMenus",
            json=menu_assign_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        # 验证菜单权限已被替换
        response = client.get(f"/role/menus/{role.id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert len(response.json()["data"]["list"]) == 3
        assert 4 in response.json()["data"]["list"]
        assert 5 in response.json()["data"]["list"]
        assert 6 in response.json()["data"]["list"]

    def test_get_role_menus_success(self, client: TestClient, session: Session, admin_headers):
        """测试获取角色的菜单权限成功"""
        from sysmanage.model.role import Role
        from sysmanage.model.role_menu import RoleMenu

        # 先创建角色
        role = Role(
            role_name="get_menus_role",
            role_key="GET_MENUS_ROLE",
            role_sort=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()

        # 创建菜单关联
        menu_ids = [1, 3, 5, 7, 9]
        for menu_id in menu_ids:
            role_menu = RoleMenu(role_id=role.id, menu_id=menu_id)
            session.add(role_menu)
        session.commit()

        response = client.get(f"/role/menus/{role.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert len(data["data"]["list"]) == 5
        assert 1 in data["data"]["list"]
        assert 3 in data["data"]["list"]
        assert 5 in data["data"]["list"]
        assert 7 in data["data"]["list"]
        assert 9 in data["data"]["list"]

    def test_get_role_menus_not_found(self, client: TestClient, admin_headers):
        """测试获取不存在角色的菜单权限"""
        response = client.get("/role/menus/99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert len(data["data"]["list"]) == 0

    def test_get_role_menus_no_menus(self, client: TestClient, session: Session, admin_headers):
        """测试获取没有菜单权限的角色"""
        from sysmanage.model.role import Role

        role = Role(
            role_name="no_menus_role",
            role_key="NO_MENUS_ROLE",
            role_sort=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()

        response = client.get(f"/role/menus/{role.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert len(data["data"]["list"]) == 0

    def test_unauthorized_access(self, client: TestClient):
        """测试未授权访问"""
        response = client.post("/role/queryByPage",
            json={"page": 1, "pageSize": 10}
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]

    def test_unauthorized_menu_assignment(self, client: TestClient):
        """测试未授权的菜单权限分配"""
        menu_assign_data = {
            "id": 1,
            "menu_ids": [1, 2, 3]
        }

        response = client.post("/role/assignMenus",
            json=menu_assign_data
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]


class TestRoleControllerIntegration:
    """角色管理集成测试"""

    def test_full_role_lifecycle_with_menus(self, client: TestClient, session: Session, admin_headers):
        """测试完整的角色生命周期（包含菜单权限）"""
        from sysmanage.model.role import Role
        from sysmanage.model.role_menu import RoleMenu

        # 1. 创建角色
        role_data = {
            "role_name": "lifecycle_role",
            "role_key": "LIFECYCLE_ROLE",
            "role_sort": 10,
            "status": "1",
            "remark": "完整生命周期测试角色"
        }

        response = client.post("/role/insert",
            json=role_data,
            headers=admin_headers
        )
        assert response.status_code == 200
        role_id = response.json()["data"]["id"]

        # 2. 查询角色详情
        response = client.get(f"/role/queryById?id={role_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json()["data"]["role_name"] == "lifecycle_role"

        # 3. 分配菜单权限
        menu_assign_data = {
            "id": role_id,
            "menu_ids": [1, 2, 3, 5]
        }
        response = client.post("/role/assignMenus",
            json=menu_assign_data,
            headers=admin_headers
        )
        assert response.status_code == 200

        # 4. 获取角色菜单权限
        response = client.get(f"/role/menus/{role_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert len(response.json()["data"]["list"]) == 4

        # 5. 更新角色
        update_data = {
            "id": role_id,
            "role_name": "updated_lifecycle_role",
            "remark": "更新后的角色"
        }
        response = client.put("/role/update",
            json=update_data,
            headers=admin_headers
        )
        assert response.status_code == 200

        # 6. 重新分配菜单权限（替换）
        menu_assign_data = {
            "id": role_id,
            "menu_ids": [4, 6, 8]
        }
        response = client.post("/role/assignMenus",
            json=menu_assign_data,
            headers=admin_headers
        )
        assert response.status_code == 200

        # 7. 验证菜单权限已更新
        response = client.get(f"/role/menus/{role_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert len(response.json()["data"]["list"]) == 3

        # 8. 删除角色（应该同时删除菜单权限）
        response = client.delete(f"/role/delete?id={role_id}",
            headers=admin_headers
        )
        assert response.status_code == 200

        # 9. 验证角色已删除
        response = client.get(f"/role/queryById?id={role_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert "不存在" in response.json()["msg"]

    def test_multiple_roles_menu_assignment(self, client: TestClient, session: Session, admin_headers):
        """测试多个角色的菜单权限分配"""
        from sysmanage.model.role import Role

        # 创建多个角色
        roles = [
            Role(role_name="admin_role", role_key="ADMIN", role_sort=1, status="1", create_time=datetime.now()),
            Role(role_name="user_role", role_key="USER", role_sort=2, status="1", create_time=datetime.now()),
            Role(role_name="guest_role", role_key="GUEST", role_sort=3, status="1", create_time=datetime.now())
        ]

        for role in roles:
            session.add(role)
        session.commit()

        role_ids = [role.id for role in roles]

        # 为每个角色分配不同的菜单权限
        menu_assignments = [
            {"id": role_ids[0], "menu_ids": [1, 2, 3, 4, 5]},  # 管理员：所有菜单
            {"id": role_ids[1], "menu_ids": [1, 6, 7]},         # 用户：部分菜单
            {"id": role_ids[2], "menu_ids": [1, 8]}             # 访客：最少菜单
        ]

        for assignment in menu_assignments:
            response = client.post("/role/assignMenus",
                json=assignment,
                headers=admin_headers
            )
            assert response.status_code == 200

        # 验证每个角色的菜单权限
        expected_counts = [5, 3, 2]
        for i, role_id in enumerate(role_ids):
            response = client.get(f"/role/menus/{role_id}",
                headers=admin_headers
            )
            assert response.status_code == 200
            assert len(response.json()["data"]["list"]) == expected_counts[i]

    def test_menu_assignment_persistence(self, client: TestClient, session: Session, admin_headers):
        """测试菜单权限分配的持久性"""
        from sysmanage.model.role import Role
        from sysmanage.model.role_menu import RoleMenu

        # 创建角色
        role = Role(
            role_name="persistent_role",
            role_key="PERSISTENT",
            role_sort=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()

        # 分配菜单权限
        menu_assign_data = {
            "id": role.id,
            "menu_ids": [1, 2, 3]
        }
        response = client.post("/role/assignMenus",
            json=menu_assign_data,
            headers=admin_headers
        )
        assert response.status_code == 200

        # 直接查询数据库验证权限已保存
        role_menus = session.exec(select(RoleMenu).where(RoleMenu.role_id == role.id)).all()
        assert len(role_menus) == 3

        # 通过API再次查询验证一致性
        response = client.get(f"/role/menus/{role.id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        api_menu_ids = set(response.json()["data"]["list"])
        db_menu_ids = set(rm.menu_id for rm in role_menus)
        assert api_menu_ids == db_menu_ids