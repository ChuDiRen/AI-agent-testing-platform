"""
API接口信息管理 接口测试
接口清单:
- POST /ApiInfo/queryByPage - 分页查询API接口信息
- GET /ApiInfo/queryById - 根据ID查询API接口信息
- POST /ApiInfo/insert - 新增API接口信息
- PUT /ApiInfo/update - 更新API接口信息
- DELETE /ApiInfo/delete - 删除API接口信息
- GET /ApiInfo/getByProject - 根据项目ID获取接口列表
- GET /ApiInfo/getMethods - 获取所有请求方法
- POST /ApiInfo/importSwagger - 导入Swagger文档
"""
from datetime import datetime

import pytest
from tests.conftest import APIClient, API_BASE_URL


class TestApiInfoAPI:
    """API接口信息管理测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        self.created_ids = []
        self.created_project_ids = []
        yield
        for api_id in self.created_ids:
            try:
                self.client.delete("/ApiInfo/delete", params={"id": api_id})
            except:
                pass
        for project_id in self.created_project_ids:
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
            "base_url": "http://localhost:5000"
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            project_id = response.json().get("data", {}).get("id")
            if project_id:
                self.created_project_ids.append(project_id)
            return project_id
        return None
    
    def _create_test_api(self, project_id=None):
        """创建测试API"""
        if not project_id:
            project_id = self._create_test_project()
        if not project_id:
            return None
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"/test/api_{unique}",
            "request_method": "GET",
            "api_desc": "测试接口"
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            api_id = response.json().get("data", {}).get("id")
            if api_id:
                self.created_ids.append(api_id)
            return api_id
        return None
    
    # ==================== POST /ApiInfo/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/ApiInfo/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_filter(self):
        """分页查询 - 带接口名筛选"""
        response = self.client.post("/ApiInfo/queryByPage", json={
            "page": 1, "pageSize": 10,
            "api_name": "test"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_method_filter(self):
        """分页查询 - 带请求方法筛选"""
        response = self.client.post("/ApiInfo/queryByPage", json={
            "page": 1, "pageSize": 10,
            "request_method": "GET"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_empty_result(self):
        """分页查询 - 空结果"""
        response = self.client.post("/ApiInfo/queryByPage", json={
            "page": 1, "pageSize": 10,
            "api_name": "不存在的接口_xyz123"
        })
        data = self.client.assert_success(response)
        assert data["total"] == 0 or len(data["data"]) == 0
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/ApiInfo/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /ApiInfo/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        api_id = self._create_test_api()
        if api_id:
            response = self.client.get("/ApiInfo/queryById", params={"id": api_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == api_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/ApiInfo/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == 200 or data["data"] is None
    
    # ==================== POST /ApiInfo/insert 新增接口测试 ====================
    
    def test_insert_success(self):
        """新增接口 - 正常请求"""
        project_id = self._create_test_project()
        if project_id:
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            response = self.client.post("/ApiInfo/insert", json={
                "project_id": project_id,
                "api_name": f"/test/api_{unique}",
                "request_method": "POST",
                "api_desc": "测试接口"
            })
            data = self.client.assert_success(response)
            assert "id" in data.get("data", {})
            self.created_ids.append(data["data"]["id"])
    
    def test_insert_missing_required(self):
        """新增接口 - 缺少必填字段"""
        response = self.client.post("/ApiInfo/insert", json={
            "api_desc": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /ApiInfo/update 更新接口测试 ====================
    
    def test_update_success(self):
        """更新接口 - 正常请求"""
        api_id = self._create_test_api()
        if api_id:
            response = self.client.put("/ApiInfo/update", json={
                "id": api_id,
                "api_desc": "更新后的描述"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新接口 - 数据不存在"""
        response = self.client.put("/ApiInfo/update", json={
            "id": 99999,
            "api_desc": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /ApiInfo/delete 删除接口测试 ====================
    
    def test_delete_success(self):
        """删除接口 - 正常请求"""
        api_id = self._create_test_api()
        if api_id:
            self.created_ids.remove(api_id)
            response = self.client.delete("/ApiInfo/delete", params={"id": api_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除接口 - 数据不存在"""
        response = self.client.delete("/ApiInfo/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== GET /ApiInfo/getByProject 按项目查询测试 ====================
    
    def test_get_by_project_success(self):
        """按项目查询 - 正常请求"""
        project_id = self._create_test_project()
        if project_id:
            self._create_test_api(project_id)
            response = self.client.get("/ApiInfo/getByProject", params={"project_id": project_id})
            data = self.client.assert_success(response)
            assert "data" in data
    
    # ==================== GET /ApiInfo/getMethods 获取请求方法测试 ====================
    
    def test_get_methods_success(self):
        """获取请求方法 - 正常请求"""
        response = self.client.get("/ApiInfo/getMethods")
        data = self.client.assert_success(response)
        assert "data" in data
        assert "GET" in data["data"]
        assert "POST" in data["data"]
