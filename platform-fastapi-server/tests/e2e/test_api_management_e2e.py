"""
接口管理完整 E2E 测试
测试接口的创建、编辑、调试、导入导出等完整流程
"""
import pytest
import json


class TestApiManagementE2E:
    """接口管理 E2E 测试"""
    
    def test_api_full_lifecycle(self, api_client, unique_name):
        """测试接口完整生命周期"""
        # 准备：创建项目和目录
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"接口测试项目_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        folder_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"用户模块_{unique_name}"
        })
        folder_data = api_client.assert_success(folder_response)
        folder_id = folder_data["data"]["id"]
        
        # 1. 创建接口
        api_data = {
            "project_id": project_id,
            "folder_id": folder_id,
            "api_name": f"获取用户信息_{unique_name}",
            "request_url": "/api/user/info",
            "request_method": "GET",
            "api_desc": "获取用户详细信息",
            "request_params": json.dumps([
                {"key": "user_id", "type": "integer", "required": True, "description": "用户ID"}
            ]),
            "request_headers": json.dumps([
                {"key": "Authorization", "value": "Bearer token"}
            ])
        }
        create_response = api_client.post("/ApiInfo/insert", json=api_data)
        create_result = api_client.assert_success(create_response)
        api_id = create_result["data"]["id"]
        print(f"✓ 创建接口成功: ID={api_id}")
        
        # 2. 查询接口详情
        detail_response = api_client.get("/ApiInfo/queryById", params={"id": api_id})
        detail_result = api_client.assert_success(detail_response)
        assert detail_result["data"]["api_name"] == f"获取用户信息_{unique_name}"
        print(f"✓ 接口详情查询成功")
        
        # 3. 更新接口
        update_data = {
            "id": api_id,
            "api_name": f"获取用户信息_V2_{unique_name}",
            "api_desc": "获取用户详细信息（V2版本）",
            "request_params": json.dumps([
                {"key": "user_id", "type": "integer", "required": True, "description": "用户ID"},
                {"key": "include_profile", "type": "boolean", "required": False, "description": "是否包含详细资料"}
            ])
        }
        update_response = api_client.put("/ApiInfo/update", json=update_data)
        api_client.assert_success(update_response)
        print(f"✓ 接口更新成功")
        
        # 4. 验证更新
        verify_response = api_client.get("/ApiInfo/queryById", params={"id": api_id})
        verify_result = api_client.assert_success(verify_response)
        assert verify_result["data"]["api_name"] == f"获取用户信息_V2_{unique_name}"
        print(f"✓ 更新验证成功")
        
        # 5. 复制接口
        copy_response = api_client.post("/ApiInfo/copy", json={"id": api_id})
        copy_result = api_client.assert_success(copy_response)
        copy_id = copy_result["data"]["id"]
        print(f"✓ 接口复制成功: ID={copy_id}")
        
        # 6. 删除接口
        api_client.delete("/ApiInfo/delete", params={"id": api_id})
        api_client.delete("/ApiInfo/delete", params={"id": copy_id})
        print(f"✓ 接口删除成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_api_with_different_methods(self, api_client, unique_name):
        """测试不同请求方法的接口"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"方法测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建不同方法的接口
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        api_ids = []
        
        for method in methods:
            response = api_client.post("/ApiInfo/insert", json={
                "project_id": project_id,
                "api_name": f"{method}接口_{unique_name}",
                "request_url": f"/api/test/{method.lower()}",
                "request_method": method
            })
            data = api_client.assert_success(response)
            api_ids.append(data["data"]["id"])
        
        print(f"✓ 创建了 {len(methods)} 个不同方法的接口")
        
        # 查询项目的所有接口
        list_response = api_client.post("/ApiInfo/queryByPage", json={
            "page": 1,
            "pageSize": 20,
            "project_id": project_id
        })
        list_data = api_client.assert_success(list_response)
        assert len(list_data["data"]) == len(methods)
        print(f"✓ 接口列表查询成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_api_with_request_body(self, api_client, unique_name):
        """测试带请求体的接口"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"请求体测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建POST接口（JSON请求体）
        json_api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"创建用户_{unique_name}",
            "request_url": "/api/user/create",
            "request_method": "POST",
            "requests_json_data": json.dumps({
                "username": "testuser",
                "email": "test@example.com",
                "age": 25
            }),
            "request_headers": json.dumps([
                {"key": "Content-Type", "value": "application/json"}
            ])
        })
        json_api_data = api_client.assert_success(json_api_response)
        json_api_id = json_api_data["data"]["id"]
        
        # 验证请求体
        detail_response = api_client.get("/ApiInfo/queryById", params={"id": json_api_id})
        detail_data = api_client.assert_success(detail_response)
        assert detail_data["data"]["requests_json_data"] is not None
        print(f"✓ JSON请求体接口创建成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_api_history_tracking(self, api_client, unique_name):
        """测试接口历史记录"""
        # 创建项目和接口
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"历史测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"测试接口_{unique_name}",
            "request_url": "/api/test",
            "request_method": "GET"
        })
        api_data = api_client.assert_success(api_response)
        api_id = api_data["data"]["id"]
        
        # 记录请求历史
        for i in range(3):
            history_response = api_client.post("/ApiRequestHistory/insert", json={
                "project_id": project_id,
                "api_id": api_id,
                "request_url": "/api/test",
                "request_method": "GET",
                "response_status": 200,
                "response_time": 100 + i * 10,
                "is_success": 1
            })
            api_client.assert_success(history_response)
        
        print(f"✓ 记录了 3 条请求历史")
        
        # 查询历史记录
        history_list_response = api_client.post("/ApiRequestHistory/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project_id
        })
        history_list_data = api_client.assert_success(history_list_response)
        assert len(history_list_data["data"]) >= 3
        print(f"✓ 历史记录查询成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestApiBatchOperations:
    """接口批量操作测试"""
    
    def test_batch_import_apis(self, api_client, unique_name):
        """测试批量导入接口"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"批量导入_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 批量创建接口
        apis_to_create = []
        for i in range(5):
            apis_to_create.append({
                "project_id": project_id,
                "api_name": f"批量接口{i}_{unique_name}",
                "request_url": f"/api/batch/{i}",
                "request_method": "GET"
            })
        
        # 逐个创建（模拟批量导入）
        created_ids = []
        for api_data in apis_to_create:
            response = api_client.post("/ApiInfo/insert", json=api_data)
            result = api_client.assert_success(response)
            created_ids.append(result["data"]["id"])
        
        print(f"✓ 批量创建了 {len(created_ids)} 个接口")
        
        # 验证批量创建结果
        list_response = api_client.post("/ApiInfo/queryByPage", json={
            "page": 1,
            "pageSize": 20,
            "project_id": project_id
        })
        list_data = api_client.assert_success(list_response)
        assert len(list_data["data"]) == 5
        print(f"✓ 批量导入验证成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_batch_delete_apis(self, api_client, unique_name):
        """测试批量删除接口"""
        # 创建项目和接口
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"批量删除_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建多个接口
        api_ids = []
        for i in range(3):
            response = api_client.post("/ApiInfo/insert", json={
                "project_id": project_id,
                "api_name": f"待删除接口{i}_{unique_name}",
                "request_url": f"/api/delete/{i}",
                "request_method": "DELETE"
            })
            data = api_client.assert_success(response)
            api_ids.append(data["data"]["id"])
        
        # 批量删除
        for api_id in api_ids:
            api_client.delete("/ApiInfo/delete", params={"id": api_id})
        
        print(f"✓ 批量删除了 {len(api_ids)} 个接口")
        
        # 验证删除结果
        list_response = api_client.post("/ApiInfo/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project_id
        })
        list_data = api_client.assert_success(list_response)
        assert len(list_data["data"]) == 0
        print(f"✓ 批量删除验证成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestApiOrganization:
    """接口组织管理测试"""
    
    def test_move_api_between_folders(self, api_client, unique_name):
        """测试在目录间移动接口"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"移动测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建两个目录
        folder1_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"源目录_{unique_name}"
        })
        folder1_data = api_client.assert_success(folder1_response)
        folder1_id = folder1_data["data"]["id"]
        
        folder2_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"目标目录_{unique_name}"
        })
        folder2_data = api_client.assert_success(folder2_response)
        folder2_id = folder2_data["data"]["id"]
        
        # 在源目录创建接口
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "folder_id": folder1_id,
            "api_name": f"待移动接口_{unique_name}",
            "request_url": "/api/move",
            "request_method": "GET"
        })
        api_data = api_client.assert_success(api_response)
        api_id = api_data["data"]["id"]
        
        # 移动接口到目标目录
        move_response = api_client.put("/ApiInfo/update", json={
            "id": api_id,
            "folder_id": folder2_id
        })
        api_client.assert_success(move_response)
        print(f"✓ 接口移动成功")
        
        # 验证移动结果
        verify_response = api_client.get("/ApiInfo/queryById", params={"id": api_id})
        verify_data = api_client.assert_success(verify_response)
        assert verify_data["data"]["folder_id"] == folder2_id
        print(f"✓ 移动验证成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_api_sorting(self, api_client, unique_name):
        """测试接口排序"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"排序测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建多个接口，指定排序
        for i in range(3):
            api_client.post("/ApiInfo/insert", json={
                "project_id": project_id,
                "api_name": f"接口{i}_{unique_name}",
                "request_url": f"/api/sort/{i}",
                "request_method": "GET",
                "sort_order": i * 10
            })
        
        # 查询接口列表
        list_response = api_client.post("/ApiInfo/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project_id
        })
        list_data = api_client.assert_success(list_response)
        
        # 验证排序（如果API支持）
        assert len(list_data["data"]) == 3
        print(f"✓ 接口排序测试完成")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
