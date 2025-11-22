"""
ApiInfoController 单元测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiInfoController:
    """API接口信息控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, test_api_info):
        """测试分页查询"""
        response = client.post("/ApiInfo/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_query_by_id(self, client: TestClient, test_api_info):
        """测试ID查询"""
        response = client.get(f"/ApiInfo/queryById?id={test_api_info.id}")
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_insert(self, client: TestClient, test_project):
        """测试新增接口"""
        data = {
            "project_id": test_project.id,
            "api_name": "测试接口",
            "request_method": "POST",
            "request_url": "https://api.test.com"
        }
        response = client.post("/ApiInfo/insert", json=data)
        assert response.status_code == 200
    
    def test_update(self, client: TestClient, test_api_info):
        """测试更新"""
        response = client.put("/ApiInfo/update", json={"id": test_api_info.id, "api_name": "updated"})
        assert response.status_code == 200
    
    def test_delete(self, client: TestClient, test_api_info):
        """测试删除"""
        response = client.delete(f"/ApiInfo/delete?id={test_api_info.id}")
        assert response.status_code == 200
