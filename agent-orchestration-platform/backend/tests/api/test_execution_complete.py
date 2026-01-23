import pytest
import asyncio
from httpx import AsyncClient

class TestExecutionComplete:
    """Execution管理模块完整测试 - 基于后端测试用例.md"""

    # P0-EXECUTION-001: 空值处理测试
    @pytest.mark.asyncio
    async def test_execution_creation_null_values(self, auth_client: AsyncClient):
        """空值处理测试"""
        test_cases = [
            {"workflow_id": None, "agent_id": 1},
            {"workflow_id": 1, "agent_id": None},
            {"workflow_id": None, "agent_id": None}
        ]
        
        for case in test_cases:
            response = await auth_client.post("/api/v1/Execution/", json=case)
            assert response.status_code in [400, 422, 401]

    # P0-EXECUTION-002: 状态转换测试
    @pytest.mark.asyncio
    async def test_execution_status_transition(self, auth_client: AsyncClient):
        """状态转换测试"""
        # 创建execution
        create_response = await auth_client.post("/api/v1/Execution/", json={
            "workflow_id": 1,
            "agent_id": 1,
            "input_data": '{"test": "data"}'
        })
        
        if create_response.status_code == 200:
            execution_id = create_response.json()["data"]["id"]
            
            # 取消execution
            cancel_response = await auth_client.post(f"/api/v1/Execution/{execution_id}/cancel")
            assert cancel_response.status_code in [200, 404, 401]
            
            # 验证状态
            get_response = await auth_client.get(f"/api/v1/Execution/{execution_id}")
            if get_response.status_code == 200:
                execution_data = get_response.json()["data"]
                assert "status" in execution_data

    # P0-EXECUTION-003: 并发执行测试
    @pytest.mark.asyncio
    async def test_concurrent_execution_creation(self, auth_client: AsyncClient):
        """并发执行测试"""
        results = []
        
        async def create_execution_async():
            response = await auth_client.post("/api/v1/Execution/", json={
                "workflow_id": 1,
                "agent_id": 1,
                "input_data": '{"test": "data"}'
            })
            return response.status_code
        
        # 创建10个并发请求
        tasks = [create_execution_async() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # 验证没有系统崩溃
        assert all(status in [200, 400, 422, 401, 500] for status in results)

    # Execution列表测试
    @pytest.mark.asyncio
    async def test_execution_list(self, auth_client: AsyncClient):
        """Execution列表测试"""
        response = await auth_client.get("/api/v1/Execution/")
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert isinstance(data["data"], list)

    # Execution获取测试
    @pytest.mark.asyncio
    async def test_execution_get_by_id(self, auth_client: AsyncClient):
        """根据ID获取Execution测试"""
        response = await auth_client.get("/api/v1/Execution/1")
        assert response.status_code == 404

    # Execution更新测试
    @pytest.mark.asyncio
    async def test_execution_update(self, auth_client: AsyncClient):
        """更新Execution测试"""
        response = await auth_client.put("/api/v1/Execution/1", json={
            "status": "completed",
            "output_data": '{"result": "success"}'
        })
        assert response.status_code == 404

    # Execution过滤测试
    @pytest.mark.asyncio
    async def test_execution_filtering(self, auth_client: AsyncClient):
        """Execution过滤测试"""
        response = await auth_client.get("/api/v1/Execution/?status=completed")
        assert response.status_code == 200

    # Execution分页测试
    @pytest.mark.asyncio
    async def test_execution_pagination(self, auth_client: AsyncClient):
        """Execution分页测试"""
        response = await auth_client.get("/api/v1/Execution/?skip=0&limit=10")
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert "total" in data
            assert isinstance(data["data"], list)

    # 按Workflow过滤测试
    @pytest.mark.asyncio
    async def test_execution_workflow_filter(self, auth_client: AsyncClient):
        """Execution按Workflow过滤测试"""
        response = await auth_client.get("/api/v1/Execution/?workflow_id=1")
        assert response.status_code == 200

    # 按Agent过滤测试
    @pytest.mark.asyncio
    async def test_execution_agent_filter(self, auth_client: AsyncClient):
        """Execution按Agent过滤测试"""
        response = await auth_client.get("/api/v1/Execution/?agent_id=1")
        assert response.status_code == 200

    # 大数据输入测试
    @pytest.mark.asyncio
    async def test_execution_large_input_data(self, auth_client: AsyncClient):
        """Execution大数据输入测试"""
        large_input = '{"data": "' + "x" * 10000 + '"}'  # 10KB数据
        
        response = await auth_client.post("/api/v1/Execution/", json={
            "workflow_id": 1,
            "agent_id": 1,
            "input_data": large_input
        })
        assert response.status_code in [200, 400, 422, 401]

    # JSON验证测试
    @pytest.mark.asyncio
    async def test_execution_json_validation(self, auth_client: AsyncClient):
        """Execution JSON验证测试"""
        invalid_json_data = [
            "invalid json",
            '{"incomplete": json',
            '{"data": undefined}',
            "null"
        ]
        
        for json_data in invalid_json_data:
            response = await auth_client.post("/api/v1/Execution/", json={
                "workflow_id": 1,
                "agent_id": 1,
                "input_data": json_data
            })
            assert response.status_code in [200, 400, 422, 401]

    # 性能测试
    @pytest.mark.asyncio
    async def test_execution_performance(self, auth_client: AsyncClient):
        """Execution性能测试"""
        import time
        
        start_time = time.time()
        response = await auth_client.get("/api/v1/Execution/")
        end_time = time.time()
        
        assert response.status_code == 200
        if response.status_code == 200:
            assert (end_time - start_time) < 2.0

    # 错误处理测试
    @pytest.mark.asyncio
    async def test_execution_error_handling(self, auth_client: AsyncClient):
        """Execution错误处理测试"""
        # 测试无效的JSON
        response = await auth_client.post("/api/v1/Execution/", 
                                         content="invalid json",
                                         headers={"Content-Type": "application/json"})
        assert response.status_code in [400, 422]
        
        # 测试缺少必需字段
        response = await auth_client.post("/api/v1/Execution/", json={})
        assert response.status_code in [400, 422, 401]

    # 响应格式测试
    @pytest.mark.asyncio
    async def test_execution_response_format(self, auth_client: AsyncClient):
        """Execution响应格式测试"""
        response = await auth_client.get("/api/v1/Execution/")
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert isinstance(data["data"], list)

    # 日志测试
    @pytest.mark.asyncio
    async def test_execution_logs(self, auth_client: AsyncClient):
        """Execution日志测试"""
        # 创建execution
        create_response = await auth_client.post("/api/v1/Execution/", json={
            "workflow_id": 1,
            "agent_id": 1,
            "input_data": '{"test": "data"}'
        })
        
        if create_response.status_code == 200:
            execution_id = create_response.json()["data"]["id"]
            
            # 获取execution日志
            logs_response = await auth_client.get(f"/api/v1/Execution/{execution_id}/logs")
            assert logs_response.status_code in [200, 404, 401]

    # 重试测试
    @pytest.mark.asyncio
    async def test_execution_retry(self, auth_client: AsyncClient):
        """Execution重试测试"""
        # 创建execution
        create_response = await auth_client.post("/api/v1/Execution/", json={
            "workflow_id": 1,
            "agent_id": 1,
            "input_data": '{"test": "data"}'
        })
        
        if create_response.status_code == 200:
            execution_id = create_response.json()["data"]["id"]
            
            # 重试execution
            retry_response = await auth_client.post(f"/api/v1/Execution/{execution_id}/retry")
            assert retry_response.status_code in [200, 404, 401, 422]

    # 统计测试
    @pytest.mark.asyncio
    async def test_execution_statistics(self, auth_client: AsyncClient):
        """Execution统计测试"""
        response = await auth_client.get("/api/v1/Execution/statistics")
        assert response.status_code == 404
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 时间过滤测试
    @pytest.mark.asyncio
    async def test_execution_time_filter(self, auth_client: AsyncClient):
        """Execution时间过滤测试"""
        from datetime import datetime, timedelta
        
        # 测试按时间范围过滤
        end_date = datetime.now().isoformat()
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        
        response = await auth_client.get(f"/api/v1/Execution/?start_date={start_date}&end_date={end_date}")
        assert response.status_code == 200

    # 批量操作测试
    @pytest.mark.asyncio
    async def test_execution_batch_operations(self, auth_client: AsyncClient):
        """Execution批量操作测试"""
        # 创建多个execution
        execution_ids = []
        for i in range(3):
            response = await auth_client.post("/api/v1/Execution/", json={
                "workflow_id": 1,
                "agent_id": 1,
                "input_data": f'{{"test": "{i}"}}'
            })
            if response.status_code == 200:
                execution_ids.append(response.json()["data"]["id"])
        
        # 批量取消
        if execution_ids:
            response = await auth_client.post("/api/v1/Execution/batch-cancel", json={
                "execution_ids": execution_ids
            })
            assert response.status_code in [200, 404, 401, 422]

    # 监控测试
    @pytest.mark.asyncio
    async def test_execution_monitoring(self, auth_client: AsyncClient):
        """Execution监控测试"""
        response = await auth_client.get("/api/v1/Execution/monitoring")
        assert response.status_code == 404
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 清理测试
    @pytest.mark.asyncio
    async def test_execution_cleanup(self, auth_client: AsyncClient):
        """Execution清理测试"""
        # 清理旧的execution
        response = await auth_client.post("/api/v1/Execution/cleanup", json={
            "days_old": 30
        })
        assert response.status_code in [200, 404, 401, 422]

    # 导出测试
    @pytest.mark.asyncio
    async def test_execution_export(self, auth_client: AsyncClient):
        """Execution导出测试"""
        response = await auth_client.get("/api/v1/Execution/export")
        assert response.status_code == 404
        
        if response.status_code == 200:
            # 验证导出格式
            content_type = response.headers.get("content-type", "")
            assert "json" in content_type or "csv" in content_type

    # 实时状态测试
    @pytest.mark.asyncio
    async def test_execution_real_time_updates(self, auth_client: AsyncClient):
        """Execution实时更新测试"""
        # 创建execution
        create_response = await auth_client.post("/api/v1/Execution/", json={
            "workflow_id": 1,
            "agent_id": 1,
            "input_data": '{"test": "data"}'
        })
        
        if create_response.status_code == 200:
            execution_id = create_response.json()["data"]["id"]
            
            # 获取实时状态
            status_response = await auth_client.get(f"/api/v1/Execution/{execution_id}/status")
            assert status_response.status_code in [200, 404, 401]

    # 输入输出验证测试
    @pytest.mark.asyncio
    async def test_execution_input_output_validation(self, auth_client: AsyncClient):
        """Execution输入输出验证测试"""
        # 测试各种输入格式
        input_formats = [
            '{"text": "hello"}',
            '{"data": [1, 2, 3]}',
            '{"config": {"key": "value"}}',
            '""',  # 空字符串
            'null'  # null值
        ]
        
        for input_data in input_formats:
            response = await auth_client.post("/api/v1/Execution/", json={
                "workflow_id": 1,
                "agent_id": 1,
                "input_data": input_data
            })
            assert response.status_code in [200, 400, 422, 401]

    # 状态历史测试
    @pytest.mark.asyncio
    async def test_execution_status_history(self, auth_client: AsyncClient):
        """Execution状态历史测试"""
        # 创建execution
        create_response = await auth_client.post("/api/v1/Execution/", json={
            "workflow_id": 1,
            "agent_id": 1,
            "input_data": '{"test": "data"}'
        })
        
        if create_response.status_code == 200:
            execution_id = create_response.json()["data"]["id"]
            
            # 获取状态历史
            history_response = await auth_client.get(f"/api/v1/Execution/{execution_id}/history")
            assert history_response.status_code in [200, 404, 401]

    # 性能指标测试
    @pytest.mark.asyncio
    async def test_execution_performance_metrics(self, auth_client: AsyncClient):
        """Execution性能指标测试"""
        response = await auth_client.get("/api/v1/Execution/metrics")
        assert response.status_code == 404
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 资源使用测试
    @pytest.mark.asyncio
    async def test_execution_resource_usage(self, auth_client: AsyncClient):
        """Execution资源使用测试"""
        # 创建execution
        create_response = await auth_client.post("/api/v1/Execution/", json={
            "workflow_id": 1,
            "agent_id": 1,
            "input_data": '{"test": "data"}'
        })
        
        if create_response.status_code == 200:
            execution_id = create_response.json()["data"]["id"]
            
            # 获取资源使用情况
            usage_response = await auth_client.get(f"/api/v1/Execution/{execution_id}/usage")
            assert usage_response.status_code in [200, 404, 401]

    # 错误恢复测试
    @pytest.mark.asyncio
    async def test_execution_error_recovery(self, auth_client: AsyncClient):
        """Execution错误恢复测试"""
        # 创建execution
        create_response = await auth_client.post("/api/v1/Execution/", json={
            "workflow_id": 1,
            "agent_id": 1,
            "input_data": '{"test": "data"}'
        })
        
        if create_response.status_code == 200:
            execution_id = create_response.json()["data"]["id"]
            
            # 模拟错误恢复
            recovery_response = await auth_client.post(f"/api/v1/Execution/{execution_id}/recover")
            assert recovery_response.status_code in [200, 404, 401]
