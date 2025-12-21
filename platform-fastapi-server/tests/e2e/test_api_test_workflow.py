"""
API 测试完整工作流 E2E 测试
测试从创建项目到执行测试的完整流程
"""
import pytest
import time


class TestApiTestWorkflow:
    """API 测试完整工作流"""
    
    def test_complete_api_test_workflow(self, api_client, unique_name):
        """
        测试完整的API测试工作流程
        1. 创建项目
        2. 创建环境
        3. 创建目录
        4. 创建接口
        5. 创建用例
        6. 创建测试计划
        7. 执行测试
        8. 查看结果
        """
        # 1. 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"E2E测试项目_{unique_name}",
            "project_desc": "E2E测试项目描述",
            "project_type": "API"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        print(f"✓ 创建项目成功: ID={project_id}")
        
        # 2. 创建目录
        folder_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"测试目录_{unique_name}",
            "folder_desc": "测试目录描述"
        })
        folder_data = api_client.assert_success(folder_response)
        folder_id = folder_data["data"]["id"]
        print(f"✓ 创建目录成功: ID={folder_id}")
        
        # 4. 创建接口
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "folder_id": folder_id,
            "api_name": f"测试接口_{unique_name}",
            "request_url": "/ApiStatistics/overview",
            "request_method": "GET",
            "api_desc": "测试接口描述"
        })
        api_data = api_client.assert_success(api_response)
        api_id = api_data["data"]["id"]
        print(f"✓ 创建接口成功: ID={api_id}")
        
        # 5. 创建用例
        case_response = api_client.post("/ApiInfoCase/insert", json={
            "project_id": project_id,
            "api_info_id": api_id,
            "case_name": f"测试用例_{unique_name}",
            "case_desc": "测试用例描述",
            "request_method": "GET",
            "request_url": "/ApiStatistics/overview"
        })
        case_data = api_client.assert_success(case_response)
        case_id = case_data["data"]["id"]
        print(f"✓ 创建用例成功: ID={case_id}")
        
        # 6. 创建测试计划
        plan_response = api_client.post("/ApiCollectionInfo/insert", json={
            "project_id": project_id,
            "collection_name": f"测试计划_{unique_name}",
            "collection_desc": "测试计划描述"
        })
        plan_data = api_client.assert_success(plan_response)
        plan_id = plan_data["data"]["id"]
        print(f"✓ 创建测试计划成功: ID={plan_id}")
        
        # 7. 添加用例到测试计划
        detail_response = api_client.post("/ApiCollectionDetail/insert", json={
            "collection_info_id": plan_id,
            "case_info_id": case_id
        })
        api_client.assert_success(detail_response)
        print(f"✓ 添加用例到测试计划成功")
        
        # 8. 查看统计数据
        stats_response = api_client.get("/ApiStatistics/overview")
        stats_data = api_client.assert_success(stats_response)
        print(f"✓ 查看统计数据成功")
        
        # 验证统计数据
        assert stats_data["data"]["projectCount"] >= 1
        assert stats_data["data"]["apiCount"] >= 1
        assert stats_data["data"]["testcaseCount"] >= 1
        
        # 清理：删除测试数据
        api_client.delete("/ApiProject/delete", params={"id": project_id})
        print(f"✓ 清理测试数据完成")
    
    def test_api_crud_workflow(self, api_client, unique_name):
        """
        测试接口CRUD完整流程
        """
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"CRUD测试_{unique_name}",
            "project_desc": "CRUD测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建接口
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"接口_{unique_name}",
            "request_url": "/test/api",
            "request_method": "POST"
        })
        api_data = api_client.assert_success(api_response)
        api_id = api_data["data"]["id"]
        
        # 查询接口
        query_response = api_client.get("/ApiInfo/queryById", params={"id": api_id})
        query_data = api_client.assert_success(query_response)
        assert query_data["data"]["api_name"] == f"接口_{unique_name}"
        
        # 更新接口
        update_response = api_client.put("/ApiInfo/update", json={
            "id": api_id,
            "api_name": f"更新接口_{unique_name}",
            "api_desc": "更新后的描述"
        })
        api_client.assert_success(update_response)
        
        # 验证更新
        verify_response = api_client.get("/ApiInfo/queryById", params={"id": api_id})
        verify_data = api_client.assert_success(verify_response)
        assert verify_data["data"]["api_name"] == f"更新接口_{unique_name}"
        
        # 删除接口
        delete_response = api_client.delete("/ApiInfo/delete", params={"id": api_id})
        api_client.assert_success(delete_response)
        
        # 清理项目
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_test_case_execution_workflow(self, api_client, unique_name):
        """
        测试用例执行流程
        """
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"执行测试_{unique_name}",
            "project_desc": "执行测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建接口
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"执行接口_{unique_name}",
            "request_url": "/ApiStatistics/overview",
            "request_method": "GET"
        })
        api_data = api_client.assert_success(api_response)
        api_id = api_data["data"]["id"]
        
        # 创建用例
        case_response = api_client.post("/ApiInfoCase/insert", json={
            "project_id": project_id,
            "api_info_id": api_id,
            "case_name": f"执行用例_{unique_name}",
            "request_method": "GET",
            "request_url": "/ApiStatistics/overview"
        })
        case_data = api_client.assert_success(case_response)
        case_id = case_data["data"]["id"]
        
        # 记录请求历史
        history_response = api_client.post("/ApiRequestHistory/insert", json={
            "project_id": project_id,
            "api_id": api_id,
            "request_url": "/ApiStatistics/overview",
            "request_method": "GET",
            "response_status": 200,
            "response_time": 100,
            "is_success": 1
        })
        api_client.assert_success(history_response)
        
        # 查看请求历史
        history_query_response = api_client.post("/ApiRequestHistory/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project_id
        })
        history_data = api_client.assert_success(history_query_response)
        assert len(history_data["data"]) >= 1
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
class TestStatisticsWorkflow:
    """统计功能工作流测试"""
    
    def test_statistics_data_flow(self, api_client, unique_name):
        """
        测试统计数据流程
        """
        # 获取初始统计
        initial_response = api_client.get("/ApiStatistics/overview")
        initial_data = api_client.assert_success(initial_response)
        initial_project_count = initial_data["data"]["projectCount"]
        
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"统计测试_{unique_name}",
            "project_desc": "统计测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 获取更新后的统计
        updated_response = api_client.get("/ApiStatistics/overview")
        updated_data = api_client.assert_success(updated_response)
        assert updated_data["data"]["projectCount"] == initial_project_count + 1
        
        # 查看执行次数统计
        exec_response = api_client.get("/ApiStatistics/executionCount")
        api_client.assert_success(exec_response)
        
        # 查看通过率
        pass_rate_response = api_client.get("/ApiStatistics/passRate", params={"days": 7})
        pass_rate_data = api_client.assert_success(pass_rate_response)
        assert "pass_rate" in pass_rate_data["data"]
        
        # 查看每日统计
        daily_response = api_client.get("/ApiStatistics/dailyStats", params={"days": 7})
        daily_data = api_client.assert_success(daily_response)
        assert "daily_stats" in daily_data["data"]
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_trend_analysis_workflow(self, api_client):
        """
        测试趋势分析流程
        """
        # 查看执行趋势
        trend_response = api_client.get("/ApiStatistics/executionTrend", params={"limit": 5})
        trend_data = api_client.assert_success(trend_response)
        assert "trend" in trend_data["data"]
        
        # 查看耗时趋势
        time_response = api_client.get("/ApiStatistics/timeTrend", params={"limit": 10})
        time_data = api_client.assert_success(time_response)
        assert "trend" in time_data["data"]
        assert "avg_time" in time_data["data"]
        
        # 查看失败TOP5
        failed_response = api_client.get("/ApiStatistics/failedTop5", params={"days": 30})
        failed_data = api_client.assert_success(failed_response)
        assert "top5" in failed_data["data"]


