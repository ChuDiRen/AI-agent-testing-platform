"""
API 统计接口测试
测试 ApiStatisticsController 的所有接口
"""
import pytest
from datetime import datetime, timedelta


class TestApiStatisticsController:
    """API 统计 Controller 测试"""
    
    def test_get_overview_success(self, api_client):
        """测试获取系统总览统计 - 成功"""
        response = api_client.get("/ApiStatistics/overview")
        data = api_client.assert_success(response)
        
        # 验证返回数据结构
        result = data.get("data")
        assert "projectCount" in result
        assert "apiCount" in result
        assert "testcaseCount" in result
        assert "planCount" in result
        assert "totalTests" in result
        assert "successRate" in result
        assert "avgTime" in result
        
        # 验证数据类型
        assert isinstance(result["projectCount"], int)
        assert isinstance(result["successRate"], (int, float))
        assert result["successRate"] >= 0
        assert result["successRate"] <= 100
    
    def test_get_overview_no_auth(self, api_client_no_auth):
        """测试获取系统总览统计 - 未登录"""
        response = api_client_no_auth.get("/ApiStatistics/overview")
        assert response.status_code in [401, 403]
    
    def test_get_execution_count_all(self, api_client):
        """测试查询执行次数 - 查询所有"""
        response = api_client.get("/ApiStatistics/executionCount")
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert "total_count" in result
        assert "success_count" in result
        assert "failed_count" in result
        assert "running_count" in result
        
        # 验证数据逻辑
        total = result["total_count"]
        success = result["success_count"]
        failed = result["failed_count"]
        running = result["running_count"]
        assert total >= 0
        assert success + failed + running <= total
    
    def test_get_execution_count_by_plan(self, api_client):
        """测试查询执行次数 - 指定计划ID"""
        response = api_client.get("/ApiStatistics/executionCount", params={"plan_id": 1})
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert "total_count" in result
    
    def test_get_case_count_success(self, api_client):
        """测试查询用例数量统计 - 成功"""
        response = api_client.get("/ApiStatistics/caseCount", params={"project_id": 1})
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert "total_cases" in result
        assert isinstance(result["total_cases"], int)
    
    def test_get_case_count_with_plan(self, api_client):
        """测试查询用例数量统计 - 带计划ID"""
        response = api_client.get("/ApiStatistics/caseCount", params={
            "plan_id": 1,
            "project_id": 1
        })
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert "total_cases" in result
        # 如果有执行记录，应该包含 last_execution
        if result.get("last_execution"):
            assert "test_name" in result["last_execution"]
            assert "test_status" in result["last_execution"]
    
    def test_get_pass_rate_default(self, api_client):
        """测试查询通过率 - 默认7天"""
        response = api_client.get("/ApiStatistics/passRate")
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert "total" in result
        assert "passed" in result
        assert "failed" in result
        assert "pass_rate" in result
        assert "period_days" in result
        
        # 验证通过率计算正确
        if result["total"] > 0:
            expected_rate = round(result["passed"] / result["total"] * 100, 2)
            assert result["pass_rate"] == expected_rate
    
    def test_get_pass_rate_custom_days(self, api_client):
        """测试查询通过率 - 自定义天数"""
        response = api_client.get("/ApiStatistics/passRate", params={"days": 30})
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert result["period_days"] == 30
    
    def test_get_pass_rate_with_plan_id(self, api_client):
        """测试查询通过率 - 指定计划ID"""
        response = api_client.get("/ApiStatistics/passRate", params={
            "plan_id": 1,
            "days": 7
        })
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert "pass_rate" in result
    
    def test_get_execution_trend_default(self, api_client):
        """测试查询执行趋势 - 默认5次"""
        response = api_client.get("/ApiStatistics/executionTrend")
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert "trend" in result
        assert "total" in result
        assert isinstance(result["trend"], list)
        assert len(result["trend"]) <= 5
        
        # 验证趋势数据结构
        if result["trend"]:
            trend_item = result["trend"][0]
            assert "execution_id" in trend_item
            assert "test_name" in trend_item
            assert "status" in trend_item
            assert "create_time" in trend_item
    
    def test_get_execution_trend_custom_limit(self, api_client):
        """测试查询执行趋势 - 自定义数量"""
        response = api_client.get("/ApiStatistics/executionTrend", params={"limit": 10})
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert len(result["trend"]) <= 10
    
    def test_get_time_trend_default(self, api_client):
        """测试查询耗时趋势 - 默认10次"""
        response = api_client.get("/ApiStatistics/timeTrend")
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert "trend" in result
        assert "avg_time" in result
        assert "max_time" in result
        assert "min_time" in result
        
        # 验证时间逻辑
        if result["trend"]:
            assert result["max_time"] >= result["min_time"]
            assert result["avg_time"] >= 0
    
    def test_get_time_trend_with_plan(self, api_client):
        """测试查询耗时趋势 - 指定计划"""
        response = api_client.get("/ApiStatistics/timeTrend", params={
            "plan_id": 1,
            "limit": 5
        })
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert "trend" in result
    
    def test_get_failed_top5_default(self, api_client):
        """测试查询失败TOP5 - 默认30天"""
        response = api_client.get("/ApiStatistics/failedTop5")
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert "top5" in result
        assert "period_days" in result
        assert "total_failures" in result
        assert isinstance(result["top5"], list)
        assert len(result["top5"]) <= 5
        
        # 验证TOP5数据结构
        if result["top5"]:
            top_item = result["top5"][0]
            assert "case_id" in top_item
            assert "test_name" in top_item
            assert "count" in top_item
    
    def test_get_failed_top5_custom_days(self, api_client):
        """测试查询失败TOP5 - 自定义天数"""
        response = api_client.get("/ApiStatistics/failedTop5", params={"days": 60})
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert result["period_days"] == 60
    
    def test_get_daily_stats_default(self, api_client):
        """测试查询每日统计 - 默认7天"""
        response = api_client.get("/ApiStatistics/dailyStats")
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert "daily_stats" in result
        assert "period_days" in result
        assert isinstance(result["daily_stats"], list)
        
        # 验证每日统计数据结构
        if result["daily_stats"]:
            daily_item = result["daily_stats"][0]
            assert "date" in daily_item
            assert "total" in daily_item
            assert "passed" in daily_item
            assert "failed" in daily_item
    
    def test_get_daily_stats_custom_days(self, api_client):
        """测试查询每日统计 - 自定义天数"""
        response = api_client.get("/ApiStatistics/dailyStats", params={"days": 14})
        data = api_client.assert_success(response)
        
        result = data.get("data")
        assert result["period_days"] == 14


