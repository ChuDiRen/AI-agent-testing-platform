"""
PluginController 插件管理模块单元测试
"""
import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestPluginController:
    """插件控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询插件"""
        from plugin.model.PluginModel import Plugin
        
        plugin = Plugin(
            plugin_name="测试插件",
            plugin_code="test_plugin",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        
        response = client.post("/Plugin/queryByPage", json={
            "pageNum": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_page_with_filter(self, client: TestClient, session: Session):
        """测试带过滤的分页查询"""
        from plugin.model.PluginModel import Plugin
        
        plugin = Plugin(
            plugin_name="特殊插件",
            plugin_code="special_plugin",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        
        response = client.post("/Plugin/queryByPage", json={
            "pageNum": 1,
            "pageSize": 10,
            "plugin_name": "特殊"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询插件"""
        from plugin.model.PluginModel import Plugin
        
        plugin = Plugin(
            plugin_name="ID查询插件",
            plugin_code="id_query_plugin",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        session.refresh(plugin)
        
        response = client.get(f"/Plugin/queryById?id={plugin.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的插件"""
        response = client.get("/Plugin/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_register_plugin(self, client: TestClient):
        """测试注册插件"""
        response = client.post("/Plugin/register", json={
            "plugin": {
                "name": "注册测试插件",
                "code": "register_test_plugin",
                "type": "executor",
                "version": "1.0.0",
                "description": "测试插件描述"
            },
            "api": {
                "endpoint": "http://localhost:8080"
            },
            "capabilities": ["execute"],
            "requirements": {
                "dependencies": ["pytest"]
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_register_existing_plugin(self, client: TestClient, session: Session):
        """测试注册已存在的插件（更新）"""
        from plugin.model.PluginModel import Plugin
        
        plugin = Plugin(
            plugin_name="已存在插件",
            plugin_code="existing_plugin",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        
        response = client.post("/Plugin/register", json={
            "plugin": {
                "name": "更新后的插件名",
                "code": "existing_plugin",
                "type": "executor",
                "version": "2.0.0"
            },
            "api": {},
            "capabilities": [],
            "requirements": {}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "更新" in data["msg"]
    
    def test_toggle_plugin(self, client: TestClient, session: Session):
        """测试切换插件状态"""
        from plugin.model.PluginModel import Plugin
        
        plugin = Plugin(
            plugin_name="切换状态插件",
            plugin_code="toggle_plugin",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        session.refresh(plugin)
        
        response = client.put(f"/Plugin/toggle?id={plugin.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "禁用" in data["msg"]
    
    def test_toggle_plugin_not_found(self, client: TestClient):
        """测试切换不存在的插件状态"""
        response = client.put("/Plugin/toggle?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_unregister_plugin(self, client: TestClient, session: Session):
        """测试注销插件"""
        from plugin.model.PluginModel import Plugin
        
        plugin = Plugin(
            plugin_name="待注销插件",
            plugin_code="unregister_plugin",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        session.refresh(plugin)
        
        response = client.delete(f"/Plugin/unregister?id={plugin.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_unregister_plugin_not_found(self, client: TestClient):
        """测试注销不存在的插件"""
        response = client.delete("/Plugin/unregister?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_list_enabled_plugins(self, client: TestClient, session: Session):
        """测试获取已启用插件列表"""
        from plugin.model.PluginModel import Plugin
        
        plugin = Plugin(
            plugin_name="启用的插件",
            plugin_code="enabled_plugin",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        
        response = client.get("/Plugin/list/enabled")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_list_enabled_plugins_by_type(self, client: TestClient, session: Session):
        """测试按类型获取已启用插件"""
        from plugin.model.PluginModel import Plugin
        
        plugin = Plugin(
            plugin_name="执行器插件",
            plugin_code="executor_plugin",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        
        response = client.get("/Plugin/list/enabled?plugin_type=executor")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_health_check(self, client: TestClient, session: Session):
        """测试插件健康检查"""
        from plugin.model.PluginModel import Plugin
        
        plugin = Plugin(
            plugin_name="健康检查插件",
            plugin_code="health_check_plugin",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            command="python",
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        session.refresh(plugin)
        
        response = client.post(f"/Plugin/healthCheck?id={plugin.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_health_check_not_found(self, client: TestClient):
        """测试健康检查不存在的插件"""
        response = client.post("/Plugin/healthCheck?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1


class TestParseConsoleScripts:
    """解析console_scripts测试"""
    
    def test_parse_console_scripts(self):
        """测试解析setup.py中的console_scripts"""
        from plugin.api.PluginController import _parse_console_scripts
        
        setup_content = '''
setup(
    name="test-plugin",
    entry_points={
        "console_scripts": [
            "mycommand=mymodule:main",
            "another=another.module:run"
        ]
    }
)
'''
        result = _parse_console_scripts(setup_content)
        assert "mycommand" in result
        assert result["mycommand"] == "mymodule:main"
        assert "another" in result
    
    def test_parse_console_scripts_empty(self):
        """测试解析空的console_scripts"""
        from plugin.api.PluginController import _parse_console_scripts
        
        setup_content = '''
setup(
    name="test-plugin"
)
'''
        result = _parse_console_scripts(setup_content)
        assert result == {}
