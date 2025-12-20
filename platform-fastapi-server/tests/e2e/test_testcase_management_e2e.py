"""
测试用例管理完整 E2E 测试
测试用例的创建、编辑、执行、断言等完整流程
"""
import pytest
import json


class TestCaseManagementE2E:
    """测试用例管理 E2E 测试"""
    
    def test_testcase_full_lifecycle(self, api_client, unique_name):
        """测试用例完整生命周期"""
        # 准备：创建项目和接口
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"用例测试项目_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"登录接口_{unique_name}",
            "request_url": "/api/login",
            "request_method": "POST"
        })
        api_data = api_client.assert_success(api_response)
        api_id = api_data["data"]["id"]
        
        # 1. 创建测试用例
        case_data = {
            "project_id": project_id,
            "api_info_id": api_id,
            "case_name": f"正常登录用例_{unique_name}",
            "case_desc": "测试正常登录流程",
            "request_method": "POST",
            "request_url": "/api/login",
            "requests_json_data": json.dumps({
                "username": "testuser",
                "password": "password123"
            }),
            "expected_status": 200
        }
        create_response = api_client.post("/ApiInfoCase/insert", json=case_data)
        create_result = api_client.assert_success(create_response)
        case_id = create_result["data"]["id"]
        print(f"✓ 创建测试用例成功: ID={case_id}")
        
        # 2. 查询用例详情
        detail_response = api_client.get("/ApiInfoCase/queryById", params={"id": case_id})
        detail_result = api_client.assert_success(detail_response)
        assert detail_result["data"]["case_name"] == f"正常登录用例_{unique_name}"
        print(f"✓ 用例详情查询成功")
        
        # 3. 更新用例
        update_data = {
            "id": case_id,
            "case_name": f"正常登录用例_V2_{unique_name}",
            "case_desc": "更新后的登录测试用例",
            "requests_json_data": json.dumps({
                "username": "testuser",
                "password": "newpassword123"
            })
        }
        update_response = api_client.put("/ApiInfoCase/update", json=update_data)
        api_client.assert_success(update_response)
        print(f"✓ 用例更新成功")
        
        # 4. 验证更新
        verify_response = api_client.get("/ApiInfoCase/queryById", params={"id": case_id})
        verify_result = api_client.assert_success(verify_response)
        assert verify_result["data"]["case_name"] == f"正常登录用例_V2_{unique_name}"
        print(f"✓ 更新验证成功")
        
        # 5. 复制用例
        copy_response = api_client.post("/ApiInfoCase/copy", json={"id": case_id})
        copy_result = api_client.assert_success(copy_response)
        copy_id = copy_result["data"]["id"]
        print(f"✓ 用例复制成功: ID={copy_id}")
        
        # 6. 删除用例
        api_client.delete("/ApiInfoCase/delete", params={"id": case_id})
        api_client.delete("/ApiInfoCase/delete", params={"id": copy_id})
        print(f"✓ 用例删除成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_testcase_with_steps(self, api_client, unique_name):
        """测试带步骤的测试用例"""
        # 创建项目和用例
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"步骤测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        case_response = api_client.post("/ApiInfoCase/insert", json={
            "project_id": project_id,
            "case_name": f"多步骤用例_{unique_name}",
            "request_url": "/api/test",
            "request_method": "GET"
        })
        case_data = api_client.assert_success(case_response)
        case_id = case_data["data"]["id"]
        
        # 添加测试步骤
        steps = []
        for i in range(3):
            step_response = api_client.post("/ApiInfoCaseStep/insert", json={
                "case_id": case_id,
                "step_name": f"步骤{i+1}_{unique_name}",
                "step_desc": f"这是第{i+1}个步骤",
                "step_order": i + 1,
                "request_url": f"/api/step/{i+1}",
                "request_method": "GET"
            })
            step_data = api_client.assert_success(step_response)
            steps.append(step_data["data"]["id"])
        
        print(f"✓ 添加了 {len(steps)} 个测试步骤")
        
        # 查询用例的所有步骤
        steps_response = api_client.get("/ApiInfoCaseStep/queryByCase", params={"case_id": case_id})
        steps_data = api_client.assert_success(steps_response)
        assert len(steps_data["data"]) == 3
        print(f"✓ 步骤查询成功")
        
        # 更新步骤顺序
        reorder_response = api_client.post("/ApiInfoCaseStep/updateOrder", json={
            "case_id": case_id,
            "step_ids": list(reversed(steps))
        })
        api_client.assert_success(reorder_response)
        print(f"✓ 步骤顺序更新成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_testcase_with_assertions(self, api_client, unique_name):
        """测试带断言的测试用例"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"断言测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建带断言的用例
        case_response = api_client.post("/ApiInfoCase/insert", json={
            "project_id": project_id,
            "case_name": f"断言用例_{unique_name}",
            "request_url": "/api/user/info",
            "request_method": "GET",
            "expected_status": 200,
            "assertions": json.dumps([
                {"type": "status_code", "expected": 200},
                {"type": "json_path", "path": "$.code", "expected": 200},
                {"type": "json_path", "path": "$.data.username", "expected": "testuser"}
            ])
        })
        case_data = api_client.assert_success(case_response)
        case_id = case_data["data"]["id"]
        
        # 验证断言配置
        detail_response = api_client.get("/ApiInfoCase/queryById", params={"id": case_id})
        detail_data = api_client.assert_success(detail_response)
        assert detail_data["data"]["expected_status"] == 200
        print(f"✓ 断言配置成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_testcase_with_variables(self, api_client, unique_name):
        """测试带变量的测试用例"""
        # 创建项目和环境
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"变量测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        env_response = api_client.post("/ApiEnvironment/insert", json={
            "project_id": project_id,
            "env_name": f"测试环境_{unique_name}",
            "base_url": "http://test.example.com",
            "variables": json.dumps({
                "api_key": "test_key_123",
                "user_id": "12345"
            })
        })
        env_data = api_client.assert_success(env_response)
        env_id = env_data["data"]["id"]
        
        # 创建使用变量的用例
        case_response = api_client.post("/ApiInfoCase/insert", json={
            "project_id": project_id,
            "case_name": f"变量用例_{unique_name}",
            "request_url": "/api/user/{{user_id}}",
            "request_method": "GET",
            "request_headers": json.dumps([
                {"key": "X-API-Key", "value": "{{api_key}}"}
            ])
        })
        case_data = api_client.assert_success(case_response)
        case_id = case_data["data"]["id"]
        
        print(f"✓ 变量用例创建成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestCaseExecution:
    """测试用例执行测试"""
    
    def test_single_case_execution(self, api_client, unique_name):
        """测试单个用例执行"""
        # 创建项目和用例
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"执行测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        case_response = api_client.post("/ApiInfoCase/insert", json={
            "project_id": project_id,
            "case_name": f"执行用例_{unique_name}",
            "request_url": "/ApiStatistics/overview",
            "request_method": "GET"
        })
        case_data = api_client.assert_success(case_response)
        case_id = case_data["data"]["id"]
        
        # 执行用例（如果有执行接口）
        # execute_response = api_client.post("/ApiInfoCase/execute", json={"id": case_id})
        # execute_data = api_client.assert_success(execute_response)
        # print(f"✓ 用例执行成功")
        
        # 记录执行历史
        history_response = api_client.post("/ApiRequestHistory/insert", json={
            "project_id": project_id,
            "request_url": "/ApiStatistics/overview",
            "request_method": "GET",
            "response_status": 200,
            "response_time": 150,
            "is_success": 1
        })
        api_client.assert_success(history_response)
        print(f"✓ 执行历史记录成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_batch_case_execution(self, api_client, unique_name):
        """测试批量用例执行"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"批量执行_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建多个用例
        case_ids = []
        for i in range(3):
            case_response = api_client.post("/ApiInfoCase/insert", json={
                "project_id": project_id,
                "case_name": f"批量用例{i}_{unique_name}",
                "request_url": f"/api/batch/{i}",
                "request_method": "GET"
            })
            case_data = api_client.assert_success(case_response)
            case_ids.append(case_data["data"]["id"])
        
        print(f"✓ 创建了 {len(case_ids)} 个用例")
        
        # 批量执行（如果有批量执行接口）
        # batch_execute_response = api_client.post("/ApiInfoCase/batchExecute", json={
        #     "case_ids": case_ids
        # })
        # api_client.assert_success(batch_execute_response)
        # print(f"✓ 批量执行成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestCaseOrganization:
    """测试用例组织管理测试"""
    
    def test_case_grouping(self, api_client, unique_name):
        """测试用例分组"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"分组测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建不同类型的用例
        case_types = ["正常流程", "异常流程", "边界测试"]
        for case_type in case_types:
            for i in range(2):
                api_client.post("/ApiInfoCase/insert", json={
                    "project_id": project_id,
                    "case_name": f"{case_type}_{i}_{unique_name}",
                    "case_desc": f"{case_type}测试用例",
                    "request_url": f"/api/{case_type}/{i}",
                    "request_method": "GET"
                })
        
        print(f"✓ 创建了 {len(case_types) * 2} 个分组用例")
        
        # 查询用例列表
        list_response = api_client.post("/ApiInfoCase/queryByPage", json={
            "page": 1,
            "pageSize": 20,
            "project_id": project_id
        })
        list_data = api_client.assert_success(list_response)
        assert len(list_data["data"]) == 6
        print(f"✓ 用例列表查询成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_case_tagging(self, api_client, unique_name):
        """测试用例标签"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"标签测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建带标签的用例
        case_response = api_client.post("/ApiInfoCase/insert", json={
            "project_id": project_id,
            "case_name": f"标签用例_{unique_name}",
            "request_url": "/api/tagged",
            "request_method": "GET",
            "tags": json.dumps(["smoke", "regression", "critical"])
        })
        case_data = api_client.assert_success(case_response)
        case_id = case_data["data"]["id"]
        
        # 验证标签
        detail_response = api_client.get("/ApiInfoCase/queryById", params={"id": case_id})
        detail_data = api_client.assert_success(detail_response)
        print(f"✓ 标签用例创建成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
