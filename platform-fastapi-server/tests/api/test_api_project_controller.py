"""
API项目管理 接口测试
接口清单:
- POST /ApiProject/queryByPage - 分页查询API项目
- GET /ApiProject/queryById - 根据ID查询API项目
- POST /ApiProject/insert - 新增API项目
- PUT /ApiProject/update - 更新API项目
- DELETE /ApiProject/delete - 删除API项目
- GET /ApiProject/queryAll - 查询所有API项目
"""
from datetime import datetime

import pytest
from tests.conftest import APIClient, API_BASE_URL


class TestApiProjectAPI:
    """API项目管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        self.created_ids = []
        yield
        for project_id in self.created_ids:
            try:
                self.client.delete("/ApiProject/delete", params={"id": project_id})
            except:
                pass
        self.client.close()
    
    def _create_test_project(self):
        """创建测试项目"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/ApiProject/insert", json={
            "project_name": f"测试项目_{unique}",
            "project_desc": "测试项目描述",
            "base_url": "http://localhost:5000"
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            project_id = response.json().get("data", {}).get("id")
            if project_id:
                self.created_ids.append(project_id)
            return project_id
        return None
    
    # ==================== POST /ApiProject/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/ApiProject/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_filter(self):
        """分页查询 - 带项目名筛选"""
        response = self.client.post("/ApiProject/queryByPage", json={
            "page": 1, "pageSize": 10,
            "project_name": "测试"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_empty_result(self):
        """分页查询 - 空结果"""
        response = self.client.post("/ApiProject/queryByPage", json={
            "page": 1, "pageSize": 10,
            "project_name": "不存在的项目_xyz123"
        })
        data = self.client.assert_success(response)
        assert data["total"] == 0 or len(data["data"]) == 0
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/ApiProject/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /ApiProject/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        project_id = self._create_test_project()
        if project_id:
            response = self.client.get("/ApiProject/queryById", params={"id": project_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == project_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/ApiProject/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == 200 or data["data"] is None
    
    # ==================== POST /ApiProject/insert 新增项目测试 ====================
    
    def test_insert_success(self):
        """新增项目 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/ApiProject/insert", json={
            "project_name": f"测试项目_{unique}",
            "project_desc": "测试项目描述",
            "base_url": "http://localhost:5000"
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_missing_required(self):
        """新增项目 - 缺少必填字段"""
        response = self.client.post("/ApiProject/insert", json={
            "project_desc": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    def test_insert_empty_name(self):
        """新增项目 - 空项目名"""
        response = self.client.post("/ApiProject/insert", json={
            "project_name": "",
            "base_url": "http://localhost:5000"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /ApiProject/update 更新项目测试 ====================
    
    def test_update_success(self):
        """更新项目 - 正常请求"""
        project_id = self._create_test_project()
        if project_id:
            response = self.client.put("/ApiProject/update", json={
                "id": project_id,
                "project_desc": "更新后的描述"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新项目 - 数据不存在"""
        response = self.client.put("/ApiProject/update", json={
            "id": 99999,
            "project_desc": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /ApiProject/delete 删除项目测试 ====================
    
    def test_delete_success(self):
        """删除项目 - 正常请求"""
        project_id = self._create_test_project()
        if project_id:
            self.created_ids.remove(project_id)
            response = self.client.delete("/ApiProject/delete", params={"id": project_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除项目 - 数据不存在"""
        response = self.client.delete("/ApiProject/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== GET /ApiProject/queryAll 查询所有测试 ====================
    
    def test_query_all_success(self):
        """查询所有 - 正常请求"""
        response = self.client.get("/ApiProject/queryAll")
        data = self.client.assert_success(response)
        assert "data" in data
