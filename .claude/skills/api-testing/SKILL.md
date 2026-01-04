# API 测试技能

## 触发条件
当用户提到：接口测试、API测试、httpx、pytest、自动化测试

## 技术栈
- pytest + httpx（异步HTTP客户端）
- pytest-asyncio（异步测试支持）
- pytest-html（测试报告）

## 项目结构
```
tests/
├── conftest.py          # 全局 fixtures
├── api/                 # API 测试
│   ├── __init__.py
│   ├── test_user.py
│   └── test_project.py
├── unit/                # 单元测试
└── data/                # 测试数据
    └── test_data.yaml
```

## conftest.py 配置
```python
import pytest
import httpx
from typing import AsyncGenerator

# 基础配置
BASE_URL = "http://localhost:8000/api"
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
    """创建 HTTP 客户端"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client

@pytest.fixture(scope="session")
async def auth_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """创建带认证的 HTTP 客户端"""
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
```

## 测试用例模板

### 基础 CRUD 测试
```python
# tests/api/test_user.py
import pytest
from httpx import AsyncClient

class TestUserAPI:
    """用户接口测试"""
    
    @pytest.mark.asyncio
    async def test_query_by_page(self, auth_client: AsyncClient):
        """测试分页查询"""
        response = await auth_client.post("/User/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert "total" in data["data"]
    
    @pytest.mark.asyncio
    async def test_create_user(self, auth_client: AsyncClient, test_user_data):
        """测试创建用户"""
        response = await auth_client.post("/User/insert", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
        
        # 保存 ID 用于后续测试
        return data["data"]["id"]
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, auth_client: AsyncClient):
        """测试按ID查询"""
        user_id = 1
        response = await auth_client.get(f"/User/queryById", params={"id": user_id})
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    @pytest.mark.asyncio
    async def test_update_user(self, auth_client: AsyncClient):
        """测试更新用户"""
        response = await auth_client.put("/User/update", json={
            "id": 1,
            "username": "updated_name"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    @pytest.mark.asyncio
    async def test_delete_user(self, auth_client: AsyncClient):
        """测试删除用户"""
        user_id = 999  # 测试用 ID
        response = await auth_client.delete("/User/delete", params={"id": user_id})
        
        assert response.status_code == 200
```

### 参数化测试
```python
@pytest.mark.asyncio
@pytest.mark.parametrize("page,pageSize,expected_count", [
    (1, 10, 10),
    (1, 20, 20),
    (2, 10, 10),
])
async def test_pagination(self, auth_client: AsyncClient, page, pageSize, expected_count):
    """测试分页参数"""
    response = await auth_client.post("/User/queryByPage", json={
        "page": page,
        "pageSize": pageSize
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]["list"]) <= expected_count
```

### 异常测试
```python
@pytest.mark.asyncio
async def test_create_user_invalid_data(self, auth_client: AsyncClient):
    """测试无效数据创建"""
    response = await auth_client.post("/User/insert", json={
        "username": "",  # 空用户名
    })
    
    assert response.status_code in [400, 422]

@pytest.mark.asyncio
async def test_get_nonexistent_user(self, auth_client: AsyncClient):
    """测试查询不存在的用户"""
    response = await auth_client.get("/User/queryById", params={"id": 999999})
    
    assert response.status_code == 200
    data = response.json()
    # 根据实际返回判断
    assert data["data"] is None or data["code"] != 200

@pytest.mark.asyncio
async def test_unauthorized_access(self, client: AsyncClient):
    """测试未授权访问"""
    response = await client.post("/User/queryByPage", json={})
    
    assert response.status_code == 401
```

## 运行测试

```bash
# 运行所有测试
pytest tests/api/ -v

# 运行指定文件
pytest tests/api/test_user.py -v

# 运行指定测试类
pytest tests/api/test_user.py::TestUserAPI -v

# 运行指定测试方法
pytest tests/api/test_user.py::TestUserAPI::test_query_by_page -v

# 生成 HTML 报告
pytest tests/api/ -v --html=report.html

# 显示覆盖率
pytest tests/api/ -v --cov=app --cov-report=html
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
assert isinstance(data["data"]["list"], list)
assert len(data["data"]["list"]) > 0

# 字段值断言
assert data["data"]["username"] == "expected_value"

# 类型断言
assert isinstance(data["data"]["id"], int)
```

## 注意事项
1. 测试数据与生产数据隔离
2. 测试后清理创建的数据
3. 使用 fixtures 复用测试配置
4. 异步测试需要 `@pytest.mark.asyncio`
