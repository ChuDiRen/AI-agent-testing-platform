"""
ApiInfoController API接口信息管理模块单元测试
覆盖所有接口: queryByPage, queryById, insert, update, delete, getByProject, getMethods, importSwagger
"""
import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiInfoController:
    """API接口信息控制器测试类"""

    def test_query_by_page_success(self, client: TestClient, session: Session, admin_headers):
        """测试分页查询API接口成功"""
        from apitest.model.ApiInfoModel import ApiInfo
        from apitest.model.ApiProjectModel import ApiProject

        # 先创建项目和接口
        project = ApiProject(
            project_name="测试项目",
            project_description="用于测试的项目",
            base_url="https://api.test.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        api_info = ApiInfo(
            project_id=project.id,
            api_name="测试接口",
            request_method="GET",
            request_url="/test/endpoint",
            api_description="测试接口描述",
            create_time=datetime.now()
        )
        session.add(api_info)
        session.commit()

        response = client.post("/ApiInfo/queryByPage",
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
        from apitest.model.ApiInfoModel import ApiInfo
        from apitest.model.ApiProjectModel import ApiProject

        # 创建项目和多个接口
        project = ApiProject(
            project_name="过滤测试项目",
            project_description="用于过滤测试",
            base_url="https://api.filter.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        apis = [
            ApiInfo(
                project_id=project.id,
                api_name="用户登录接口",
                request_method="POST",
                request_url="/user/login",
                create_time=datetime.now()
            ),
            ApiInfo(
                project_id=project.id,
                api_name="用户信息接口",
                request_method="GET",
                request_url="/user/info",
                create_time=datetime.now()
            )
        ]

        for api in apis:
            session.add(api)
        session.commit()

        # 测试按项目ID过滤
        response = client.post("/ApiInfo/queryByPage",
            json={
                "page": 1,
                "pageSize": 10,
                "project_id": project.id
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) >= 2

        # 测试按接口名称过滤
        response = client.post("/ApiInfo/queryByPage",
            json={
                "page": 1,
                "pageSize": 10,
                "api_name": "登录"
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        if len(data["data"]["list"]) > 0:
            for api in data["data"]["list"]:
                assert "登录" in api["api_name"]

    def test_query_by_id_success(self, client: TestClient, session: Session, admin_headers):
        """测试根据ID查询API接口成功"""
        from apitest.model.ApiInfoModel import ApiInfo
        from apitest.model.ApiProjectModel import ApiProject

        project = ApiProject(
            project_name="单个查询项目",
            project_description="用于单个查询测试",
            base_url="https://api.single.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        api_info = ApiInfo(
            project_id=project.id,
            api_name="单个查询接口",
            request_method="GET",
            request_url="/single/endpoint",
            api_description="单个查询测试接口",
            create_time=datetime.now()
        )
        session.add(api_info)
        session.commit()

        response = client.get(f"/ApiInfo/queryById?id={api_info.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["api_name"] == "单个查询接口"
        assert data["data"]["request_method"] == "GET"

    def test_query_by_id_not_found(self, client: TestClient, admin_headers):
        """测试查询不存在的接口ID"""
        response = client.get("/ApiInfo/queryById?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "没有数据" in data["msg"]

    def test_insert_api_success(self, client: TestClient, session: Session, admin_headers):
        """测试新增API接口成功"""
        from apitest.model.ApiProjectModel import ApiProject

        project = ApiProject(
            project_name="新增接口项目",
            project_description="用于新增接口测试",
            base_url="https://api.insert.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        api_data = {
            "project_id": project.id,
            "api_name": "新增测试接口",
            "request_method": "POST",
            "request_url": "/new/endpoint",
            "api_description": "新增的测试接口",
            "request_header": '{"Content-Type": "application/json"}',
            "request_body": '{"key": "value"}',
            "response_example": '{"status": "success"}'
        }

        response = client.post("/ApiInfo/insert",
            json=api_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
        assert "id" in data["data"]

    def test_update_api_success(self, client: TestClient, session: Session, admin_headers):
        """测试更新API接口成功"""
        from apitest.model.ApiInfoModel import ApiInfo
        from apitest.model.ApiProjectModel import ApiProject

        project = ApiProject(
            project_name="更新接口项目",
            project_description="用于更新接口测试",
            base_url="https://api.update.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        api_info = ApiInfo(
            project_id=project.id,
            api_name="待更新接口",
            request_method="GET",
            request_url="/old/endpoint",
            create_time=datetime.now()
        )
        session.add(api_info)
        session.commit()

        update_data = {
            "id": api_info.id,
            "api_name": "已更新接口",
            "request_method": "PUT",
            "request_url": "/updated/endpoint",
            "api_description": "更新后的接口描述"
        }

        response = client.put("/ApiInfo/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_update_api_not_found(self, client: TestClient, admin_headers):
        """测试更新不存在的API接口"""
        update_data = {
            "id": 99999,
            "api_name": "不存在的接口",
            "request_method": "GET",
            "request_url": "/nonexistent"
        }

        response = client.put("/ApiInfo/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_delete_api_success(self, client: TestClient, session: Session, admin_headers):
        """测试删除API接口成功"""
        from apitest.model.ApiInfoModel import ApiInfo
        from apitest.model.ApiProjectModel import ApiProject

        project = ApiProject(
            project_name="删除接口项目",
            project_description="用于删除接口测试",
            base_url="https://api.delete.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        api_info = ApiInfo(
            project_id=project.id,
            api_name="待删除接口",
            request_method="DELETE",
            request_url="/delete/endpoint",
            create_time=datetime.now()
        )
        session.add(api_info)
        session.commit()

        response = client.delete(f"/ApiInfo/delete?id={api_info.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_delete_api_not_found(self, client: TestClient, admin_headers):
        """测试删除不存在的API接口"""
        response = client.delete("/ApiInfo/delete?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_get_by_project_success(self, client: TestClient, session: Session, admin_headers):
        """测试根据项目ID获取接口列表成功"""
        from apitest.model.ApiInfoModel import ApiInfo
        from apitest.model.ApiProjectModel import ApiProject

        project = ApiProject(
            project_name="项目接口列表",
            project_description="用于项目接口列表测试",
            base_url="https://api.project.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        # 创建多个接口
        apis = [
            ApiInfo(
                project_id=project.id,
                api_name="接口1",
                request_method="GET",
                request_url="/endpoint1",
                create_time=datetime.now()
            ),
            ApiInfo(
                project_id=project.id,
                api_name="接口2",
                request_method="POST",
                request_url="/endpoint2",
                create_time=datetime.now()
            )
        ]

        for api in apis:
            session.add(api)
        session.commit()

        response = client.get(f"/ApiInfo/getByProject?project_id={project.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert len(data["data"]["list"]) >= 2

    def test_get_methods_success(self, client: TestClient):
        """测试获取所有请求方法成功"""
        response = client.get("/ApiInfo/getMethods")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        methods = data["data"]["list"]

        # 验证包含所有常用HTTP方法
        expected_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        for method in expected_methods:
            assert method in methods

    def test_import_swagger_with_json(self, client: TestClient, session: Session, admin_headers):
        """测试通过JSON导入Swagger成功"""
        from apitest.model.ApiProjectModel import ApiProject

        project = ApiProject(
            project_name="Swagger导入项目",
            project_description="用于Swagger导入测试",
            base_url="https://api.swagger.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        swagger_json = {
            "openapi": "3.0.0",
            "info": {
                "title": "测试API",
                "version": "1.0.0"
            },
            "paths": {
                "/users": {
                    "get": {
                        "summary": "获取用户列表",
                        "responses": {
                            "200": {
                                "description": "成功",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array"}
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "创建用户",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        },
                        "responses": {
                            "201": {"description": "创建成功"}
                        }
                    }
                },
                "/users/{id}": {
                    "get": {
                        "summary": "获取用户详情",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"}
                            }
                        ],
                        "responses": {
                            "200": {"description": "成功"}
                        }
                    }
                }
            }
        }

        response = client.post("/ApiInfo/importSwagger",
            json={
                "project_id": project.id,
                "swagger_json": swagger_json,
                "override_existing": False
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 验证导入结果包含统计信息
        assert "total_apis" in data["data"]
        assert "imported_apis" in data["data"]

    def test_import_swagger_override_existing(self, client: TestClient, session: Session, admin_headers):
        """测试覆盖现有接口导入Swagger"""
        from apitest.model.ApiInfoModel import ApiInfo
        from apitest.model.ApiProjectModel import ApiProject

        project = ApiProject(
            project_name="覆盖测试项目",
            project_description="用于覆盖测试",
            base_url="https://api.override.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        # 先创建一个现有接口
        existing_api = ApiInfo(
            project_id=project.id,
            api_name="/users",
            request_method="GET",
            request_url="/users",
            create_time=datetime.now()
        )
        session.add(existing_api)
        session.commit()

        swagger_json = {
            "openapi": "3.0.0",
            "info": {"title": "覆盖测试API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "summary": "获取用户列表（更新版）",
                        "responses": {"200": {"description": "成功"}}
                    }
                }
            }
        }

        response = client.post("/ApiInfo/importSwagger",
            json={
                "project_id": project.id,
                "swagger_json": swagger_json,
                "override_existing": True
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_import_swagger_invalid_json(self, client: TestClient, session: Session, admin_headers):
        """测试导入无效Swagger JSON"""
        from apitest.model.ApiProjectModel import ApiProject

        project = ApiProject(
            project_name="无效JSON项目",
            project_description="用于无效JSON测试",
            base_url="https://api.invalid.com",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()

        # 无效的Swagger JSON
        invalid_swagger = {
            "invalid": "structure"
        }

        response = client.post("/ApiInfo/importSwagger",
            json={
                "project_id": project.id,
                "swagger_json": invalid_swagger,
                "override_existing": False
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1

    def test_unauthorized_access(self, client: TestClient):
        """测试未授权访问"""
        response = client.post("/ApiInfo/queryByPage",
            json={"page": 1, "pageSize": 10}
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]
