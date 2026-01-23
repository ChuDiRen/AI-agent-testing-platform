# API 测试技能

## 触发条件
当用户提到：接口测试、API测试、httpx、pytest、自动化测试、可执行测试用例

## 技术栈
- pytest + httpx（异步HTTP客户端）
- pytest-asyncio（异步测试支持）
- pytest-html（测试报告）
- pytest-cov（覆盖率测试）
- 真实服务测试（非Mock优先）

## 项目结构
```
tests/
├── conftest.py          # 全局 fixtures
├── pytest.ini          # pytest配置
├── requirements.txt     # 测试依赖
├── run_tests.py        # 测试运行脚本
├── README.md           # 说明文档
├── api/                 # API 测试
│   ├── __init__.py
│   ├── test_auth.py     # 认证授权测试
│   ├── test_agent.py    # Agent管理测试
│   ├── test_workflow.py # Workflow管理测试
│   ├── test_execution.py# Execution管理测试
│   ├── test_tool.py     # Tool管理测试
│   ├── test_billing.py  # 计费统计测试
│   ├── test_batch.py    # 批量操作测试
│   └── test_boundary.py # 边界条件测试
├── unit/                # 单元测试
└── data/                # 测试数据
    └── test_data.yaml
```

## conftest.py 配置
```python
import pytest
import httpx
from typing import AsyncGenerator
import asyncio
from unittest.mock import Mock, patch

# 基础配置 - 真实服务地址
BASE_URL = "http://localhost:8000"
TEST_TOKEN = "test_token_here"

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """创建 HTTP 客户端 - 连接真实服务"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client

@pytest.fixture(scope="session")
async def auth_client() -> AsyncGenerator[httpx.AsyncClient, None]:
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

# 仅在必要时使用Mock - 优先使用真实服务
@pytest.fixture
def mock_db_session():
    """模拟数据库会话 - 仅用于异常测试"""
    with patch('app.db.session.get_db') as mock_get_db:
        mock_session = Mock()
        mock_get_db.return_value = mock_session
        yield mock_session

@pytest.fixture
def mock_logger():
    """模拟日志记录器 - 仅用于日志验证"""
    with patch('app.core.logger.setup_logger') as mock_logger:
        mock_instance = Mock()
        mock_logger.return_value = mock_instance
        yield mock_instance
```

## 真实服务测试原则

### 1. 优先使用真实服务
- 所有功能测试优先连接真实后端服务
- 仅在异常场景、性能测试、日志验证时使用Mock
- 确保测试环境与生产环境一致

### 2. 测试数据管理
```python
@pytest.fixture(scope="function")
async def cleanup_test_data(auth_client: AsyncClient):
    """测试后清理数据"""
    yield
    # 清理测试创建的数据
    # 实现具体的清理逻辑

@pytest.mark.asyncio
async def test_with_real_data(auth_client: AsyncClient, cleanup_test_data):
    """使用真实数据的测试"""
    # 创建真实数据
    response = await auth_client.post("/api/v1/Agent/", json={
        "name": "real_test_agent",
        "description": "Real test"
    })
    assert response.status_code == 200
    
    # 验证数据存在
    agent_id = response.json()["data"]["id"]
    get_response = await auth_client.get(f"/api/v1/Agent/{agent_id}")
    assert get_response.status_code == 200
```

### 3. 环境检查
```python
@pytest.fixture(scope="session")
async def check_service_health():
    """检查服务健康状态"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
    except Exception as e:
        pytest.skip(f"服务不可用: {e}")
```

## 测试用例模板

### 基础 CRUD 测试（真实服务）
```python
# tests/api/test_user.py
import pytest
from httpx import AsyncClient

class TestUserAPI:
    """用户接口测试 - 基于真实服务"""
    
    @pytest.mark.asyncio
    async def test_create_user_real(self, auth_client: AsyncClient, test_user_data):
        """测试创建用户 - 真实服务"""
        response = await auth_client.post("/api/v1/Auth/register", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
        
        # 验证用户真实存在
        user_id = data["data"]["id"]
        get_response = await auth_client.get(f"/api/v1/Auth/user/info", 
                                             headers={"current_user_id": str(user_id)})
        assert get_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_query_by_page_real(self, auth_client: AsyncClient):
        """测试分页查询 - 真实服务"""
        response = await auth_client.post("/api/v1/Auth/users", json={
            "skip": 0,
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert isinstance(data["data"], list)
```

### 异常测试（有限Mock）
```python
@pytest.mark.asyncio
async def test_database_error_only(self, auth_client: AsyncClient, mock_db_session):
    """测试数据库异常 - 仅在异常场景使用Mock"""
    mock_db_session.side_effect = Exception("Database connection failed")
    
    response = await auth_client.get("/api/v1/Agent/")
    assert response.status_code == 500
    assert "detail" in response.json()
```

