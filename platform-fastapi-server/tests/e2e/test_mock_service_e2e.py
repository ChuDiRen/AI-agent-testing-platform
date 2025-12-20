"""
Mock 服务完整 E2E 测试
测试 Mock 规则的创建、管理、使用等完整流程
"""
import pytest
import json


class TestMockServiceE2E:
    """Mock 服务 E2E 测试"""
    
    def test_mock_full_lifecycle(self, api_client, unique_name):
        """测试 Mock 规则完整生命周期"""
        # 准备：创建项目和接口
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"Mock测试项目_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"用户接口_{unique_name}",
            "request_url": "/api/user",
            "request_method": "GET"
        })
        api_data = api_client.assert_success(api_response)
        api_id = api_data["data"]["id"]
        
        # 1. 创建 Mock 规则
        mock_data = {
            "project_id": project_id,
            "api_id": api_id,
            "mock_name": f"用户Mock_{unique_name}",
            "mock_path": f"/mock/user/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": json.dumps({
                "code": 200,
                "msg": "success",
                "data": {
                    "id": 1,
                    "username": "mockuser",
                    "email": "mock@example.com"
                }
            }),
            "response_body_type": "json",
            "response_headers": json.dumps([
                {"key": "Content-Type", "value": "application/json"}
            ]),
            "is_enabled": 1,
            "priority": 1
        }
        create_response = api_client.post("/ApiMock/insert", json=mock_data)
        create_result = api_client.assert_success(create_response)
        mock_id = create_result["data"]["id"]
        print(f"✓ 创建 Mock 规则成功: ID={mock_id}")
        
        # 2. 查询 Mock 规则详情
        detail_response = api_client.get("/ApiMock/queryById", params={"id": mock_id})
        detail_result = api_client.assert_success(detail_response)
        assert detail_result["data"]["mock_name"] == f"用户Mock_{unique_name}"
        print(f"✓ Mock 规则详情查询成功")
        
        # 3. 获取 Mock URL
        url_response = api_client.get("/ApiMock/getMockUrl", params={"id": mock_id})
        url_result = api_client.assert_success(url_response)
        assert "mock_url" in url_result["data"]
        assert "full_url" in url_result["data"]
        print(f"✓ Mock URL 获取成功: {url_result['data']['mock_url']}")
        
        # 4. 更新 Mock 规则
        update_data = {
            "id": mock_id,
            "mock_name": f"用户Mock_V2_{unique_name}",
            "response_status": 201,
            "response_body": json.dumps({
                "code": 201,
                "msg": "updated",
                "data": {
                    "id": 1,
                    "username": "updateduser"
                }
            })
        }
        update_response = api_client.put("/ApiMock/update", json=update_data)
        api_client.assert_success(update_response)
        print(f"✓ Mock 规则更新成功")
        
        # 5. 切换启用状态
        toggle_response = api_client.put("/ApiMock/toggleEnabled", params={"id": mock_id})
        toggle_result = api_client.assert_success(toggle_response)
        print(f"✓ Mock 状态切换成功: {toggle_result['msg']}")
        
        # 6. 再次切换回启用
        api_client.put("/ApiMock/toggleEnabled", params={"id": mock_id})
        print(f"✓ Mock 重新启用成功")
        
        # 7. 删除 Mock 规则
        delete_response = api_client.delete("/ApiMock/delete", params={"id": mock_id})
        api_client.assert_success(delete_response)
        print(f"✓ Mock 规则删除成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_mock_from_api(self, api_client, unique_name):
        """测试从接口生成 Mock"""
        # 创建项目和接口
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"Mock生成_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"订单接口_{unique_name}",
            "request_url": "/api/order",
            "request_method": "POST",
            "requests_json_data": json.dumps({
                "product_id": 1,
                "quantity": 2
            })
        })
        api_data = api_client.assert_success(api_response)
        api_id = api_data["data"]["id"]
        
        # 从接口生成 Mock
        generate_response = api_client.post("/ApiMock/generateFromApi", json={
            "api_id": api_id,
            "mock_name": f"自动生成Mock_{unique_name}"
        })
        generate_result = api_client.assert_success(generate_response)
        mock_id = generate_result["data"]["id"]
        print(f"✓ 从接口生成 Mock 成功: ID={mock_id}")
        
        # 验证生成的 Mock
        detail_response = api_client.get("/ApiMock/queryById", params={"id": mock_id})
        detail_result = api_client.assert_success(detail_response)
        assert detail_result["data"]["mock_method"] == "POST"
        print(f"✓ 生成的 Mock 验证成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_mock_with_different_response_types(self, api_client, unique_name):
        """测试不同响应类型的 Mock"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"响应类型_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # JSON 响应
        json_mock_response = api_client.post("/ApiMock/insert", json={
            "project_id": project_id,
            "mock_name": f"JSON_Mock_{unique_name}",
            "mock_path": f"/mock/json/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": json.dumps({"type": "json", "data": [1, 2, 3]}),
            "response_body_type": "json",
            "is_enabled": 1
        })
        json_mock_data = api_client.assert_success(json_mock_response)
        json_mock_id = json_mock_data["data"]["id"]
        
        # 文本响应
        text_mock_response = api_client.post("/ApiMock/insert", json={
            "project_id": project_id,
            "mock_name": f"Text_Mock_{unique_name}",
            "mock_path": f"/mock/text/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": "Plain text response",
            "response_body_type": "text",
            "is_enabled": 1
        })
        text_mock_data = api_client.assert_success(text_mock_response)
        text_mock_id = text_mock_data["data"]["id"]
        
        print(f"✓ 创建了不同响应类型的 Mock")
        
        # 查询 Mock 列表
        list_response = api_client.post("/ApiMock/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project_id
        })
        list_data = api_client.assert_success(list_response)
        assert len(list_data["data"]) == 2
        print(f"✓ Mock 列表查询成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_mock_priority(self, api_client, unique_name):
        """测试 Mock 优先级"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"优先级测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建相同路径但不同优先级的 Mock
        priorities = [1, 5, 10]
        mock_ids = []
        
        for priority in priorities:
            response = api_client.post("/ApiMock/insert", json={
                "project_id": project_id,
                "mock_name": f"优先级{priority}_{unique_name}",
                "mock_path": f"/mock/priority/{unique_name}",
                "mock_method": "GET",
                "response_status": 200,
                "response_body": json.dumps({"priority": priority}),
                "response_body_type": "json",
                "priority": priority,
                "is_enabled": 1
            })
            data = api_client.assert_success(response)
            mock_ids.append(data["data"]["id"])
        
        print(f"✓ 创建了 {len(priorities)} 个不同优先级的 Mock")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestMockLogging:
    """Mock 日志测试"""
    
    def test_mock_log_tracking(self, api_client, unique_name):
        """测试 Mock 日志记录"""
        # 创建项目和 Mock
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"日志测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        mock_response = api_client.post("/ApiMock/insert", json={
            "project_id": project_id,
            "mock_name": f"日志Mock_{unique_name}",
            "mock_path": f"/mock/log/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": json.dumps({"logged": True}),
            "response_body_type": "json",
            "is_enabled": 1
        })
        mock_data = api_client.assert_success(mock_response)
        mock_id = mock_data["data"]["id"]
        
        # 查询 Mock 日志
        log_response = api_client.post("/ApiMock/queryLogs", json={
            "page": 1,
            "pageSize": 10,
            "mock_id": mock_id
        })
        log_data = api_client.assert_success(log_response)
        print(f"✓ Mock 日志查询成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_mock_log_cleanup(self, api_client, unique_name):
        """测试 Mock 日志清理"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"日志清理_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 清空 Mock 日志
        clear_response = api_client.delete("/ApiMock/clearLogs", params={
            "project_id": project_id,
            "days": 7
        })
        clear_data = api_client.assert_success(clear_response)
        print(f"✓ Mock 日志清理成功: {clear_data['msg']}")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestMockAdvancedFeatures:
    """Mock 高级功能测试"""
    
    def test_mock_with_delay(self, api_client, unique_name):
        """测试带延迟的 Mock"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"延迟测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建带延迟的 Mock
        mock_response = api_client.post("/ApiMock/insert", json={
            "project_id": project_id,
            "mock_name": f"延迟Mock_{unique_name}",
            "mock_path": f"/mock/delay/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": json.dumps({"delayed": True}),
            "response_body_type": "json",
            "response_delay": 1000,  # 1秒延迟
            "is_enabled": 1
        })
        mock_data = api_client.assert_success(mock_response)
        mock_id = mock_data["data"]["id"]
        
        print(f"✓ 创建延迟 Mock 成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_mock_with_dynamic_response(self, api_client, unique_name):
        """测试动态响应 Mock"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"动态响应_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建动态响应 Mock（使用模板变量）
        mock_response = api_client.post("/ApiMock/insert", json={
            "project_id": project_id,
            "mock_name": f"动态Mock_{unique_name}",
            "mock_path": f"/mock/dynamic/{unique_name}",
            "mock_method": "GET",
            "response_status": 200,
            "response_body": json.dumps({
                "timestamp": "{{timestamp}}",
                "random_id": "{{random_uuid}}",
                "user": "{{request.query.user}}"
            }),
            "response_body_type": "json",
            "is_enabled": 1
        })
        mock_data = api_client.assert_success(mock_response)
        mock_id = mock_data["data"]["id"]
        
        print(f"✓ 创建动态响应 Mock 成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