class TestApiStatisticsControllerEdgeCases:
    """API 统计 Controller 边界情况测试"""
    
    def test_invalid_plan_id(self, api_client):
        """测试无效的计划ID"""
        response = api_client.get("/ApiStatistics/executionCount", params={"plan_id": 99999})
        data = api_client.assert_success(response)
        
        # 应该返回空数据或0
        result = data.get("data")
        assert result["total_count"] >= 0
    
    def test_zero_days(self, api_client):
        """测试0天查询"""
        response = api_client.get("/ApiStatistics/passRate", params={"days": 0})
        # 可能返回错误或空数据
        assert response.status_code in [200, 400]
    
    def test_negative_days(self, api_client):
        """测试负数天数"""
        response = api_client.get("/ApiStatistics/passRate", params={"days": -1})
        # 应该返回错误或被处理为0
        assert response.status_code in [200, 400]
    
    def test_large_limit(self, api_client):
        """测试过大的limit"""
        response = api_client.get("/ApiStatistics/executionTrend", params={"limit": 1000})
        data = api_client.assert_success(response)
        
        # 应该有合理的限制
        result = data.get("data")
        assert len(result["trend"]) <= 1000
    
    def test_concurrent_requests(self, api_client):
        """测试并发请求"""
        import concurrent.futures
        
        def make_request():
            response = api_client.get("/ApiStatistics/overview")
            return response.status_code
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # 所有请求都应该成功
        assert all(status == 200 for status in results)
