"""
API测试历史管理 接口测试
接口清单:
- POST /ApiHistory/queryByPage - 分页查询API测试历史
- GET /ApiHistory/queryById - 根据ID查询API测试历史
- POST /ApiHistory/execute - 执行API接口测试
- GET /ApiHistory/status - 查询API测试状态
- DELETE /ApiHistory/delete - 删除API测试历史
- GET /ApiHistory/queryByPlanId - 根据测试计划ID查询历史记录
- GET /ApiHistory/queryByExecutionUuid - 根据批量执行UUID查询历史记录
"""
import pytest
from tests.conftest import APIClient, API_BASE_URL


class TestApiHistoryAPI:
    """API测试历史管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        yield
        self.client.close()
    
    # ==================== POST /ApiHistory/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/ApiHistory/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_status_filter(self):
        """分页查询 - 带状态筛选"""
        response = self.client.post("/ApiHistory/queryByPage", json={
            "page": 1, "pageSize": 10,
            "test_status": "success"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_project_filter(self):
        """分页查询 - 带项目ID筛选"""
        response = self.client.post("/ApiHistory/queryByPage", json={
            "page": 1, "pageSize": 10,
            "project_id": 1
        })
        self.client.assert_success(response)
    
    def test_query_by_page_empty_result(self):
        """分页查询 - 空结果"""
        response = self.client.post("/ApiHistory/queryByPage", json={
            "page": 1, "pageSize": 10,
            "project_id": 99999
        })
        data = self.client.assert_success(response)
        assert data["total"] == 0 or len(data["data"]) == 0
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/ApiHistory/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /ApiHistory/queryById ID查询测试 ====================
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/ApiHistory/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == 200 or data["data"] is None
    
    # ==================== GET /ApiHistory/status 查询测试状态测试 ====================
    
    def test_status_not_exist(self):
        """查询测试状态 - 记录不存在"""
        response = self.client.get("/ApiHistory/status", params={"test_id": 99999})
        data = response.json()
        assert data["code"] == -1 or "不存在" in data.get("msg", "")
    
    # ==================== DELETE /ApiHistory/delete 删除测试历史测试 ====================
    
    def test_delete_not_exist(self):
        """删除测试历史 - 数据不存在"""
        response = self.client.delete("/ApiHistory/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== GET /ApiHistory/queryByPlanId 按计划ID查询测试 ====================
    
    def test_query_by_plan_id_success(self):
        """按计划ID查询 - 正常请求"""
        response = self.client.get("/ApiHistory/queryByPlanId", params={"plan_id": 1})
        data = self.client.assert_success(response)
        assert "data" in data
    
    # ==================== GET /ApiHistory/queryByExecutionUuid 按执行UUID查询测试 ====================
    
    def test_query_by_execution_uuid_success(self):
        """按执行UUID查询 - 正常请求"""
        response = self.client.get("/ApiHistory/queryByExecutionUuid", params={"execution_uuid": "test-uuid-123"})
        data = self.client.assert_success(response)
        assert "data" in data
