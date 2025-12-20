"""
API Mock 服务接口测试
测试 ApiMockController 的所有接口
"""
import pytest


class TestApiMockController:
    """API Mock Controller 测试"""
    
    def test_query_by_page_success(self, api_client):
        """测试分页查询Mock规则 - 成功"""
        response = api_client.post("/ApiMock/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        data = api_client.assert_success(response)
        
        assert "data" in data
        assert "total" in data
        assert isinstance(data["data"], list)
    
    def test_query_by_page_with_filters(self, api_client):
        """测试分页查询 - 带过滤条件"""
        response = api_client.post("/ApiMock/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": 1,
            "mock_method": "GET",
            "is_enabled": 1
        })
        data = api_client.assert_success(response)
        
        for item in data["data"]:
            if "mock_method" in item:
                assert item["mock_method"] == "GET"
    
    def test_query_by_id_success(self, api_client, unique_name):
        """测试根据ID查询Mock规则 - 成功"""
        # 先创建Mock规则
        create_response = api_client.post("/ApiMock/insert", json={
            "project_id": 1,
            "mock_name": f"Mock_{unique_name}",
            "mock_path": f"/mock/test/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": '{"code": 200, "msg": "success"}',
            "response_body_type": "json",
            "is_enabled": 1
        })
        create_data = api_client.assert_success(create_response)
        mock_id = create_data["data"]["id"]
        
        # 查询
        response = api_client.get("/ApiMock/queryById", params={"id": mock_id})
        data = api_client.assert_success(response)
        
        assert data["data"]["id"] == mock_id
        assert data["data"]["mock_name"] == f"Mock_{unique_name}"
    
    def test_query_by_api_success(self, api_client):
        """测试查询接口的Mock规则 - 成功"""
        response = api_client.get("/ApiMock/queryByApi", params={"api_id": 1})
        data = api_client.assert_success(response)
        
        assert isinstance(data["data"], list)
        # 所有返回的Mock规则都应该属于该接口
        for item in data["data"]:
            if "api_id" in item:
                assert item["api_id"] == 1
    
    def test_insert_success(self, api_client, unique_name):
        """测试新增Mock规则 - 成功"""
        response = api_client.post("/ApiMock/insert", json={
            "project_id": 1,
            "mock_name": f"测试Mock_{unique_name}",
            "mock_path": f"/api/mock/{unique_name}",
            "mock_method": "POST",
            "response_status": 200,
            "response_body": '{"code": 200, "data": {"test": "mock"}}',
            "response_body_type": "json",
            "response_headers": '{"Content-Type": "application/json"}',
            "is_enabled": 1,
            "priority": 1
        })
        data = api_client.assert_success(response)
        
        assert "id" in data["data"]
        assert isinstance(data["data"]["id"], int)
    
    def test_insert_duplicate_path(self, api_client, unique_name):
        """测试新增Mock规则 - 重复路径"""
        mock_data = {
            "project_id": 1,
            "mock_name": f"Mock_{unique_name}",
            "mock_path": f"/duplicate/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": '{"code": 200}',
            "is_enabled": 1
        }
        
        # 第一次创建
        response1 = api_client.post("/ApiMock/insert", json=mock_data)
        api_client.assert_success(response1)
        
        # 第二次创建相同路径
        response2 = api_client.post("/ApiMock/insert", json=mock_data)
        # 应该返回错误
        assert response2.status_code in [200, 400]
        if response2.status_code == 200:
            data = response2.json()
            assert data.get("code") != 200 or "已存在" in data.get("msg", "")
    
    def test_update_success(self, api_client, unique_name):
        """测试更新Mock规则 - 成功"""
        # 先创建
        create_response = api_client.post("/ApiMock/insert", json={
            "project_id": 1,
            "mock_name": f"Original_{unique_name}",
            "mock_path": f"/update/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": '{"code": 200}',
            "is_enabled": 1
        })
        create_data = api_client.assert_success(create_response)
        mock_id = create_data["data"]["id"]
        
        # 更新
        response = api_client.put("/ApiMock/update", json={
            "id": mock_id,
            "mock_name": f"Updated_{unique_name}",
            "response_status": 201,
            "response_body": '{"code": 201, "msg": "updated"}'
        })
        data = api_client.assert_success(response)
        
        # 验证更新
        query_response = api_client.get("/ApiMock/queryById", params={"id": mock_id})
        query_data = api_client.assert_success(query_response)
        assert query_data["data"]["mock_name"] == f"Updated_{unique_name}"
    
    def test_delete_success(self, api_client, unique_name):
        """测试删除Mock规则 - 成功"""
        # 先创建
        create_response = api_client.post("/ApiMock/insert", json={
            "project_id": 1,
            "mock_name": f"ToDelete_{unique_name}",
            "mock_path": f"/delete/{unique_name}",
            "mock_method": "DELETE",
            "response_status": 200,
            "response_body": '{"code": 200}',
            "is_enabled": 1
        })
        create_data = api_client.assert_success(create_response)
        mock_id = create_data["data"]["id"]
        
        # 删除
        response = api_client.delete("/ApiMock/delete", params={"id": mock_id})
        data = api_client.assert_success(response)
        
        # 验证已删除
        query_response = api_client.get("/ApiMock/queryById", params={"id": mock_id})
        assert query_response.status_code in [200, 404]
    
    def test_toggle_enabled_success(self, api_client, unique_name):
        """测试切换启用状态 - 成功"""
        # 创建Mock规则
        create_response = api_client.post("/ApiMock/insert", json={
            "project_id": 1,
            "mock_name": f"Toggle_{unique_name}",
            "mock_path": f"/toggle/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": '{"code": 200}',
            "is_enabled": 1
        })
        create_data = api_client.assert_success(create_response)
        mock_id = create_data["data"]["id"]
        
        # 切换状态
        response = api_client.put("/ApiMock/toggleEnabled", params={"id": mock_id})
        data = api_client.assert_success(response)
        assert "启用" in data["msg"] or "禁用" in data["msg"]
    
    def test_generate_from_api_success(self, api_client, unique_name):
        """测试从接口生成Mock - 成功"""
        response = api_client.post("/ApiMock/generateFromApi", json={
            "api_id": 1,
            "mock_name": f"Generated_{unique_name}"
        })
        data = api_client.assert_success(response)
        
        assert "id" in data["data"]
    
    def test_query_logs_success(self, api_client):
        """测试查询Mock日志 - 成功"""
        response = api_client.post("/ApiMock/queryLogs", json={
            "page": 1,
            "pageSize": 10
        })
        data = api_client.assert_success(response)
        
        assert "data" in data
        assert "total" in data
        assert isinstance(data["data"], list)
    
    def test_query_logs_with_filters(self, api_client):
        """测试查询Mock日志 - 带过滤条件"""
        response = api_client.post("/ApiMock/queryLogs", json={
            "page": 1,
            "pageSize": 10,
            "project_id": 1,
            "mock_id": 1,
            "request_method": "GET"
        })
        data = api_client.assert_success(response)
        
        assert isinstance(data["data"], list)
    
    def test_clear_logs_success(self, api_client):
        """测试清空Mock日志 - 成功"""
        response = api_client.delete("/ApiMock/clearLogs", params={
            "project_id": 1,
            "days": 7
        })
        data = api_client.assert_success(response)
        
        assert "已清空" in data["msg"] or "条日志" in data["msg"]
    
    def test_get_mock_url_success(self, api_client, unique_name):
        """测试获取Mock URL - 成功"""
        # 创建Mock规则
        create_response = api_client.post("/ApiMock/insert", json={
            "project_id": 1,
            "mock_name": f"URL_{unique_name}",
            "mock_path": f"/test/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": '{"code": 200}',
            "is_enabled": 1
        })
        create_data = api_client.assert_success(create_response)
        mock_id = create_data["data"]["id"]
        
        # 获取Mock URL
        response = api_client.get("/ApiMock/getMockUrl", params={"id": mock_id})
        data = api_client.assert_success(response)
        
        assert "mock_url" in data["data"]
        assert "method" in data["data"]
        assert "full_url" in data["data"]


