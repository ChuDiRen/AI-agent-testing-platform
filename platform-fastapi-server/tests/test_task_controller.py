"""
TaskController 任务调度模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestTaskController:
    """任务控制器测试类"""
    
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


class TestCommandExecutor:
    """命令执行器测试"""
    
    def test_parse_test_output(self):
        """测试解析测试输出"""
        from plugin.service.CommandExecutor import parse_test_output
        
        stdout = '''
test_case_execute[用例1] PASSED
test_case_execute[用例2] FAILED
========== 1 passed, 1 failed ==========
'''
        result = parse_test_output(stdout)
        
        assert len(result["test_cases"]) == 2
        assert result["test_cases"][0]["name"] == "用例1"
        assert result["test_cases"][0]["status"] == "PASSED"
        assert result["summary"]["passed"] == 1
        assert result["summary"]["failed"] == 1
    
    def test_parse_test_output_empty(self):
        """测试解析空输出"""
        from plugin.service.CommandExecutor import parse_test_output
        
        result = parse_test_output("")
        
        assert result["test_cases"] == []
        assert result["summary"] == {}
    
    def test_parse_test_output_with_response_data(self):
        """测试解析带响应数据的输出"""
        from plugin.service.CommandExecutor import parse_test_output
        
        stdout = '''
-----------current_response_data-----------
{"status": 200, "data": "test"}
-----------end current_response_data-----------
test_case_execute[用例1] PASSED
========== 1 passed ==========
'''
        result = parse_test_output(stdout)
        
        assert result["response_data"] is not None
        assert result["summary"]["passed"] == 1
