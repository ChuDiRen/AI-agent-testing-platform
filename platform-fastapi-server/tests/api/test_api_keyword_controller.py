"""
API关键字管理 接口测试
接口清单:
- GET /ApiKeyWord/queryAll - 查询所有关键字
- POST /ApiKeyWord/queryByPage - 分页查询关键字
- GET /ApiKeyWord/queryById - 根据ID查询关键字
- POST /ApiKeyWord/insert - 新增关键字
- PUT /ApiKeyWord/update - 更新关键字
- DELETE /ApiKeyWord/delete - 删除关键字
- GET /ApiKeyWord/queryByOperationType - 根据操作类型查询关键字
- GET /ApiKeyWord/getKeywordFields - 获取关键字字段描述
- GET /ApiKeyWord/queryGroupedByEngine - 按执行引擎分组查询
"""
from datetime import datetime

import pytest
from tests.conftest import APIClient, API_BASE_URL


class TestApiKeyWordAPI:
    """API关键字管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        self.created_ids = []
        yield
        for keyword_id in self.created_ids:
            try:
                self.client.delete("/ApiKeyWord/delete", params={"id": keyword_id})
            except:
                pass
        self.client.close()
    
    def _create_test_keyword(self):
        """创建测试关键字"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/ApiKeyWord/insert", json={
            "name": f"测试关键字_{unique}",
            "keyword_fun_name": f"test_keyword_{unique}",
            "keyword_desc": "测试关键字描述",
            "operation_type_id": 1,
            "is_enabled": "1"
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            keyword_id = response.json().get("data", {}).get("id")
            if keyword_id:
                self.created_ids.append(keyword_id)
            return keyword_id
        return None
    
    # ==================== GET /ApiKeyWord/queryAll 查询所有测试 ====================
    
    def test_query_all_success(self):
        """查询所有关键字 - 正常请求"""
        response = self.client.get("/ApiKeyWord/queryAll")
        data = self.client.assert_success(response)
        assert "data" in data
    
    # ==================== POST /ApiKeyWord/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/ApiKeyWord/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_filter(self):
        """分页查询 - 带关键字名筛选"""
        response = self.client.post("/ApiKeyWord/queryByPage", json={
            "page": 1, "pageSize": 10,
            "name": "request"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_operation_type(self):
        """分页查询 - 带操作类型筛选"""
        response = self.client.post("/ApiKeyWord/queryByPage", json={
            "page": 1, "pageSize": 10,
            "operation_type_id": 1
        })
        self.client.assert_success(response)
    
    def test_query_by_page_empty_result(self):
        """分页查询 - 空结果"""
        response = self.client.post("/ApiKeyWord/queryByPage", json={
            "page": 1, "pageSize": 10,
            "name": "不存在的关键字_xyz123"
        })
        data = self.client.assert_success(response)
        assert data["total"] == 0 or len(data["data"]) == 0
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/ApiKeyWord/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /ApiKeyWord/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        keyword_id = self._create_test_keyword()
        if keyword_id:
            response = self.client.get("/ApiKeyWord/queryById", params={"id": keyword_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == keyword_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/ApiKeyWord/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == 200 or data["data"] is None
    
    # ==================== POST /ApiKeyWord/insert 新增关键字测试 ====================
    
    def test_insert_success(self):
        """新增关键字 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/ApiKeyWord/insert", json={
            "name": f"测试关键字_{unique}",
            "keyword_fun_name": f"test_keyword_{unique}",
            "keyword_desc": "测试关键字描述",
            "operation_type_id": 1,
            "is_enabled": "1"
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_duplicate(self):
        """新增关键字 - 重复方法名"""
        keyword_id = self._create_test_keyword()
        if keyword_id:
            response = self.client.get("/ApiKeyWord/queryById", params={"id": keyword_id})
            keyword_fun_name = response.json()["data"]["keyword_fun_name"]
            response = self.client.post("/ApiKeyWord/insert", json={
                "name": "重复测试",
                "keyword_fun_name": keyword_fun_name,
                "operation_type_id": 1,
                "is_enabled": "1"
            })
            assert response.json()["code"] != 200 or "重复" in response.json().get("msg", "")
    
    def test_insert_missing_required(self):
        """新增关键字 - 缺少必填字段"""
        response = self.client.post("/ApiKeyWord/insert", json={
            "keyword_desc": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /ApiKeyWord/update 更新关键字测试 ====================
    
    def test_update_success(self):
        """更新关键字 - 正常请求"""
        keyword_id = self._create_test_keyword()
        if keyword_id:
            response = self.client.put("/ApiKeyWord/update", json={
                "id": keyword_id,
                "keyword_desc": "更新后的描述"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新关键字 - 数据不存在"""
        response = self.client.put("/ApiKeyWord/update", json={
            "id": 99999,
            "keyword_desc": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /ApiKeyWord/delete 删除关键字测试 ====================
    
    def test_delete_success(self):
        """删除关键字 - 正常请求"""
        keyword_id = self._create_test_keyword()
        if keyword_id:
            self.created_ids.remove(keyword_id)
            response = self.client.delete("/ApiKeyWord/delete", params={"id": keyword_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除关键字 - 数据不存在"""
        response = self.client.delete("/ApiKeyWord/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== GET /ApiKeyWord/queryByOperationType 按操作类型查询测试 ====================
    
    def test_query_by_operation_type_success(self):
        """按操作类型查询 - 正常请求"""
        response = self.client.get("/ApiKeyWord/queryByOperationType", params={"operation_type_id": 1})
        data = self.client.assert_success(response)
        assert "data" in data
    
    # ==================== GET /ApiKeyWord/queryGroupedByEngine 按引擎分组查询测试 ====================
    
    def test_query_grouped_by_engine_success(self):
        """按引擎分组查询 - 正常请求"""
        response = self.client.get("/ApiKeyWord/queryGroupedByEngine")
        data = self.client.assert_success(response)
        assert "data" in data