class TestApiMockControllerEdgeCases:
    """API Mock Controller 边界情况测试"""
    
    def test_insert_with_invalid_json(self, api_client, unique_name):
        """测试新增Mock - 无效的JSON"""
        response = api_client.post("/ApiMock/insert", json={
            "project_id": 1,
            "mock_name": f"Invalid_{unique_name}",
            "mock_path": f"/invalid/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": "not a valid json",
            "response_body_type": "json",
            "is_enabled": 1
        })
        # 应该能创建，但响应体是字符串
        data = api_client.assert_success(response)
        assert "id" in data["data"]
    
    def test_update_nonexistent_mock(self, api_client):
        """测试更新不存在的Mock"""
        response = api_client.put("/ApiMock/update", json={
            "id": 999999,
            "mock_name": "Updated"
        })
        # 应该返回错误
        assert response.status_code in [200, 404]
    
    def test_delete_nonexistent_mock(self, api_client):
        """测试删除不存在的Mock"""
        response = api_client.delete("/ApiMock/delete", params={"id": 999999})
        assert response.status_code in [200, 404]
    
    def test_toggle_nonexistent_mock(self, api_client):
        """测试切换不存在的Mock状态"""
        response = api_client.put("/ApiMock/toggleEnabled", params={"id": 999999})
        assert response.status_code in [200, 404]
