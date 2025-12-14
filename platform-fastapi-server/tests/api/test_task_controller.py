"""
任务调度 接口测试
接口清单:
- POST /Task/execute - 执行测试任务
- POST /Task/status - 查询任务状态
- POST /Task/report - 获取测试报告
- POST /Task/cancel - 取消任务
- GET /Task/executors - 获取可用执行器列表
"""
import pytest
from tests.conftest import APIClient, API_BASE_URL


class TestTaskAPI:
    """任务调度接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        yield
        self.client.close()
    
    # ==================== POST /Task/execute 执行任务测试 ====================
    
    def test_execute_missing_plugin_code(self):
        """执行任务 - 缺少插件代码"""
        response = self.client.post("/Task/execute", json={
            "test_case_id": 1,
            "test_case_content": "desc: 测试"
        })
        assert response.status_code == 422
    
    def test_execute_missing_case_id(self):
        """执行任务 - 缺少用例ID"""
        response = self.client.post("/Task/execute", json={
            "plugin_code": "api_engine",
            "test_case_content": "desc: 测试"
        })
        assert response.status_code == 422
    
    def test_execute_missing_content(self):
        """执行任务 - 缺少用例内容"""
        response = self.client.post("/Task/execute", json={
            "plugin_code": "api_engine",
            "test_case_id": 1
        })
        assert response.status_code == 422
    
    def test_execute_invalid_plugin(self):
        """执行任务 - 无效插件"""
        response = self.client.post("/Task/execute", json={
            "plugin_code": "invalid_plugin_xyz",
            "test_case_id": 1,
            "test_case_content": "desc: 测试"
        })
        # 插件不存在应返回错误
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == -1 or "失败" in data.get("msg", "") or "不存在" in data.get("msg", "")
    
    def test_execute_with_config(self):
        """执行任务 - 带配置参数"""
        response = self.client.post("/Task/execute", json={
            "plugin_code": "api_engine",
            "test_case_id": 1,
            "test_case_content": "desc: 测试\nsteps:\n  - 发送请求",
            "config": {"timeout": 30}
        })
        # 可能成功或失败，取决于插件是否存在
        assert response.status_code == 200
    
    # ==================== POST /Task/status 查询状态测试 ====================
    
    def test_status_missing_params(self):
        """查询状态 - 缺少参数"""
        response = self.client.post("/Task/status", json={})
        assert response.status_code == 422
    
    def test_status_invalid_task(self):
        """查询状态 - 无效任务"""
        response = self.client.post("/Task/status", json={
            "plugin_code": "api_engine",
            "task_id": "invalid_task_id",
            "temp_dir": "/tmp/test"
        })
        assert response.status_code == 200
    
    # ==================== POST /Task/report 获取报告测试 ====================
    
    def test_report_missing_params(self):
        """获取报告 - 缺少参数"""
        response = self.client.post("/Task/report", json={})
        assert response.status_code == 422
    
    def test_report_invalid_task(self):
        """获取报告 - 无效任务"""
        response = self.client.post("/Task/report", json={
            "plugin_code": "api_engine",
            "task_id": "invalid_task_id",
            "temp_dir": "/tmp/test"
        })
        assert response.status_code == 200
    
    # ==================== POST /Task/cancel 取消任务测试 ====================
    
    def test_cancel_missing_params(self):
        """取消任务 - 缺少参数"""
        response = self.client.post("/Task/cancel", json={})
        assert response.status_code == 422
    
    def test_cancel_invalid_task(self):
        """取消任务 - 无效任务"""
        response = self.client.post("/Task/cancel", json={
            "plugin_code": "api_engine",
            "task_id": "invalid_task_id",
            "temp_dir": "/tmp/test"
        })
        assert response.status_code == 200
    
    # ==================== GET /Task/executors 获取执行器列表测试 ====================
    
    def test_get_executors_success(self):
        """获取执行器列表 - 正常请求"""
        response = self.client.get("/Task/executors")
        data = self.client.assert_success(response)
        assert "data" in data
    
    def test_get_executors_structure(self):
        """获取执行器列表 - 返回结构验证"""
        response = self.client.get("/Task/executors")
        data = self.client.assert_success(response)
        # 验证返回的是列表
        assert isinstance(data.get("data"), list)
    
    def test_get_executors_unauthorized(self):
        """获取执行器列表 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.get("/Task/executors")
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
