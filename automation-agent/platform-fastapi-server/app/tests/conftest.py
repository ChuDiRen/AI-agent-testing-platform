"""
登录服务测试
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_login_success():
    """测试登录成功"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/login",
            json={
                "username": "admin",
                "password": "123456"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert "token" in data


@pytest.mark.asyncio
async def test_login_wrong_password():
    """测试登录失败（密码错误）"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/login",
            json={
                "username": "admin",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401 or response.status_code == 500


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["framework"] == "FastAPI"
