"""
代码生成器-表配置管理 API 接口测试
接口清单:
- GET /GenTable/dbTables - 获取数据库可导入表
- POST /GenTable/importTables - 批量导入表配置
- POST /GenTable/queryByPage - 分页查询表配置
- GET /GenTable/queryById - 根据ID查询表配置
- PUT /GenTable/update - 更新表配置
- DELETE /GenTable/delete - 删除表配置
"""
import pytest
from ..conftest import APIClient, API_BASE_URL


class TestGenTableAPI:
    """代码生成器-表配置管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """使用全局 api_client fixture"""
        self.client = api_client
        self.created_ids = []
        yield
        for table_id in self.created_ids:
            try:
                self.client.delete("/GenTable/delete", params={"id": table_id})
            except:
                pass
        self.client.close()
    
    # ==================== GET /GenTable/dbTables 获取可导入表测试 ====================
    
    def test_get_db_tables_success(self):
        """获取可导入表 - 正常请求"""
        response = self.client.get("/GenTable/dbTables")
        data = self.client.assert_success(response)
        assert "data" in data
    
    def test_get_db_tables_unauthorized(self):
        """获取可导入表 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.get("/GenTable/dbTables")
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== POST /GenTable/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/GenTable/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_filter(self):
        """分页查询 - 带表名筛选"""
        response = self.client.post("/GenTable/queryByPage", json={
            "page": 1, "pageSize": 10,
            "table_name": "user"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_empty_result(self):
        """分页查询 - 空结果"""
        response = self.client.post("/GenTable/queryByPage", json={
            "page": 1, "pageSize": 10,
            "table_name": "不存在的表_xyz123"
        })
        data = self.client.assert_success(response)
        assert data["total"] == 0 or len(data["data"]) == 0
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/GenTable/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /GenTable/queryById ID查询测试 ====================
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/GenTable/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == -1 or "不存在" in data.get("msg", "")
    
    # ==================== PUT /GenTable/update 更新表配置测试 ====================
    
    def test_update_not_exist(self):
        """更新表配置 - 数据不存在"""
        response = self.client.put("/GenTable/update", json={
            "id": 99999,
            "class_name": "TestClass"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /GenTable/delete 删除表配置测试 ====================
    
    def test_delete_not_exist(self):
        """删除表配置 - 数据不存在"""
        response = self.client.delete("/GenTable/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
