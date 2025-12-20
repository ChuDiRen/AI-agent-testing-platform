"""
测试计划和执行完整 E2E 测试
测试测试计划的创建、用例关联、执行、报告等完整流程
"""
import pytest
import json


class TestPlanManagementE2E:
    """测试计划管理 E2E 测试"""
    
    def test_testplan_full_lifecycle(self, api_client, unique_name):
        """测试计划完整生命周期"""
        # 准备：创建项目、接口和用例
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"计划测试项目_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建测试用例
        case_ids = []
        for i in range(3):
            case_response = api_client.post("/ApiInfoCase/insert", json={
                "project_id": project_id,
                "case_name": f"测试用例{i}_{unique_name}",
                "request_url": f"/api/test/{i}",
                "request_method": "GET"
            })
            case_data = api_client.assert_success(case_response)
            case_ids.append(case_data["data"]["id"])
        
        # 1. 创建测试计划
        plan_data = {
            "project_id": project_id,
            "collection_name": f"回归测试计划_{unique_name}",
            "collection_desc": "每日回归测试",
            "status": 1
        }
        create_response = api_client.post("/ApiCollectionInfo/insert", json=plan_data)
        create_result = api_client.assert_success(create_response)
        plan_id = create_result["data"]["id"]
        print(f"✓ 创建测试计划成功: ID={plan_id}")
        
        # 2. 添加用例到测试计划
        for case_id in case_ids:
            detail_response = api_client.post("/ApiCollectionDetail/insert", json={
                "collection_info_id": plan_id,
                "case_info_id": case_id
            })
            api_client.assert_success(detail_response)
        print(f"✓ 添加了 {len(case_ids)} 个用例到测试计划")
        
        # 3. 查询测试计划详情
        detail_response = api_client.get("/ApiCollectionInfo/queryById", params={"id": plan_id})
        detail_result = api_client.assert_success(detail_response)
        assert detail_result["data"]["collection_name"] == f"回归测试计划_{unique_name}"
        print(f"✓ 测试计划详情查询成功")
        
        # 4. 查询测试计划的用例列表
        cases_response = api_client.post("/ApiCollectionDetail/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "collection_info_id": plan_id
        })
        cases_result = api_client.assert_success(cases_response)
        assert len(cases_result["data"]) == 3
        print(f"✓ 测试计划用例列表查询成功")
        
        # 5. 更新测试计划
        update_data = {
            "id": plan_id,
            "collection_name": f"回归测试计划_V2_{unique_name}",
            "collection_desc": "更新后的回归测试计划"
        }
        update_response = api_client.put("/ApiCollectionInfo/update", json=update_data)
        api_client.assert_success(update_response)
        print(f"✓ 测试计划更新成功")
        
        # 6. 从测试计划移除用例
        remove_response = api_client.delete("/ApiCollectionDetail/delete", params={
            "collection_info_id": plan_id,
            "case_info_id": case_ids[0]
        })
        api_client.assert_success(remove_response)
        print(f"✓ 从测试计划移除用例成功")
        
        # 7. 删除测试计划
        delete_response = api_client.delete("/ApiCollectionInfo/delete", params={"id": plan_id})
        api_client.assert_success(delete_response)
        print(f"✓ 测试计划删除成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_testplan_execution(self, api_client, unique_name):
        """测试计划执行流程"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"执行计划_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建用例
        case_response = api_client.post("/ApiInfoCase/insert", json={
            "project_id": project_id,
            "case_name": f"可执行用例_{unique_name}",
            "request_url": "/ApiStatistics/overview",
            "request_method": "GET"
        })
        case_data = api_client.assert_success(case_response)
        case_id = case_data["data"]["id"]
        
        # 创建测试计划
        plan_response = api_client.post("/ApiCollectionInfo/insert", json={
            "project_id": project_id,
            "collection_name": f"执行测试_{unique_name}"
        })
        plan_data = api_client.assert_success(plan_response)
        plan_id = plan_data["data"]["id"]
        
        # 添加用例到计划
        api_client.post("/ApiCollectionDetail/insert", json={
            "collection_info_id": plan_id,
            "case_info_id": case_id
        })
        
        # 执行测试计划（如果有执行接口）
        # execute_response = api_client.post("/ApiCollectionInfo/execute", json={"id": plan_id})
        # execute_data = api_client.assert_success(execute_response)
        # execution_id = execute_data["data"]["execution_id"]
        # print(f"✓ 测试计划执行成功: execution_id={execution_id}")
        
        # 查询执行统计
        stats_response = api_client.get("/ApiStatistics/executionCount", params={
            "plan_id": plan_id
        })
        stats_data = api_client.assert_success(stats_response)
        print(f"✓ 执行统计查询成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_testplan_scheduling(self, api_client, unique_name):
        """测试计划调度"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"调度测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建测试计划
        plan_response = api_client.post("/ApiCollectionInfo/insert", json={
            "project_id": project_id,
            "collection_name": f"定时计划_{unique_name}",
            "schedule_type": "cron",
            "schedule_config": json.dumps({
                "cron": "0 0 * * *",
                "timezone": "Asia/Shanghai"
            })
        })
        plan_data = api_client.assert_success(plan_response)
        plan_id = plan_data["data"]["id"]
        
        print(f"✓ 创建定时测试计划成功")
        
        # 查询调度配置
        detail_response = api_client.get("/ApiCollectionInfo/queryById", params={"id": plan_id})
        detail_data = api_client.assert_success(detail_response)
        print(f"✓ 调度配置查询成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestPlanReporting:
    """测试计划报告测试"""
    
    def test_execution_report_generation(self, api_client, unique_name):
        """测试执行报告生成"""
        # 创建项目和计划
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"报告测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        plan_response = api_client.post("/ApiCollectionInfo/insert", json={
            "project_id": project_id,
            "collection_name": f"报告计划_{unique_name}"
        })
        plan_data = api_client.assert_success(plan_response)
        plan_id = plan_data["data"]["id"]
        
        # 查询执行趋势
        trend_response = api_client.get("/ApiStatistics/executionTrend", params={
            "plan_id": plan_id,
            "limit": 10
        })
        trend_data = api_client.assert_success(trend_response)
        print(f"✓ 执行趋势查询成功")
        
        # 查询通过率
        pass_rate_response = api_client.get("/ApiStatistics/passRate", params={
            "plan_id": plan_id,
            "days": 7
        })
        pass_rate_data = api_client.assert_success(pass_rate_response)
        print(f"✓ 通过率查询成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_report_export(self, api_client, unique_name):
        """测试报告导出"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"导出测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 查询每日统计（用于导出）
        daily_stats_response = api_client.get("/ApiStatistics/dailyStats", params={
            "days": 7
        })
        daily_stats_data = api_client.assert_success(daily_stats_response)
        assert "daily_stats" in daily_stats_data["data"]
        print(f"✓ 每日统计数据获取成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestTaskManagement:
    """测试任务管理测试"""
    
    def test_task_creation_and_execution(self, api_client, unique_name):
        """测试任务创建和执行"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"任务测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建测试计划
        plan_response = api_client.post("/ApiCollectionInfo/insert", json={
            "project_id": project_id,
            "collection_name": f"任务计划_{unique_name}"
        })
        plan_data = api_client.assert_success(plan_response)
        plan_id = plan_data["data"]["id"]
        
        # 创建测试任务
        task_response = api_client.post("/TestTask/insert", json={
            "project_id": project_id,
            "task_name": f"自动化任务_{unique_name}",
            "task_desc": "自动化测试任务",
            "collection_id": plan_id,
            "task_type": "scheduled",
            "status": 1
        })
        task_data = api_client.assert_success(task_response)
        task_id = task_data["data"]["id"]
        print(f"✓ 创建测试任务成功: ID={task_id}")
        
        # 查询任务详情
        detail_response = api_client.get("/TestTask/queryById", params={"id": task_id})
        detail_data = api_client.assert_success(detail_response)
        assert detail_data["data"]["task_name"] == f"自动化任务_{unique_name}"
        print(f"✓ 任务详情查询成功")
        
        # 更新任务状态
        update_response = api_client.put("/TestTask/update", json={
            "id": task_id,
            "status": 0
        })
        api_client.assert_success(update_response)
        print(f"✓ 任务状态更新成功")
        
        # 删除任务
        delete_response = api_client.delete("/TestTask/delete", params={"id": task_id})
        api_client.assert_success(delete_response)
        print(f"✓ 任务删除成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_task_scheduling(self, api_client, unique_name):
        """测试任务调度"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"调度任务_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建定时任务
        task_response = api_client.post("/TestTask/insert", json={
            "project_id": project_id,
            "task_name": f"定时任务_{unique_name}",
            "task_type": "scheduled",
            "cron_expression": "0 0 * * *",
            "status": 1
        })
        task_data = api_client.assert_success(task_response)
        task_id = task_data["data"]["id"]
        
        print(f"✓ 创建定时任务成功")
        
        # 查询任务列表
        list_response = api_client.post("/TestTask/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project_id
        })
        list_data = api_client.assert_success(list_response)
        assert len(list_data["data"]) >= 1
        print(f"✓ 任务列表查询成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
