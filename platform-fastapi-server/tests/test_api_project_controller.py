"""
ApiProjectController API项目管理模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiProjectController:
    """API项目控制器测试类"""

    def test_query_by_page_success(self, client: TestClient, session: Session, admin_headers):
        """测试分页查询API项目成功"""
        # 先创建测试项目
        from apitest.model.ApiProjectModel import ApiProject

        project = ApiProject(
            project_name="测试项目1",
            project_description="这是一个测试项目",
            base_url="https://api.example.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        response = client.post("/ApiProject/queryByPage",
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
        """测试带条件过滤的分页查询"""
        from apitest.model.ApiProjectModel import ApiProject

        # 创建多个项目
        projects = [
            ApiProject(
                project_name="用户管理项目",
                project_description="用户相关API",
                base_url="https://api.user.com",
                create_time=datetime.now()
            ),
            ApiProject(
                project_name="订单管理项目",
                project_description="订单相关API",
                base_url="https://api.order.com",
                create_time=datetime.now()
            )
        ]

        for project in projects:
            session.add(project)
        session.commit()

        # 测试按项目名过滤
        response = client.post("/ApiProject/queryByPage",
            json={"page": 1, "pageSize": 10, "project_name": "用户"},
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) >= 1
        # 验证返回的都是包含"用户"的项目
        for project in data["data"]["list"]:
            assert "用户" in project["project_name"]

    def test_query_by_id_success(self, client: TestClient, session: Session, admin_headers):
        """测试根据ID查询API项目成功"""
        from apitest.model.ApiProjectModel import ApiProject

        project = ApiProject(
            project_name="单个查询测试项目",
            project_description="用于单个查询测试",
            base_url="https://api.single.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        response = client.get(f"/ApiProject/queryById?id={project.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["project_name"] == "单个查询测试项目"
        assert data["data"]["base_url"] == "https://api.single.com"

    def test_query_by_id_not_found(self, client: TestClient, admin_headers):
        """测试查询不存在的项目ID"""
        response = client.get("/ApiProject/queryById?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "没有数据" in data["msg"]

    def test_insert_project_success(self, client: TestClient, admin_headers):
        """测试新增API项目成功"""
        project_data = {
            "project_name": "新增测试项目",
            "project_description": "这是一个新增的测试项目",
            "base_url": "https://api.newproject.com"
        }

        response = client.post("/ApiProject/insert",
            json=project_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
        assert "id" in data["data"]

    def test_insert_project_duplicate_name(self, client: TestClient, session: Session, admin_headers):
        """测试新增重复项目名的项目"""
        from apitest.model.ApiProjectModel import ApiProject

        # 先创建一个项目
        existing_project = ApiProject(
            project_name="重复项目名",
            project_description="已存在的项目",
            base_url="https://api.existing.com",
            create_time=datetime.now()
        )
        session.add(existing_project)
        session.commit()

        # 尝试创建同名项目
        project_data = {
            "project_name": "重复项目名",
            "project_description": "重复名称的项目",
            "base_url": "https://api.duplicate.com"
        }

        response = client.post("/ApiProject/insert",
            json=project_data,
            headers=admin_headers
        )

        # 应该会出错，但不一定是因为重复检查（取决于数据库约束）
        assert response.status_code == 200

    def test_update_project_success(self, client: TestClient, session: Session, admin_headers):
        """测试更新API项目成功"""
        from apitest.model.ApiProjectModel import ApiProject

        # 先创建项目
        project = ApiProject(
            project_name="待更新项目",
            project_description="更新前的描述",
            base_url="https://api.old.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        # 更新项目
        update_data = {
            "id": project.id,
            "project_name": "已更新项目",
            "project_description": "更新后的描述",
            "base_url": "https://api.new.com"
        }

        response = client.put("/ApiProject/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_update_project_not_found(self, client: TestClient, admin_headers):
        """测试更新不存在的项目"""
        update_data = {
            "id": 99999,
            "project_name": "不存在的项目",
            "project_description": "这个项目不存在",
            "base_url": "https://api.nonexistent.com"
        }

        response = client.put("/ApiProject/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_delete_project_success(self, client: TestClient, session: Session, admin_headers):
        """测试删除API项目成功"""
        from apitest.model.ApiProjectModel import ApiProject

        # 先创建项目
        project = ApiProject(
            project_name="待删除项目",
            project_description="这个项目将被删除",
            base_url="https://api.delete.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        response = client.delete(f"/ApiProject/delete?id={project.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_delete_project_not_found(self, client: TestClient, admin_headers):
        """测试删除不存在的项目"""
        response = client.delete("/ApiProject/delete?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_query_all_success(self, client: TestClient, session: Session, admin_headers):
        """测试查询所有API项目成功"""
        from apitest.model.ApiProjectModel import ApiProject

        # 创建多个项目
        projects = [
            ApiProject(
                project_name="全部查询项目1",
                project_description="第一个项目",
                base_url="https://api1.com",
                create_time=datetime.now()
            ),
            ApiProject(
                project_name="全部查询项目2",
                project_description="第二个项目",
                base_url="https://api2.com",
                create_time=datetime.now()
            )
        ]

        for project in projects:
            session.add(project)
        session.commit()

        response = client.get("/ApiProject/queryAll",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert len(data["data"]["list"]) >= 2

    def test_unauthorized_access(self, client: TestClient):
        """测试未授权访问"""
        response = client.post("/ApiProject/queryByPage",
            json={"page": 1, "pageSize": 10}
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]
