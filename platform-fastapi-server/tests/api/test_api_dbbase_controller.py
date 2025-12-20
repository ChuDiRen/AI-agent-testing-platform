"""
API数据库配置管理 接口测试
接口清单:
- POST /ApiDbBase/queryByPage - 分页查询数据库配置
- GET /ApiDbBase/queryById - 根据ID查询数据库配置
- POST /ApiDbBase/insert - 新增数据库配置
- PUT /ApiDbBase/update - 更新数据库配置
- DELETE /ApiDbBase/delete - 删除数据库配置
"""
from datetime import datetime

import pytest


class TestApiDbBaseAPI:
    """API数据库配置管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """使用全局 api_client fixture"""
        self.client = api_client
        self.created_ids = []
        yield
        for db_id in self.created_ids:
            try:
                self.client.delete("/ApiDbBase/delete", params={"id": db_id})
            except:
                pass
    
    def _create_test_db_config(self):
        """创建测试数据库配置"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/ApiDbBase/insert", json={
            "project_id": 1,
            "name": f"测试数据库_{unique}",
            "ref_name": f"test_db_{unique}",
            "db_type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "test_db",
            "username": "root",
            "password": "test123"
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            db_id = response.json().get("data", {}).get("id")
            if db_id:
                self.created_ids.append(db_id)
            return db_id
        return None
    
    # ==================== POST /ApiDbBase/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/ApiDbBase/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_project_filter(self):
        """分页查询 - 带项目ID筛选"""
        response = self.client.post("/ApiDbBase/queryByPage", json={
            "page": 1, "pageSize": 10,
            "project_id": 1
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_name_filter(self):
        """分页查询 - 带连接名筛选"""
        response = self.client.post("/ApiDbBase/queryByPage", json={
            "page": 1, "pageSize": 10,
            "connect_name": "test"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/ApiDbBase/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /ApiDbBase/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        db_id = self._create_test_db_config()
        if db_id:
            response = self.client.get("/ApiDbBase/queryById", params={"id": db_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == db_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/ApiDbBase/queryById", params={"id": 99999})
        assert response.status_code == 200
    
    def test_query_by_id_missing_param(self):
        """ID查询 - 缺少参数"""
        response = self.client.get("/ApiDbBase/queryById")
        assert response.status_code == 422
    
    # ==================== POST /ApiDbBase/insert 新增配置测试 ====================
    
    def test_insert_success(self):
        """新增配置 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/ApiDbBase/insert", json={
            "project_id": 1,
            "name": f"测试数据库_{unique}",
            "ref_name": f"test_db_{unique}",
            "db_type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "test_db",
            "username": "root",
            "password": "test123"
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_duplicate_ref_name(self):
        """新增配置 - 重复引用名"""
        db_id = self._create_test_db_config()
        if db_id:
            response = self.client.get("/ApiDbBase/queryById", params={"id": db_id})
            ref_name = response.json()["data"]["ref_name"]
            response = self.client.post("/ApiDbBase/insert", json={
                "project_id": 1,
                "name": "重复测试",
                "ref_name": ref_name,
                "db_type": "mysql",
                "host": "localhost"
            })
            assert response.json()["code"] != 200 or "重复" in response.json().get("msg", "")
    
    def test_insert_missing_required(self):
        """新增配置 - 缺少必填字段"""
        response = self.client.post("/ApiDbBase/insert", json={
            "name": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /ApiDbBase/update 更新配置测试 ====================
    
    def test_update_success(self):
        """更新配置 - 正常请求"""
        db_id = self._create_test_db_config()
        if db_id:
            response = self.client.put("/ApiDbBase/update", json={
                "id": db_id,
                "name": "更新后的名称"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新配置 - 数据不存在"""
        response = self.client.put("/ApiDbBase/update", json={
            "id": 99999,
            "name": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /ApiDbBase/delete 删除配置测试 ====================
    
    def test_delete_success(self):
        """删除配置 - 正常请求"""
        db_id = self._create_test_db_config()
        if db_id:
            self.created_ids.remove(db_id)
            response = self.client.delete("/ApiDbBase/delete", params={"id": db_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除配置 - 数据不存在"""
        response = self.client.delete("/ApiDbBase/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
