"""
TaskController 任务调度模块接口测试
测试服务地址: http://127.0.0.1:5000
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestTaskController:
    """任务控制器测试类"""
    
    # ==================== 执行器列表接口 ====================
    
    def test_list_executors(self, client: TestClient, session: Session):
        """测试获取执行器列表"""
        from plugin.model.PluginModel import Plugin
        
        plugin = Plugin(
            plugin_name="测试执行器",
            plugin_code="test_executor",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            command="pytest",
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        
        response = client.get("/Task/executors")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_list_executors_empty(self, client: TestClient):
        """测试获取空执行器列表"""
        response = client.get("/Task/executors")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_list_executors_multiple(self, client: TestClient, session: Session):
        """测试获取多个执行器"""
        from plugin.model.PluginModel import Plugin
        
        executors = [
            Plugin(
                plugin_name="API执行器",
                plugin_code="api_executor",
                plugin_type="executor",
                version="1.0.0",
                is_enabled=1,
                command="pytest",
                create_time=datetime.now()
            ),
            Plugin(
                plugin_name="Web执行器",
                plugin_code="web_executor",
                plugin_type="executor",
                version="2.0.0",
                is_enabled=1,
                command="python",
                create_time=datetime.now()
            )
        ]
        for plugin in executors:
            session.add(plugin)
        session.commit()
        
        response = client.get("/Task/executors")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]) >= 2
    
    def test_list_executors_filter_disabled(self, client: TestClient, session: Session):
        """测试执行器列表 - 过滤禁用的"""
        from plugin.model.PluginModel import Plugin
        
        # 创建一个禁用的执行器
        disabled_plugin = Plugin(
            plugin_name="禁用执行器",
            plugin_code="disabled_executor",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=0,  # 禁用
            command="pytest",
            create_time=datetime.now()
        )
        session.add(disabled_plugin)
        session.commit()
        
        response = client.get("/Task/executors")
        
        assert response.status_code == 200
        data = response.json()
        # 禁用的执行器不应该出现在列表中
        codes = [e["plugin_code"] for e in data["data"]]
        assert "disabled_executor" not in codes
    
    def test_list_executors_filter_non_executor(self, client: TestClient, session: Session):
        """测试执行器列表 - 过滤非执行器类型"""
        from plugin.model.PluginModel import Plugin
        
        # 创建一个非执行器类型的插件
        reporter = Plugin(
            plugin_name="报告插件",
            plugin_code="reporter",
            plugin_type="reporter",  # 非executor类型
            version="1.0.0",
            is_enabled=1,
            command="report",
            create_time=datetime.now()
        )
        session.add(reporter)
        session.commit()
        
        response = client.get("/Task/executors")
        
        assert response.status_code == 200
        data = response.json()
        codes = [e["plugin_code"] for e in data["data"]]
        assert "reporter" not in codes
    
    # ==================== 执行测试接口 ====================
    
    def test_execute_test_plugin_not_found(self, client: TestClient):
        """测试执行不存在的插件"""
        response = client.post("/Task/execute", json={
            "plugin_code": "nonexistent_plugin",
            "test_case_id": 1,
            "test_case_content": "test: content"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_execute_test_missing_plugin_code(self, client: TestClient):
        """测试执行 - 缺少plugin_code"""
        response = client.post("/Task/execute", json={
            "test_case_id": 1,
            "test_case_content": "test: content"
        })
        
        assert response.status_code == 422
    
    def test_execute_test_missing_case_id(self, client: TestClient):
        """测试执行 - 缺少test_case_id"""
        response = client.post("/Task/execute", json={
            "plugin_code": "test_executor",
            "test_case_content": "test: content"
        })
        
        assert response.status_code == 422
    
    def test_execute_test_missing_content(self, client: TestClient):
        """测试执行 - 缺少test_case_content"""
        response = client.post("/Task/execute", json={
            "plugin_code": "test_executor",
            "test_case_id": 1
        })
        
        assert response.status_code == 422
    
    def test_execute_test_with_config(self, client: TestClient):
        """测试执行 - 带配置参数"""
        response = client.post("/Task/execute", json={
            "plugin_code": "test_executor",
            "test_case_id": 1,
            "test_case_content": "desc: 测试\nsteps:\n  - step1",
            "config": {
                "timeout": 30,
                "retry": 3,
                "env": "test"
            }
        })
        
        assert response.status_code == 200
    
    def test_execute_test_yaml_content(self, client: TestClient):
        """测试执行 - YAML格式用例内容"""
        yaml_content = """
