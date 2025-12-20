"""
环境配置和关键字管理 E2E 测试
测试环境变量、关键字等辅助功能的完整流程
"""
import pytest
import json


class TestEnvironmentManagementE2E:
    """环境配置管理 E2E 测试"""
    
    def test_environment_full_lifecycle(self, api_client, unique_name):
        """测试环境配置完整生命周期"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"环境测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 1. 创建开发环境
        dev_env_data = {
            "project_id": project_id,
            "env_name": f"开发环境_{unique_name}",
            "base_url": "http://dev.example.com",
            "env_desc": "开发环境配置",
            "variables": json.dumps({
                "api_key": "dev_key_123",
                "timeout": 5000,
                "debug": True
            }),
            "headers": json.dumps([
                {"key": "X-Environment", "value": "development"}
            ])
        }
        dev_env_response = api_client.post("/ApiEnvironment/insert", json=dev_env_data)
        dev_env_result = api_client.assert_success(dev_env_response)
        dev_env_id = dev_env_result["data"]["id"]
        print(f"✓ 创建开发环境成功: ID={dev_env_id}")
        
        # 2. 创建测试环境
        test_env_response = api_client.post("/ApiEnvironment/insert", json={
            "project_id": project_id,
            "env_name": f"测试环境_{unique_name}",
            "base_url": "http://test.example.com",
            "variables": json.dumps({
                "api_key": "test_key_456",
                "timeout": 10000,
                "debug": False
            })
        })
        test_env_result = api_client.assert_success(test_env_response)
        test_env_id = test_env_result["data"]["id"]
        print(f"✓ 创建测试环境成功: ID={test_env_id}")
        
        # 3. 创建生产环境
        prod_env_response = api_client.post("/ApiEnvironment/insert", json={
            "project_id": project_id,
            "env_name": f"生产环境_{unique_name}",
            "base_url": "https://api.example.com",
            "variables": json.dumps({
                "api_key": "prod_key_789",
                "timeout": 30000,
                "debug": False
            })
        })
        prod_env_result = api_client.assert_success(prod_env_response)
        prod_env_id = prod_env_result["data"]["id"]
        print(f"✓ 创建生产环境成功: ID={prod_env_id}")
        
        # 4. 查询环境列表
        list_response = api_client.post("/ApiEnvironment/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project_id
        })
        list_data = api_client.assert_success(list_response)
        assert len(list_data["data"]) == 3
        print(f"✓ 环境列表查询成功，共 3 个环境")
        
        # 5. 更新环境配置
        update_response = api_client.put("/ApiEnvironment/update", json={
            "id": dev_env_id,
            "env_name": f"开发环境_V2_{unique_name}",
            "base_url": "http://dev-v2.example.com",
            "variables": json.dumps({
                "api_key": "dev_key_new",
                "timeout": 8000,
                "debug": True,
                "new_var": "added"
            })
        })
        api_client.assert_success(update_response)
        print(f"✓ 环境配置更新成功")
        
        # 6. 验证更新
        detail_response = api_client.get("/ApiEnvironment/queryById", params={"id": dev_env_id})
        detail_data = api_client.assert_success(detail_response)
        assert detail_data["data"]["env_name"] == f"开发环境_V2_{unique_name}"
        assert detail_data["data"]["base_url"] == "http://dev-v2.example.com"
        print(f"✓ 更新验证成功")
        
        # 7. 删除环境
        delete_response = api_client.delete("/ApiEnvironment/delete", params={"id": test_env_id})
        api_client.assert_success(delete_response)
        print(f"✓ 环境删除成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_environment_variable_usage(self, api_client, unique_name):
        """测试环境变量的使用"""
        # 创建项目和环境
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"变量使用_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        env_response = api_client.post("/ApiEnvironment/insert", json={
            "project_id": project_id,
            "env_name": f"变量环境_{unique_name}",
            "base_url": "http://api.example.com",
            "variables": json.dumps({
                "user_id": "12345",
                "token": "abc123xyz",
                "api_version": "v1"
            })
        })
        env_data = api_client.assert_success(env_response)
        env_id = env_data["data"]["id"]
        
        # 创建使用环境变量的接口
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"变量接口_{unique_name}",
            "request_url": "/{{api_version}}/user/{{user_id}}",
            "request_method": "GET",
            "request_headers": json.dumps([
                {"key": "Authorization", "value": "Bearer {{token}}"}
            ])
        })
        api_data = api_client.assert_success(api_response)
        api_id = api_data["data"]["id"]
        
        print(f"✓ 创建使用环境变量的接口成功")
        
        # 创建使用环境变量的用例
        case_response = api_client.post("/ApiInfoCase/insert", json={
            "project_id": project_id,
            "api_info_id": api_id,
            "case_name": f"变量用例_{unique_name}",
            "request_url": "/{{api_version}}/user/{{user_id}}",
            "request_method": "GET"
        })
        case_data = api_client.assert_success(case_response)
        print(f"✓ 创建使用环境变量的用例成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_environment_switching(self, api_client, unique_name):
        """测试环境切换"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"环境切换_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建多个环境
        environments = []
        for env_type in ["dev", "test", "prod"]:
            env_response = api_client.post("/ApiEnvironment/insert", json={
                "project_id": project_id,
                "env_name": f"{env_type}环境_{unique_name}",
                "base_url": f"http://{env_type}.example.com",
                "is_default": 1 if env_type == "dev" else 0
            })
            env_data = api_client.assert_success(env_response)
            environments.append(env_data["data"]["id"])
        
        print(f"✓ 创建了 {len(environments)} 个环境")
        
        # 切换默认环境
        switch_response = api_client.put("/ApiEnvironment/update", json={
            "id": environments[1],  # 切换到测试环境
            "is_default": 1
        })
        api_client.assert_success(switch_response)
        print(f"✓ 环境切换成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestKeywordManagementE2E:
    """关键字管理 E2E 测试"""
    
    def test_keyword_full_lifecycle(self, api_client, unique_name):
        """测试关键字完整生命周期"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"关键字测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 1. 创建关键字
        keyword_data = {
            "project_id": project_id,
            "keyword_name": f"登录关键字_{unique_name}",
            "keyword_desc": "用户登录的关键字",
            "keyword_type": "request",
            "keyword_content": json.dumps({
                "url": "/api/login",
                "method": "POST",
                "body": {
                    "username": "{{username}}",
                    "password": "{{password}}"
                }
            })
        }
        create_response = api_client.post("/ApiKeyWord/insert", json=keyword_data)
        create_result = api_client.assert_success(create_response)
        keyword_id = create_result["data"]["id"]
        print(f"✓ 创建关键字成功: ID={keyword_id}")
        
        # 2. 查询关键字详情
        detail_response = api_client.get("/ApiKeyWord/queryById", params={"id": keyword_id})
        detail_data = api_client.assert_success(detail_response)
        assert detail_data["data"]["keyword_name"] == f"登录关键字_{unique_name}"
        print(f"✓ 关键字详情查询成功")
        
        # 3. 更新关键字
        update_response = api_client.put("/ApiKeyWord/update", json={
            "id": keyword_id,
            "keyword_name": f"登录关键字_V2_{unique_name}",
            "keyword_desc": "更新后的登录关键字",
            "keyword_content": json.dumps({
                "url": "/api/v2/login",
                "method": "POST",
                "body": {
                    "username": "{{username}}",
                    "password": "{{password}}",
                    "remember_me": True
                }
            })
        })
        api_client.assert_success(update_response)
        print(f"✓ 关键字更新成功")
        
        # 4. 创建更多关键字
        for i in range(3):
            api_client.post("/ApiKeyWord/insert", json={
                "project_id": project_id,
                "keyword_name": f"关键字{i}_{unique_name}",
                "keyword_type": "assertion",
                "keyword_content": json.dumps({
                    "type": "status_code",
                    "expected": 200
                })
            })
        
        # 5. 查询关键字列表
        list_response = api_client.post("/ApiKeyWord/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project_id
        })
        list_data = api_client.assert_success(list_response)
        assert len(list_data["data"]) >= 4
        print(f"✓ 关键字列表查询成功，共 {len(list_data['data'])} 个")
        
        # 6. 删除关键字
        delete_response = api_client.delete("/ApiKeyWord/delete", params={"id": keyword_id})
        api_client.assert_success(delete_response)
        print(f"✓ 关键字删除成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_keyword_types(self, api_client, unique_name):
        """测试不同类型的关键字"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"关键字类型_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建不同类型的关键字
        keyword_types = [
            {
                "type": "request",
                "name": "请求关键字",
                "content": {"url": "/api/test", "method": "GET"}
            },
            {
                "type": "assertion",
                "name": "断言关键字",
                "content": {"type": "json_path", "path": "$.code", "expected": 200}
            },
            {
                "type": "setup",
                "name": "前置关键字",
                "content": {"action": "setup_database"}
            },
            {
                "type": "teardown",
                "name": "清理关键字",
                "content": {"action": "cleanup_data"}
            }
        ]
        
        keyword_ids = []
        for kw_type in keyword_types:
            response = api_client.post("/ApiKeyWord/insert", json={
                "project_id": project_id,
                "keyword_name": f"{kw_type['name']}_{unique_name}",
                "keyword_type": kw_type["type"],
                "keyword_content": json.dumps(kw_type["content"])
            })
            data = api_client.assert_success(response)
            keyword_ids.append(data["data"]["id"])
        
        print(f"✓ 创建了 {len(keyword_types)} 种类型的关键字")
        
        # 按类型查询
        for kw_type in ["request", "assertion", "setup", "teardown"]:
            type_response = api_client.post("/ApiKeyWord/queryByPage", json={
                "page": 1,
                "pageSize": 10,
                "project_id": project_id,
                "keyword_type": kw_type
            })
            type_data = api_client.assert_success(type_response)
            print(f"✓ 查询 {kw_type} 类型关键字成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_keyword_reusability(self, api_client, unique_name):
        """测试关键字的复用性"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"关键字复用_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建可复用的关键字
        keyword_response = api_client.post("/ApiKeyWord/insert", json={
            "project_id": project_id,
            "keyword_name": f"通用验证_{unique_name}",
            "keyword_type": "assertion",
            "keyword_desc": "通用的响应验证关键字",
            "keyword_content": json.dumps({
                "assertions": [
                    {"type": "status_code", "expected": 200},
                    {"type": "json_path", "path": "$.code", "expected": 200},
                    {"type": "response_time", "max": 1000}
                ]
            })
        })
        keyword_data = api_client.assert_success(keyword_response)
        keyword_id = keyword_data["data"]["id"]
        
        # 在多个用例中使用该关键字
        for i in range(3):
            case_response = api_client.post("/ApiInfoCase/insert", json={
                "project_id": project_id,
                "case_name": f"使用关键字的用例{i}_{unique_name}",
                "request_url": f"/api/test/{i}",
                "request_method": "GET",
                "keywords": json.dumps([keyword_id])
            })
            api_client.assert_success(case_response)
        
        print(f"✓ 关键字在 3 个用例中复用成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestDatabaseConfigurationE2E:
    """数据库配置 E2E 测试"""
    
    def test_database_config_lifecycle(self, api_client, unique_name):
        """测试数据库配置生命周期"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"数据库测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建数据库配置
        db_config_data = {
            "project_id": project_id,
            "db_name": f"测试数据库_{unique_name}",
            "db_type": "mysql",
            "host": "localhost",
            "port": 3306,
            "username": "testuser",
            "password": "testpass",
            "database": "testdb"
        }
        create_response = api_client.post("/ApiDbBase/insert", json=db_config_data)
        create_result = api_client.assert_success(create_response)
        db_id = create_result["data"]["id"]
        print(f"✓ 创建数据库配置成功: ID={db_id}")
        
        # 查询配置详情
        detail_response = api_client.get("/ApiDbBase/queryById", params={"id": db_id})
        detail_data = api_client.assert_success(detail_response)
        assert detail_data["data"]["db_name"] == f"测试数据库_{unique_name}"
        print(f"✓ 数据库配置查询成功")
        
        # 更新配置
        update_response = api_client.put("/ApiDbBase/update", json={
            "id": db_id,
            "db_name": f"测试数据库_V2_{unique_name}",
            "port": 3307
        })
        api_client.assert_success(update_response)
        print(f"✓ 数据库配置更新成功")
        
        # 删除配置
        delete_response = api_client.delete("/ApiDbBase/delete", params={"id": db_id})
        api_client.assert_success(delete_response)
        print(f"✓ 数据库配置删除成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
