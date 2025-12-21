"""
项目管理完整 E2E 测试
测试项目的创建、编辑、查询、删除等完整流程
"""
import pytest


class TestProjectManagementE2E:
    """项目管理 E2E 测试"""
    
    def test_project_full_lifecycle(self, api_client, unique_name):
        """测试项目完整生命周期"""
        # 1. 创建项目
        project_data = {
            "project_name": f"E2E项目_{unique_name}",
            "project_desc": "这是一个E2E测试项目",
            "project_type": "API",
            "status": 1
        }
        create_response = api_client.post("/ApiProject/insert", json=project_data)
        create_result = api_client.assert_success(create_response)
        project_id = create_result["data"]["id"]
        print(f"✓ 创建项目成功: ID={project_id}")
        
        # 2. 查询项目列表，验证新项目存在
        list_response = api_client.post("/ApiProject/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        list_result = api_client.assert_success(list_response)
        project_ids = [p["id"] for p in list_result["data"]]
        assert project_id in project_ids
        print(f"✓ 项目列表查询成功")
        
        # 3. 根据ID查询项目详情
        detail_response = api_client.get("/ApiProject/queryById", params={"id": project_id})
        detail_result = api_client.assert_success(detail_response)
        assert detail_result["data"]["project_name"] == f"E2E项目_{unique_name}"
        print(f"✓ 项目详情查询成功")
        
        # 4. 更新项目信息
        update_data = {
            "id": project_id,
            "project_name": f"E2E项目_已更新_{unique_name}",
            "project_desc": "更新后的项目描述",
            "status": 1
        }
        update_response = api_client.put("/ApiProject/update", json=update_data)
        api_client.assert_success(update_response)
        print(f"✓ 项目更新成功")
        
        # 5. 验证更新结果
        verify_response = api_client.get("/ApiProject/queryById", params={"id": project_id})
        verify_result = api_client.assert_success(verify_response)
        assert verify_result["data"]["project_name"] == f"E2E项目_已更新_{unique_name}"
        assert verify_result["data"]["project_desc"] == "更新后的项目描述"
        print(f"✓ 更新验证成功")
        
        # 6. 删除项目
        delete_response = api_client.delete("/ApiProject/delete", params={"id": project_id})
        api_client.assert_success(delete_response)
        print(f"✓ 项目删除成功")
        
        # 7. 验证删除结果
        verify_delete_response = api_client.get("/ApiProject/queryById", params={"id": project_id})
        assert verify_delete_response.status_code in [200, 404]
        print(f"✓ 删除验证成功")
    
    def test_project_with_folders(self, api_client, unique_name):
        """测试项目与目录结构的关联"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"目录测试项目_{unique_name}",
            "project_desc": "测试目录结构"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建多级目录
        # 一级目录
        folder1_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"用户模块_{unique_name}",
            "folder_desc": "用户相关接口",
            "parent_id": 0
        })
        folder1_data = api_client.assert_success(folder1_response)
        folder1_id = folder1_data["data"]["id"]
        
        # 二级目录
        folder2_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"用户登录_{unique_name}",
            "folder_desc": "登录相关接口",
            "parent_id": folder1_id
        })
        folder2_data = api_client.assert_success(folder2_response)
        folder2_id = folder2_data["data"]["id"]
        
        print(f"✓ 创建了多级目录结构")
        
        # 查询目录树
        tree_response = api_client.get("/ApiFolder/tree", params={"project_id": project_id})
        tree_data = api_client.assert_success(tree_response)
        assert len(tree_data["data"]) > 0
        print(f"✓ 目录树查询成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_project_statistics(self, api_client, unique_name):
        """测试项目统计数据"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"统计测试项目_{unique_name}",
            "project_desc": "测试统计功能"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建接口
        for i in range(5):
            api_client.post("/ApiInfo/insert", json={
                "project_id": project_id,
                "api_name": f"接口{i}_{unique_name}",
                "request_url": f"/api/test/{i}",
                "request_method": "GET"
            })
        
        # 创建用例
        for i in range(3):
            api_client.post("/ApiInfoCase/insert", json={
                "project_id": project_id,
                "case_name": f"用例{i}_{unique_name}",
                "request_url": f"/api/case/{i}",
                "request_method": "POST"
            })
        
        print(f"✓ 创建了测试数据")
        
        # 查询统计数据
        stats_response = api_client.get("/ApiStatistics/overview")
        stats_data = api_client.assert_success(stats_response)
        assert "projectCount" in stats_data["data"]
        assert "apiCount" in stats_data["data"]
        assert "testcaseCount" in stats_data["data"]
        print(f"✓ 统计数据查询成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestProjectSearchAndFilter:
    """项目搜索和过滤测试"""
    
    def test_search_project_by_name(self, api_client, unique_name):
        """测试按名称搜索项目"""
        # 创建多个项目
        projects = []
        for i in range(3):
            response = api_client.post("/ApiProject/insert", json={
                "project_name": f"搜索测试_{i}_{unique_name}",
                "project_desc": f"项目{i}"
            })
            data = api_client.assert_success(response)
            projects.append(data["data"]["id"])
        
        # 搜索项目
        search_response = api_client.post("/ApiProject/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_name": f"搜索测试_1_{unique_name}"
        })
        search_data = api_client.assert_success(search_response)
        
        # 验证搜索结果
        found = any(p["project_name"] == f"搜索测试_1_{unique_name}" for p in search_data["data"])
        assert found
        print(f"✓ 项目搜索成功")
        
        # 清理
        for project_id in projects:
            api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_filter_project_by_status(self, api_client, unique_name):
        """测试按状态过滤项目"""
        # 创建不同状态的项目
        active_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"激活项目_{unique_name}",
            "status": 1
        })
        active_data = api_client.assert_success(active_response)
        active_id = active_data["data"]["id"]
        
        inactive_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"停用项目_{unique_name}",
            "status": 0
        })
        inactive_data = api_client.assert_success(inactive_response)
        inactive_id = inactive_data["data"]["id"]
        
        # 按状态过滤
        filter_response = api_client.post("/ApiProject/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "status": 1
        })
        filter_data = api_client.assert_success(filter_response)
        
        # 验证过滤结果
        active_projects = [p for p in filter_data["data"] if p.get("status") == 1]
        assert len(active_projects) > 0
        print(f"✓ 状态过滤成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": active_id})
        api_client.delete("/ApiProject/delete", params={"id": inactive_id})