desc: API接口测试
steps:
  - 发送请求:
      method: GET
      url: /api/users
  - 验证响应:
      status: 200
"""
        response = client.post("/Task/execute", json={
            "plugin_code": "api_executor",
            "test_case_id": 1,
            "test_case_content": yaml_content
        })
        
        assert response.status_code == 200
    
    # ==================== 任务状态查询接口 ====================
    
    def test_query_status_missing_fields(self, client: TestClient):
        """测试查询状态 - 缺少字段"""
        response = client.post("/Task/status", json={
            "plugin_code": "test_executor"
        })
        
        assert response.status_code == 422
    
    def test_query_status(self, client: TestClient):
        """测试查询任务状态"""
        response = client.post("/Task/status", json={
            "plugin_code": "test_executor",
            "task_id": "task_123",
            "temp_dir": "/tmp/test"
        })
        
        assert response.status_code == 200
    
    def test_query_status_invalid_task(self, client: TestClient):
        """测试查询状态 - 无效任务ID"""
        response = client.post("/Task/status", json={
            "plugin_code": "test_executor",
            "task_id": "invalid_task_id",
            "temp_dir": "/tmp/invalid"
        })
        
        assert response.status_code == 200
    
    # ==================== 获取测试报告接口 ====================
    
    def test_get_report(self, client: TestClient):
        """测试获取测试报告"""
        response = client.post("/Task/report", json={
            "plugin_code": "test_executor",
            "task_id": "task_123",
            "temp_dir": "/tmp/test"
        })
        
        assert response.status_code == 200
    
    def test_get_report_missing_fields(self, client: TestClient):
        """测试获取报告 - 缺少字段"""
        response = client.post("/Task/report", json={
            "plugin_code": "test_executor"
        })
        
        assert response.status_code == 422
    
    # ==================== 取消任务接口 ====================
    
    def test_cancel_task(self, client: TestClient):
        """测试取消任务"""
        response = client.post("/Task/cancel", json={
            "plugin_code": "test_executor",
            "task_id": "task_123",
            "temp_dir": "/tmp/test"
        })
        
        assert response.status_code == 200
    
    def test_cancel_task_missing_fields(self, client: TestClient):
        """测试取消任务 - 缺少字段"""
        response = client.post("/Task/cancel", json={
            "plugin_code": "test_executor"
        })
        
        assert response.status_code == 422
    
    def test_cancel_nonexistent_task(self, client: TestClient):
        """测试取消不存在的任务"""
        response = client.post("/Task/cancel", json={
            "plugin_code": "test_executor",
            "task_id": "nonexistent_task",
            "temp_dir": "/tmp/nonexistent"
        })
        
        assert response.status_code == 200


class TestTaskControllerIntegration:
    """任务控制器集成测试"""
    
    def test_executor_list_then_execute(self, client: TestClient, session: Session):
        """测试先获取执行器列表再执行"""
        from plugin.model.PluginModel import Plugin
        
        # 创建执行器
        plugin = Plugin(
            plugin_name="集成测试执行器",
            plugin_code="integration_executor",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            command="pytest",
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        
        # 获取执行器列表
        response = client.get("/Task/executors")
        assert response.status_code == 200
        executors = response.json()["data"]
        
        # 找到我们创建的执行器
        our_executor = next(
            (e for e in executors if e["plugin_code"] == "integration_executor"),
            None
        )
        
        if our_executor:
            # 使用该执行器执行测试
            response = client.post("/Task/execute", json={
                "plugin_code": our_executor["plugin_code"],
                "test_case_id": 1,
                "test_case_content": "test: integration"
            })
            assert response.status_code == 200
