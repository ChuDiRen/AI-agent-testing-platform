"""
API元数据管理 接口测试
接口清单:
- GET /ApiMeta/queryAll - 查询所有元数据
- POST /ApiMeta/queryByPage - 分页查询元数据
- GET /ApiMeta/queryById - 根据ID查询元数据
- POST /ApiMeta/insert - 上传文件并新增元数据
- PUT /ApiMeta/update - 更新元数据
- DELETE /ApiMeta/delete - 删除元数据
- GET /ApiMeta/downloadFile - 获取文件下载地址
"""
import pytest


class TestApiMetaAPI:
    """API元数据管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """使用全局 api_client fixture"""
        self.client = api_client
        self.created_ids = []
        yield
        for meta_id in self.created_ids:
            try:
                self.client.delete("/ApiMeta/delete", params={"id": meta_id})
            except:
                pass
    
    # ==================== GET /ApiMeta/queryAll 查询所有测试 ====================
    
    def test_query_all_success(self):
        """查询所有元数据 - 正常请求"""
        response = self.client.get("/ApiMeta/queryAll")
        data = self.client.assert_success(response)
        assert "data" in data
    
    # ==================== POST /ApiMeta/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/ApiMeta/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_name_filter(self):
        """分页查询 - 带名称筛选"""
        response = self.client.post("/ApiMeta/queryByPage", json={
            "page": 1, "pageSize": 10,
            "mate_name": "test"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_project_filter(self):
        """分页查询 - 带项目ID筛选"""
        response = self.client.post("/ApiMeta/queryByPage", json={
            "page": 1, "pageSize": 10,
            "project_id": 1
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_file_type_filter(self):
        """分页查询 - 带文件类型筛选"""
        response = self.client.post("/ApiMeta/queryByPage", json={
            "page": 1, "pageSize": 10,
            "file_type": "json"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/ApiMeta/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /ApiMeta/queryById ID查询测试 ====================
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/ApiMeta/queryById", params={"id": 99999})
        assert response.status_code == 200
    
    def test_query_by_id_missing_param(self):
        """ID查询 - 缺少参数"""
        response = self.client.get("/ApiMeta/queryById")
        assert response.status_code == 422
    
    # ==================== PUT /ApiMeta/update 更新元数据测试 ====================
    
    def test_update_not_exist(self):
        """更新元数据 - 数据不存在"""
        response = self.client.put("/ApiMeta/update", json={
            "id": 99999,
            "mate_name": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /ApiMeta/delete 删除元数据测试 ====================
    
    def test_delete_not_exist(self):
        """删除元数据 - 数据不存在"""
        response = self.client.delete("/ApiMeta/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_delete_missing_param(self):
        """删除元数据 - 缺少参数"""
        response = self.client.delete("/ApiMeta/delete")
        assert response.status_code == 422
    
    # ==================== GET /ApiMeta/downloadFile 下载文件测试 ====================
    
    def test_download_file_not_exist(self):
        """下载文件 - 文件不存在"""
        response = self.client.get("/ApiMeta/downloadFile", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_download_file_missing_param(self):
        """下载文件 - 缺少参数"""
        response = self.client.get("/ApiMeta/downloadFile")
        assert response.status_code == 422