class TestRequestHistoryWorkflow:
    """请求历史工作流测试"""
    
    def test_request_history_lifecycle(self, api_client, unique_name):
        """
        测试请求历史生命周期
        """
        # 创建请求历史
        create_response = api_client.post("/ApiRequestHistory/insert", json={
            "project_id": 1,
            "request_url": f"/test/{unique_name}",
            "request_method": "GET",
            "response_status": 200,
            "response_time": 150,
            "is_success": 1,
            "is_favorite": 0
        })
        create_data = api_client.assert_success(create_response)
        history_id = create_data["data"]["id"]
        
        # 查询历史
        query_response = api_client.get("/ApiRequestHistory/queryById", params={"id": history_id})
        api_client.assert_success(query_response)
        
        # 收藏
        favorite_response = api_client.put("/ApiRequestHistory/toggleFavorite", params={"id": history_id})
        api_client.assert_success(favorite_response)
        
        # 查询收藏列表
        favorites_response = api_client.get("/ApiRequestHistory/queryFavorites", params={"project_id": 1})
        favorites_data = api_client.assert_success(favorites_response)
        favorite_ids = [item["id"] for item in favorites_data["data"] if "id" in item]
        assert history_id in favorite_ids
        
        # 取消收藏
        unfavorite_response = api_client.put("/ApiRequestHistory/toggleFavorite", params={"id": history_id})
        api_client.assert_success(unfavorite_response)
        
        # 删除
        delete_response = api_client.delete("/ApiRequestHistory/delete", params={"id": history_id})
        api_client.assert_success(delete_response)
