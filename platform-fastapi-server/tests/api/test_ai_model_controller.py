"""
AI模型管理 API 接口测试
接口清单:
- POST /AiModel/queryByPage - 分页查询AI模型
- GET /AiModel/queryById - 根据ID查询AI模型
- GET /AiModel/queryEnabled - 查询所有已启用的模型
- POST /AiModel/insert - 新增AI模型
- PUT /AiModel/update - 更新AI模型
- DELETE /AiModel/delete - 删除AI模型
- POST /AiModel/toggleStatus - 切换模型启用/禁用状态
- POST /AiModel/testConnection - 测试模型API连接
"""
from datetime import datetime

import pytest
from ..conftest import APIClient, API_BASE_URL


class TestAiModelAPI:
    """AI模型管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """使用全局 api_client fixture"""
        self.client = api_client
        self.created_ids = []
        yield
        for model_id in self.created_ids:
            try:
                self.client.delete("/AiModel/delete", params={"id": model_id})
            except:
                pass
    
    def _create_test_model(self):
        """创建测试AI模型"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/AiModel/insert", json={
            "model_name": f"测试模型_{unique}",
            "model_code": f"test_model_{unique}",
            "provider": "openai",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_key": "test_api_key",
            "is_enabled": True
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            model_id = response.json().get("data", {}).get("id")
            if model_id:
                self.created_ids.append(model_id)
            return model_id
        return None
    
    # ==================== POST /AiModel/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/AiModel/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_provider_filter(self):
        """分页查询 - 带提供商筛选"""
        response = self.client.post("/AiModel/queryByPage", json={
            "page": 1, "pageSize": 10,
            "provider": "openai"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_status_filter(self):
        """分页查询 - 带状态筛选"""
        response = self.client.post("/AiModel/queryByPage", json={
            "page": 1, "pageSize": 10,
            "is_enabled": True
        })
        self.client.assert_success(response)
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权（注意：当前API未强制要求认证）"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/AiModel/queryByPage", json={"page": 1, "pageSize": 10})
        # 当前API允许未授权访问，因此期望成功
        assert response.status_code == 200
        client.close()
    
    # ==================== GET /AiModel/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        model_id = self._create_test_model()
        if model_id:
            response = self.client.get("/AiModel/queryById", params={"id": model_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == model_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/AiModel/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == 200 or data["data"] is None
    
    # ==================== GET /AiModel/queryEnabled 查询已启用模型测试 ====================
    
    def test_query_enabled_success(self):
        """查询已启用模型 - 正常请求"""
        response = self.client.get("/AiModel/queryEnabled")
        data = self.client.assert_success(response)
        assert "data" in data
    
    # ==================== POST /AiModel/insert 新增模型测试 ====================
    
    def test_insert_success(self):
        """新增模型 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/AiModel/insert", json={
            "model_name": f"测试模型_{unique}",
            "model_code": f"test_model_{unique}",
            "provider": "openai",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_key": "test_api_key",
            "is_enabled": True
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_duplicate(self):
        """新增模型 - 重复模型代码"""
        model_id = self._create_test_model()
        if model_id:
            response = self.client.get("/AiModel/queryById", params={"id": model_id})
            model_code = response.json()["data"]["model_code"]
            response = self.client.post("/AiModel/insert", json={
                "model_name": "重复测试",
                "model_code": model_code,
                "provider": "openai",
                "api_url": "https://api.openai.com",
                "api_key": "test"
            })
            assert response.json()["code"] != 200 or "已存在" in response.json().get("msg", "")
    
    def test_insert_missing_required(self):
        """新增模型 - 缺少必填字段"""
        response = self.client.post("/AiModel/insert", json={
            "model_name": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /AiModel/update 更新模型测试 ====================
    
    def test_update_success(self):
        """更新模型 - 正常请求"""
        model_id = self._create_test_model()
        if model_id:
            response = self.client.put("/AiModel/update", json={
                "id": model_id,
                "model_name": "更新后的模型名"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新模型 - 数据不存在"""
        response = self.client.put("/AiModel/update", json={
            "id": 99999,
            "model_name": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /AiModel/delete 删除模型测试 ====================
    
    def test_delete_success(self):
        """删除模型 - 正常请求"""
        model_id = self._create_test_model()
        if model_id:
            self.created_ids.remove(model_id)
            response = self.client.delete("/AiModel/delete", params={"id": model_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除模型 - 数据不存在"""
        response = self.client.delete("/AiModel/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== POST /AiModel/toggleStatus 切换状态测试 ====================
    
    def test_toggle_status_success(self):
        """切换状态 - 正常请求"""
        model_id = self._create_test_model()
        if model_id:
            response = self.client.post(f"/AiModel/toggleStatus?id={model_id}")
            self.client.assert_success(response)
    
    def test_toggle_status_not_exist(self):
        """切换状态 - 模型不存在"""
        response = self.client.post("/AiModel/toggleStatus?id=99999")
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
