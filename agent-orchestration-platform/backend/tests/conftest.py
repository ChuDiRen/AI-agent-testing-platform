import pytest
import httpx
from typing import AsyncGenerator
import asyncio
from httpx import AsyncClient
import pytest_asyncio

# 基础配置 - 真实服务地址
BASE_URL = "http://localhost:8000"
TEST_TOKEN = "test_token_here"

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def check_service_health():
    """检查服务健康状态"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                pytest.skip(f"服务健康检查失败: {response.status_code}")
    except Exception as e:
        pytest.skip(f"服务不可用: {e}")

@pytest_asyncio.fixture(scope="session")
async def client(check_service_health) -> AsyncGenerator[httpx.AsyncClient, None]:
    """创建 HTTP 客户端 - 连接真实服务"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client

@pytest_asyncio.fixture(scope="session")
async def auth_client(check_service_health) -> AsyncGenerator[httpx.AsyncClient, None]:
    """创建带认证的 HTTP 客户端 - 连接真实服务"""
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30.0) as client:
        yield client

@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123456"
    }

@pytest.fixture
def test_agent_data():
    """测试Agent数据"""
    return {
        "name": "test_agent",
        "description": "Test agent description",
        "type": "chat"
    }

@pytest.fixture
def test_workflow_data():
    """测试Workflow数据"""
    return {
        "name": "test_workflow",
        "description": "Test workflow description"
    }

@pytest.fixture
def test_tool_data():
    """测试Tool数据"""
    return {
        "name": "test_tool",
        "type": "api",
        "config": {
            "endpoint": "https://api.example.com",
            "api_key": "test_key"
        }
    }

@pytest.fixture(scope="function")
async def cleanup_test_data(auth_client: AsyncClient):
    """测试后清理数据"""
    yield
    # 这里可以添加具体的清理逻辑
    # 比如删除测试创建的用户、Agent等
    pass
