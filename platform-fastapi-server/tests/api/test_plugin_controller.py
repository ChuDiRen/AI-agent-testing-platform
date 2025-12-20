"""
插件管理 API 接口测试
接口清单:
- POST /Plugin/register - 注册插件
- POST /Plugin/queryByPage - 分页查询插件列表
- GET /Plugin/queryById - 根据ID查询插件详情
- PUT /Plugin/update - 更新插件配置
- DELETE /Plugin/unregister - 注销插件
- PUT /Plugin/toggle - 启用/禁用插件
- POST /Plugin/healthCheck - 检查插件健康状态
- GET /Plugin/list/enabled - 获取所有已启用的插件
"""
import pytest
from ..conftest import APIClient, API_BASE_URL


class TestPluginAPI:
    """插件管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """使用全局 api_client fixture"""
        self.client = api_client
        self.created_ids = []
        yield
        for plugin_id in self.created_ids:
            try:
                self.client.delete("/Plugin/unregister", params={"id": plugin_id})
            except:
                pass
        self.client.close()
    
    # ==================== POST /Plugin/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/Plugin/queryByPage", json={
            "pageNum": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
    
    def test_query_by_page_with_filter(self):
        """分页查询 - 带插件名筛选"""
        response = self.client.post("/Plugin/queryByPage", json={
            "pageNum": 1, "pageSize": 10,
            "plugin_name": "api"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_type_filter(self):
        """分页查询 - 带插件类型筛选"""
        response = self.client.post("/Plugin/queryByPage", json={
            "pageNum": 1, "pageSize": 10,
            "plugin_type": "executor"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_empty_result(self):
        """分页查询 - 空结果"""
        response = self.client.post("/Plugin/queryByPage", json={
            "pageNum": 1, "pageSize": 10,
            "plugin_name": "不存在的插件_xyz123"
        })
        data = self.client.assert_success(response)
        assert data["data"]["total"] == 0 or len(data["data"]["rows"]) == 0
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/Plugin/queryByPage", json={"pageNum": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /Plugin/queryById ID查询测试 ====================
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/Plugin/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == -1 or "不存在" in data.get("msg", "")
    
    # ==================== GET /Plugin/list/enabled 获取已启用插件测试 ====================
    
    def test_list_enabled_success(self):
        """获取已启用插件 - 正常请求"""
        response = self.client.get("/Plugin/list/enabled")
        data = self.client.assert_success(response)
        assert "data" in data
    
    def test_list_enabled_with_type(self):
        """获取已启用插件 - 按类型筛选"""
        response = self.client.get("/Plugin/list/enabled", params={"plugin_type": "executor"})
        self.client.assert_success(response)