### 性能测试（真实服务）
```python
@pytest.mark.asyncio
async def test_performance_real(self, auth_client: AsyncClient):
    """性能测试 - 真实服务"""
    import time
    
    # 创建测试数据
    for i in range(10):
        await auth_client.post("/api/v1/Agent/", json={
            "name": f"perf_test_{i}",
            "description": "Performance test"
        })
    
    # 测试查询性能
    start_time = time.time()
    response = await auth_client.get("/api/v1/Agent/?limit=20")
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # 1秒内完成
```

## 参数化测试

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("username,password,expected_status", [
    ("valid_user", "valid_pass", 200),
    ("", "valid_pass", 400),
    ("valid_user", "", 400),
    ("nonexistent", "wrong", 401),
])
async def test_login_scenarios(self, client: AsyncClient, username, password, expected_status):
    """测试登录场景 - 真实服务"""
    response = await client.post("/api/v1/Auth/login", json={
        "username": username,
        "password": password
    })
    
    assert response.status_code == expected_status
```

## 安全测试（真实服务）

```python
@pytest.mark.asyncio
@pytest.mark.security
async def test_sql_injection_real(self, client: AsyncClient):
    """SQL注入测试 - 真实服务"""
    malicious_inputs = [
        "admin'--",
        "admin' OR '1'='1",
        "'; DROP TABLE users; --"
    ]
    
    for payload in malicious_inputs:
        response = await client.post("/api/v1/Auth/login", json={
            "username": payload,
            "password": "password"
        })
        assert response.status_code != 500
        assert response.status_code in [401, 400, 422]
```

## 并发测试（真实服务）

```python
@pytest.mark.asyncio
async def test_concurrent_requests_real(self, auth_client: AsyncClient):
    """并发请求测试 - 真实服务"""
    import asyncio
    
    async def create_agent():
        return await auth_client.post("/api/v1/Agent/", json={
            "name": "concurrent_test",
            "description": "test"
        })
    
    # 并发创建
    tasks = [create_agent() for _ in range(10)]
    responses = await asyncio.gather(*tasks)
    
    # 验证没有系统崩溃
    for response in responses:
        assert response.status_code in [200, 400, 422, 500]
```

## 运行测试

```bash
# 确保服务运行
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 运行所有测试
pytest tests/api/ -v

# 运行指定文件
pytest tests/api/test_user.py -v

# 运行指定测试类
pytest tests/api/test_user.py::TestUserAPI -v

# 运行指定测试方法
pytest tests/api/test_user.py::TestUserAPI::test_create_user_real -v

# 生成 HTML 报告
pytest tests/api/ -v --html=report.html

# 显示覆盖率
pytest tests/api/ -v --cov=app --cov-report=html

# 运行安全测试
pytest tests/api/ -v -m security

# 运行性能测试
pytest tests/api/ -v -m performance
```

## 测试标记

```python
# pytest.ini
[tool:pytest]
markers =
    security: marks tests as security tests
    performance: marks tests as performance tests
    integration: marks tests as integration tests
    slow: marks tests as slow running tests
    unit: marks tests as unit tests
```

## 断言工具

```python
# 状态码断言
assert response.status_code == 200

# JSON 结构断言
data = response.json()
assert "code" in data
assert "data" in data
assert "message" in data

# 列表断言
assert isinstance(data["data"], list)
assert len(data["data"]) > 0

# 字段值断言
assert data["data"]["username"] == "expected_value"

# 类型断言
assert isinstance(data["data"]["id"], int)

# 性能断言
assert response_time < 1.0

# 安全断言
assert "password" not in str(data)
assert "sql" not in error_message.lower()
```

## 注意事项

1. **真实服务优先**: 优先使用真实后端服务进行测试
2. **Mock限制使用**: 仅在异常场景、日志验证时使用Mock
3. **测试数据隔离**: 每个测试用例使用独立数据，测试后清理
4. **环境检查**: 测试前检查服务可用性
5. **异步测试**: 所有API测试需要 `@pytest.mark.asyncio`
6. **性能考虑**: 合理控制并发测试数量
7. **安全测试**: 真实验证安全漏洞防护
8. **错误处理**: 验证真实错误响应格式

## 真实服务测试检查清单

- [ ] 服务健康检查
- [ ] 测试数据准备和清理
- [ ] 真实API端点验证
- [ ] 实际数据库操作
- [ ] 真实网络请求
- [ ] 实际错误响应
- [ ] 真实性能表现
- [ ] 实际安全防护
