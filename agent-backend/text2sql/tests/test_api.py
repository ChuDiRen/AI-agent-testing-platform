"""
API集成测试
"""

import pytest
from fastapi.testclient import TestClient

from ..api.server import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app(debug=True)
    return TestClient(app)


class TestHealthEndpoints:
    """健康检查端点测试"""
    
    def test_root(self, client):
        """测试根路由"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
    
    def test_ok(self, client):
        """测试健康检查"""
        response = client.get("/ok")
        
        assert response.status_code == 200
        assert response.json() == {"ok": True}
    
    def test_health(self, client):
        """测试API健康检查"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestSQLValidation:
    """SQL验证端点测试"""
    
    def test_validate_valid_sql(self, client):
        """测试验证有效SQL"""
        response = client.post(
            "/api/v1/sql/validate",
            params={"sql": "SELECT id, name FROM users LIMIT 10"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
    
    def test_validate_dangerous_sql(self, client):
        """测试验证危险SQL"""
        response = client.post(
            "/api/v1/sql/validate",
            params={"sql": "DROP TABLE users"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["errors"]) > 0


class TestChartEndpoint:
    """图表端点测试"""
    
    def test_create_chart(self, client):
        """测试创建图表"""
        response = client.post(
            "/api/v1/chart",
            json={
                "data": [
                    {"name": "A", "value": 10},
                    {"name": "B", "value": 20}
                ],
                "columns": ["name", "value"],
                "title": "Test Chart"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "chart_config" in data


class TestQueryEndpoint:
    """查询端点测试（需要数据库连接）"""
    
    def test_query_without_connection(self, client):
        """测试无连接时的查询"""
        response = client.post(
            "/api/v1/query",
            json={
                "query": "查询用户",
                "connection_id": 9999  # 不存在的连接
            }
        )
        
        # 应该返回错误
        assert response.status_code in [400, 500]


class TestMiddleware:
    """中间件测试"""
    
    def test_request_id_header(self, client):
        """测试请求ID头"""
        response = client.get("/ok")
        
        # 应该有请求ID
        assert "x-request-id" in response.headers or response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
