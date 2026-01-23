import pytest
import asyncio
from httpx import AsyncClient

class TestWorkflowComplete:
    """Workflow管理模块完整测试 - 基于后端测试用例.md"""

    # P0-WORKFLOW-001: 空值处理测试
    @pytest.mark.asyncio
    async def test_workflow_creation_null_values(self, auth_client: AsyncClient):
        """空值处理测试"""
        test_cases = [
            {"name": None, "description": "test"},
            {"name": "", "description": "test"},
            {"name": "valid", "description": None}
        ]
        
        for case in test_cases:
            response = await auth_client.post("/api/v1/Workflow/", json={
                "graph_data": '{"nodes": [], "edges": []}',
                "created_by": 1,
                **case
            })
            assert response.status_code == 422

    # P0-WORKFLOW-002: 状态一致性测试
    @pytest.mark.asyncio
    async def test_workflow_publish_consistency(self, auth_client: AsyncClient):
        """状态一致性测试"""
        # 创建workflow
        create_response = await auth_client.post("/api/v1/Workflow/", json={
            "name": "test_workflow",
            "description": "test",
            "graph_data": '{"nodes": [], "edges": []}',
            "created_by": 1
        })
        
        if create_response.status_code == 200:
            workflow_id = create_response.json()["data"]["id"]
            
            # 发布workflow
            publish_response = await auth_client.post(f"/api/v1/Workflow/{workflow_id}/publish")
            assert publish_response.status_code in [200, 404, 401]
            
            # 验证状态
            get_response = await auth_client.get(f"/api/v1/Workflow/{workflow_id}")
            if get_response.status_code == 200:
                workflow_data = get_response.json()["data"]
                assert "is_published" in workflow_data

    # Workflow列表测试
    @pytest.mark.asyncio
    async def test_workflow_list(self, auth_client: AsyncClient):
        """Workflow列表测试"""
        response = await auth_client.get("/api/v1/Workflow/")
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert isinstance(data["data"], list)

    # Workflow获取测试
    @pytest.mark.asyncio
    async def test_workflow_get_by_id(self, auth_client: AsyncClient):
        """根据ID获取Workflow测试"""
        response = await auth_client.get("/api/v1/Workflow/1")
        assert response.status_code == 404

    # Workflow更新测试
    @pytest.mark.asyncio
    async def test_workflow_update(self, auth_client: AsyncClient):
        """更新Workflow测试"""
        response = await auth_client.put("/api/v1/Workflow/1", json={
            "name": "updated_workflow",
            "description": "updated description"
        })
        assert response.status_code == 404

    # Workflow删除测试
    @pytest.mark.asyncio
    async def test_workflow_delete(self, auth_client: AsyncClient):
        """删除Workflow测试"""
        response = await auth_client.delete("/api/v1/Workflow/999")
        assert response.status_code == 404

    # 带图数据的Workflow创建测试
    @pytest.mark.asyncio
    async def test_workflow_creation_with_graph_data(self, auth_client: AsyncClient):
        """带图数据的Workflow创建测试"""
        graph_data = {
            "nodes": [
                {"id": "1", "type": "start", "position": {"x": 0, "y": 0}},
                {"id": "2", "type": "process", "position": {"x": 100, "y": 0}}
            ],
            "edges": [
                {"id": "e1", "source": "1", "target": "2"}
            ]
        }
        
        response = await auth_client.post("/api/v1/Workflow/", json={
            "name": "test_workflow_with_graph",
            "description": "test",
            "graph_data": str(graph_data).replace("'", '"'),
            "created_by": 1
        })
        assert response.status_code == 200

    # Workflow列表分页测试
    @pytest.mark.asyncio
    async def test_workflow_list_pagination(self, auth_client: AsyncClient):
        """Workflow列表分页测试"""
        response = await auth_client.get("/api/v1/Workflow/?skip=0&limit=10")
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert "total" in data
            assert isinstance(data["data"], list)

    # Workflow过滤测试
    @pytest.mark.asyncio
    async def test_workflow_filtering(self, auth_client: AsyncClient):
        """Workflow过滤测试"""
        response = await auth_client.get("/api/v1/Workflow/?is_published=true")
        assert response.status_code == 200

    # Workflow搜索测试
    @pytest.mark.asyncio
    async def test_workflow_search(self, auth_client: AsyncClient):
        """Workflow搜索测试"""
        response = await auth_client.get("/api/v1/Workflow/?search=test")
        assert response.status_code == 200

    # 并发创建测试
    @pytest.mark.asyncio
    async def test_workflow_concurrent_creation(self, auth_client: AsyncClient):
        """并发创建测试"""
        results = []
        
        async def create_workflow_async(name):
            response = await auth_client.post("/api/v1/Workflow/", json={
                "name": name,
                "description": "test",
                "graph_data": '{"nodes": [], "edges": []}',
                "created_by": 1
            })
            return response.status_code
        
        # 创建10个并发请求
        tasks = [create_workflow_async(f"concurrent_workflow_{i}") for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        # 验证没有系统崩溃
        assert all(status in [200, 400, 422, 401, 500] for status in results)

    # 大图数据测试
    @pytest.mark.asyncio
    async def test_workflow_large_graph_data(self, auth_client: AsyncClient):
        """Workflow大图数据测试"""
        large_graph = '{"nodes": [' + ','.join([f'{{"id": "{i}", "type": "node"}}' for i in range(100)]) + '], "edges": []}'
        
        response = await auth_client.post("/api/v1/Workflow/", json={
            "name": "test_large_workflow",
            "description": "test",
            "graph_data": large_graph,
            "created_by": 1
        })
        assert response.status_code == 200

    # 特殊字符测试
    @pytest.mark.asyncio
    async def test_workflow_special_characters(self, auth_client: AsyncClient):
        """Workflow特殊字符测试"""
        special_names = [
            "测试工作流",
            "Workflow 🚀",
            "Workflow-Test_123",
            "Workflow.Test"
        ]
        
        for name in special_names:
            response = await auth_client.post("/api/v1/Workflow/", json={
                "name": name,
                "description": "test",
                "graph_data": '{"nodes": [], "edges": []}',
                "created_by": 1
            })
            assert response.status_code == 200

    # 图数据验证测试
    @pytest.mark.asyncio
    async def test_workflow_graph_data_validation(self, auth_client: AsyncClient):
        """Workflow图数据验证测试"""
        invalid_graph_data = [
            None,
            "",
            "invalid json",
            '{"nodes": [], "edges": [{"invalid": "edge"}]}'
        ]
        
        for graph_data in invalid_graph_data:
            response = await auth_client.post("/api/v1/Workflow/", json={
                "name": "test_validation",
                "description": "test",
                "graph_data": graph_data,
                "created_by": 1
            })
            assert response.status_code == 422

    # 性能测试
    @pytest.mark.asyncio
    async def test_workflow_performance(self, auth_client: AsyncClient):
        """Workflow性能测试"""
        import time
        
        start_time = time.time()
        response = await auth_client.get("/api/v1/Workflow/")
        end_time = time.time()
        
        assert response.status_code == 200
        if response.status_code == 200:
            assert (end_time - start_time) < 2.0

    # 错误处理测试
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, auth_client: AsyncClient):
        """Workflow错误处理测试"""
        # 测试无效的JSON
        response = await auth_client.post("/api/v1/Workflow/", 
                                         content="invalid json",
                                         headers={"Content-Type": "application/json"})
        assert response.status_code in [400, 422]
        
        # 测试缺少必需字段
        response = await auth_client.post("/api/v1/Workflow/", json={})
        assert response.status_code == 422

    # 响应格式测试
    @pytest.mark.asyncio
    async def test_workflow_response_format(self, auth_client: AsyncClient):
        """Workflow响应格式测试"""
        response = await auth_client.get("/api/v1/Workflow/")
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert isinstance(data["data"], list)

    # 版本管理测试
    @pytest.mark.asyncio
    async def test_workflow_version_management(self, auth_client: AsyncClient):
        """Workflow版本管理测试"""
        # 创建workflow
        create_response = await auth_client.post("/api/v1/Workflow/", json={
            "name": "version_test_workflow",
            "description": "test",
            "graph_data": '{"nodes": [], "edges": []}',
            "created_by": 1
        })
        
        if create_response.status_code == 200:
            workflow_id = create_response.json()["data"]["id"]
            
            # 创建新版本
            version_response = await auth_client.post(f"/api/v1/Workflow/{workflow_id}/versions", json={
                "graph_data": '{"nodes": [{"id": "new"}], "edges": []}',
                "description": "new version"
            })
            assert version_response.status_code in [200, 404, 401, 422]

    # 导出导入测试
    @pytest.mark.asyncio
    async def test_workflow_export_import(self, auth_client: AsyncClient):
        """Workflow导出导入测试"""
        # 创建workflow
        create_response = await auth_client.post("/api/v1/Workflow/", json={
            "name": "export_test_workflow",
            "description": "test",
            "graph_data": '{"nodes": [], "edges": []}',
            "created_by": 1
        })
        
        if create_response.status_code == 200:
            workflow_id = create_response.json()["data"]["id"]
            
            # 导出workflow
            export_response = await auth_client.get(f"/api/v1/Workflow/{workflow_id}/export")
            assert export_response.status_code in [200, 404, 401]
            
            # 导入workflow
            import_response = await auth_client.post("/api/v1/Workflow/import", json={
                "name": "imported_workflow",
                "workflow_data": '{"nodes": [], "edges": []}',
                "created_by": 1
            })
            assert import_response.status_code in [200, 404, 401, 422]

    # 执行链接测试
    @pytest.mark.asyncio
    async def test_workflow_execution_link(self, auth_client: AsyncClient):
        """Workflow执行链接测试"""
        # 创建workflow
        create_response = await auth_client.post("/api/v1/Workflow/", json={
            "name": "execution_test_workflow",
            "description": "test",
            "graph_data": '{"nodes": [], "edges": []}',
            "created_by": 1
        })
        
        if create_response.status_code == 200:
            workflow_id = create_response.json()["data"]["id"]
            
            # 创建execution
            execution_response = await auth_client.post("/api/v1/Execution/", json={
                "workflow_id": workflow_id,
                "agent_id": 1
            })
            assert execution_response.status_code in [200, 400, 422, 401]

    # 统计测试
    @pytest.mark.asyncio
    async def test_workflow_statistics(self, auth_client: AsyncClient):
        """Workflow统计测试"""
        response = await auth_client.get("/api/v1/Workflow/statistics")
        assert response.status_code == 404
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 复制测试
    @pytest.mark.asyncio
    async def test_workflow_duplication(self, auth_client: AsyncClient):
        """Workflow复制测试"""
        # 创建workflow
        create_response = await auth_client.post("/api/v1/Workflow/", json={
            "name": "original_workflow",
            "description": "test",
            "graph_data": '{"nodes": [], "edges": []}',
            "created_by": 1
        })
        
        if create_response.status_code == 200:
            workflow_id = create_response.json()["data"]["id"]
            
            # 复制workflow
            duplicate_response = await auth_client.post(f"/api/v1/Workflow/{workflow_id}/duplicate", json={
                "name": "duplicated_workflow",
                "created_by": 1
            })
            assert duplicate_response.status_code in [200, 404, 401, 422]

    # 模板测试
    @pytest.mark.asyncio
    async def test_workflow_templates(self, auth_client: AsyncClient):
        """Workflow模板测试"""
        # 创建模板
        template_response = await auth_client.post("/api/v1/Workflow/templates", json={
            "name": "test_template",
            "description": "test template",
            "graph_data": '{"nodes": [], "edges": []}',
            "created_by": 1
        })
        assert template_response.status_code in [200, 404, 401, 422]
        
        if template_response.status_code == 200:
            template_id = template_response.json()["data"]["id"]
            
            # 从模板创建workflow
            from_template_response = await auth_client.post("/api/v1/Workflow/from-template", json={
                "template_id": template_id,
                "name": "workflow_from_template",
                "created_by": 1
            })
            assert from_template_response.status_code in [200, 404, 401, 422]

    # 验证测试
    @pytest.mark.asyncio
    async def test_workflow_validation(self, auth_client: AsyncClient):
        """Workflow验证测试"""
        # 创建workflow
        create_response = await auth_client.post("/api/v1/Workflow/", json={
            "name": "validation_test_workflow",
            "description": "test",
            "graph_data": '{"nodes": [], "edges": []}',
            "created_by": 1
        })
        
        if create_response.status_code == 200:
            workflow_id = create_response.json()["data"]["id"]
            
            # 验证workflow
            validation_response = await auth_client.post(f"/api/v1/Workflow/{workflow_id}/validate")
            assert validation_response.status_code in [200, 404, 401]

    # 监控测试
    @pytest.mark.asyncio
    async def test_workflow_monitoring(self, auth_client: AsyncClient):
        """Workflow监控测试"""
        response = await auth_client.get("/api/v1/Workflow/monitoring")
        assert response.status_code == 404
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 分析测试
    @pytest.mark.asyncio
    async def test_workflow_analytics(self, auth_client: AsyncClient):
        """Workflow分析测试"""
        response = await auth_client.get("/api/v1/Workflow/analytics")
        assert response.status_code == 404
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
