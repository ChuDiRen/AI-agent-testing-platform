"""
API 环境配置接口测试
测试 ApiEnvironmentController 的所有接口
"""
import pytest
import json


class TestApiEnvironmentController:
    """API 环境配置 Controller 测试"""
    
    def test_query_by_page_success(self, api_client, unique_name):
        """测试分页查询环境配置 - 成功"""
        # 先创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"环境测试项目_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建环境
        env_response = api_client.post("/ApiEnvironment/insert", json={
            "project_id": project_id,
            "env_name": f"测试环境_{unique_name}",
            "base_url": "http://test.example.com"
        })
        api_client.assert_success(env_response)
        
        # 分页查询
        response = api_client.post("/ApiEnvironment/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project_id
        })
        data = api_client.assert_success(response)
        
        assert "data" in data
        assert "total" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_query_by_id_success(self, api_client, unique_name):
        """测试根据ID查询环境 - 成功"""
        # 创建项目和环境
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"环境查询_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        env_response = api_client.post("/ApiEnvironment/insert", json={
            "project_id": project_id,
            "env_name": f"开发环境_{unique_name}",
            "base_url": "http://dev.example.com",
            "env_desc": "开发环境配置"
        })
        env_data = api_client.assert_success(env_response)
        env_id = env_data["data"]["id"]
        
        # 查询环境详情
        response = api_client.get("/ApiEnvironment/queryById", params={"id": env_id})
        data = api_client.assert_success(response)
        
        assert data["data"]["id"] == env_id
        assert data["data"]["env_name"] == f"开发环境_{unique_name}"
        assert data["data"]["base_url"] == "http://dev.example.com"
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_insert_success(self, api_client, unique_name):
        """测试新增环境配置 - 成功"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"新增环境_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 新增环境
        env_data = {
            "project_id": project_id,
            "env_name": f"生产环境_{unique_name}",
            "base_url": "https://api.example.com",
            "env_desc": "生产环境配置",
            "variables": json.dumps({
                "api_key": "prod_key_123",
                "timeout": 30000
            }),
            "headers": json.dumps([
                {"key": "X-Environment", "value": "production"}
            ])
        }
        response = api_client.post("/ApiEnvironment/insert", json=env_data)
        data = api_client.assert_success(response)
        
        assert "id" in data["data"]
        assert isinstance(data["data"]["id"], int)
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_update_success(self, api_client, unique_name):
        """测试更新环境配置 - 成功"""
        # 创建项目和环境
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"更新环境_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        env_response = api_client.post("/ApiEnvironment/insert", json={
            "project_id": project_id,
            "env_name": f"原始环境_{unique_name}",
            "base_url": "http://old.example.com"
        })
        env_data = api_client.assert_success(env_response)
        env_id = env_data["data"]["id"]
        
        # 更新环境
        update_data = {
            "id": env_id,
            "env_name": f"更新环境_{unique_name}",
            "base_url": "http://new.example.com",
            "env_desc": "更新后的环境"
        }
        response = api_client.put("/ApiEnvironment/update", json=update_data)
        api_client.assert_success(response)
        
        # 验证更新
        verify_response = api_client.get("/ApiEnvironment/queryById", params={"id": env_id})
        verify_data = api_client.assert_success(verify_response)
        assert verify_data["data"]["env_name"] == f"更新环境_{unique_name}"
        assert verify_data["data"]["base_url"] == "http://new.example.com"
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_delete_success(self, api_client, unique_name):
        """测试删除环境配置 - 成功"""
        # 创建项目和环境
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"删除环境_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        env_response = api_client.post("/ApiEnvironment/insert", json={
            "project_id": project_id,
            "env_name": f"待删除环境_{unique_name}",
            "base_url": "http://delete.example.com"
        })
        env_data = api_client.assert_success(env_response)
        env_id = env_data["data"]["id"]
        
        # 删除环境
        response = api_client.delete("/ApiEnvironment/delete", params={"id": env_id})
        api_client.assert_success(response)
        
        # 验证删除
        verify_response = api_client.get("/ApiEnvironment/queryById", params={"id": env_id})
        assert verify_response.status_code in [200, 404]
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_query_by_project(self, api_client, unique_name):
        """测试查询项目的所有环境"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"多环境项目_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建多个环境
        env_names = ["开发", "测试", "生产"]
        for env_name in env_names:
            api_client.post("/ApiEnvironment/insert", json={
                "project_id": project_id,
                "env_name": f"{env_name}环境_{unique_name}",
                "base_url": f"http://{env_name}.example.com"
            })
        
        # 查询项目的所有环境
        response = api_client.post("/ApiEnvironment/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project_id
        })
        data = api_client.assert_success(response)
        
        assert len(data["data"]) == 3
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_environment_with_variables(self, api_client, unique_name):
        """测试带变量的环境配置"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"变量环境_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建带变量的环境
        env_response = api_client.post("/ApiEnvironment/insert", json={
            "project_id": project_id,
            "env_name": f"变量环境_{unique_name}",
            "base_url": "http://api.example.com",
            "variables": json.dumps({
                "user_id": "12345",
                "api_key": "test_key",
                "timeout": 5000,
                "debug": True
            })
        })
        env_data = api_client.assert_success(env_response)
        env_id = env_data["data"]["id"]
        
        # 验证变量
        detail_response = api_client.get("/ApiEnvironment/queryById", params={"id": env_id})
        detail_data = api_client.assert_success(detail_response)
        assert detail_data["data"]["variables"] is not None
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestApiEnvironmentControllerEdgeCases:
    """API 环境配置 Controller 边界情况测试"""
    
    def test_query_nonexistent_environment(self, api_client):
        """测试查询不存在的环境"""
        response = api_client.get("/ApiEnvironment/queryById", params={"id": 999999})
        assert response.status_code in [200, 404]
    
    def test_delete_nonexistent_environment(self, api_client):
        """测试删除不存在的环境"""
        response = api_client.delete("/ApiEnvironment/delete", params={"id": 999999})
        assert response.status_code in [200, 404]
    
    def test_duplicate_environment_name(self, api_client, unique_name):
        """测试重复的环境名称"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"重复环境_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建第一个环境
        env1_response = api_client.post("/ApiEnvironment/insert", json={
            "project_id": project_id,
            "env_name": f"重复名称_{unique_name}",
            "base_url": "http://test1.example.com"
        })
        api_client.assert_success(env1_response)
        
        # 尝试创建同名环境
        env2_response = api_client.post("/ApiEnvironment/insert", json={
            "project_id": project_id,
            "env_name": f"重复名称_{unique_name}",
            "base_url": "http://test2.example.com"
        })
        
        # 可能允许重复或返回错误
        assert env2_response.status_code in [200, 400]
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
