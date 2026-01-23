# 测试文档

本指南详细说明了如何运行测试、编写测试用例和理解测试结构。

## 目录

- [快速开始](#快速开始)
- [运行测试](#运行测试)
- [测试结构](#测试结构)
- [编写测试](#编写测试)
- [Fixtures](#fixtures)
- [覆盖率](#覆盖率)

## 快速开始

### 安装测试依赖

```bash
cd backend

# 安装所有依赖（包括测试依赖）
pip install -r requirements.txt
```

### 运行所有测试

```bash
# 运行所有测试
pytest

# 运行所有测试并显示输出
pytest -v
```

## 运行测试

### 基本用法

```bash
# 运行所有测试
pytest

# 运行指定文件
pytest tests/test_auth_api.py

# 运行指定测试类
pytest tests/test_auth_api.py::TestAuthAPI

# 运行指定测试方法
pytest tests/test_auth_api.py::TestAuthAPI::test_login_success

# 运行匹配模式的测试
pytest tests/test_auth_api.py -k "login"
```

### 使用标记

```bash
# 运行所有单元测试
pytest -m unit

# 运行所有集成测试
pytest -m integration

# 排除慢速测试
pytest -m "not slow"
```

### 输出选项

```bash
# 详细输出
pytest -v

# 显示局部变量
pytest -l

# 显示测试持续时间
pytest --durations=10

# 在失败时进入调试器
pytest --pdb

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 停止规则

```bash
# 第一个失败时停止
pytest -x

# 第N个失败时停止
pytest -x --maxfail=3
```

## 测试结构

### 目录结构

```
tests/
├── conftest.py              # Pytest 配置和共享 fixtures
├── test_auth_api.py         # 认证 API 测试
├── test_document_api.py      # 文档管理 API 测试
├── test_chat_api.py         # 智能问答 API 测试
├── test_user_api.py         # 用户管理 API 测试
└── __init__.py
```

### 测试文件模式

测试文件命名：`test_*.py`

测试类命名：`Test*`

测试方法命名：`test_*`

示例：
```python
# ✅ 正确命名
test_auth_api.py
class TestAuthAPI:
    def test_login_success(self):
        pass

# ❌ 错误命名
auth_test.py
class AuthTests:
    def login_test(self):
        pass
```

## 编写测试

### 基本测试结构

```python
import pytest
from fastapi.testclient import TestClient


class TestMyFeature:
    """功能测试类"""

    def test_success_case(self, client, user_auth_headers):
        """成功场景测试"""
        # 准备测试数据
        test_data = {
            "field1": "value1",
            "field2": "value2"
        }

        # 执行请求
        response = client.post(
            "/api/v1/endpoint",
            headers=user_auth_headers,
            json=test_data
        )

        # 验证结果
        assert response.status_code == 200
        data = response.json()
        assert data["field1"] == "value1"

    def test_failure_case(self, client, user_auth_headers):
        """失败场景测试"""
        response = client.post(
            "/api/v1/endpoint",
            headers=user_auth_headers,
            json={"invalid_field": "value"}
        )

        assert response.status_code == 400
```

### 测试最佳实践

#### 1. AAA 模式

Arrange (准备) - Act (执行) - Assert (断言)

```python
def test_upload_document(self, client, user_auth_headers):
    # Arrange: 准备测试数据
    test_data = {"title": "测试文档"}
    test_file = create_temp_file()

    # Act: 执行操作
    response = client.post(
        "/api/v1/documents/upload",
        headers=user_auth_headers,
        files={"file": test_file}
    )

    # Assert: 验证结果
    assert response.status_code == 200
    assert "document_id" in response.json()
```

#### 2. 独立性

每个测试应该独立运行，不依赖其他测试。

```python
# ✅ 好的实践
def test_create_user(self, client, admin_auth_headers):
    user_data = {"username": "unique_user", "email": "test@example.com"}
    response = client.post("/api/v1/users", headers=admin_auth_headers, json=user_data)
    assert response.status_code == 200

# ❌ 不好的实践 - 依赖前一个测试
def test_create_user_then_get(self, client, admin_auth_headers):
    # 假设上一个测试创建了用户
    response = client.get("/api/v1/users/1", headers=admin_auth_headers)
```

#### 3. 清理

使用 fixtures 自动清理资源。

```python
@pytest.fixture
def test_user(test_session):
    # 创建测试数据
    user = User(username="test_user", email="test@example.com")
    test_session.add(user)
    test_session.commit()

    yield user  # 返回给测试使用

    # 清理：自动 rollback
    test_session.rollback()
```

#### 4. 有意义的名称

```python
# ✅ 清晰的名称
def test_login_with_correct_credentials(self):
    pass

def test_login_with_incorrect_password(self):
    pass

# ❌ 不清晰的名称
def test_login_1(self):
    pass
def test_login_2(self):
    pass
```

#### 5. 测试边界情况

```python
def test_upload_max_size_file(self, client):
    """测试上传最大大小文件"""
    large_file = create_file(size=50 * 1024 * 1024)  # 50MB
    response = upload_file(client, large_file)
    assert response.status_code == 200  # 或 413

def test_upload_over_max_size_file(self, client):
    """测试上传超过最大大小文件"""
    huge_file = create_file(size=51 * 1024 * 1024)  # 51MB
    response = upload_file(client, huge_file)
    assert response.status_code == 413  # Payload Too Large
```

## Fixtures

### 共享 Fixtures

在 `conftest.py` 中定义的共享 fixtures：

#### `client`
FastAPI 测试客户端

```python
def test_api_endpoint(client):
    response = client.get("/api/v1/endpoint")
    assert response.status_code == 200
```

#### `test_session`
数据库测试会话（自动回滚）

```python
def test_database_operation(test_session):
    user = User(username="test_user")
    test_session.add(user)
    test_session.commit()
    # 测试结束后自动回滚
```

#### `test_admin_user`
测试管理员用户

```python
def test_admin_operation(admin_auth_headers):
    response = client.get("/api/v1/admin/endpoint", headers=admin_auth_headers)
    assert response.status_code == 200
```

#### `test_regular_user`
测试普通用户

```python
def test_user_operation(user_auth_headers):
    response = client.get("/api/v1/user/endpoint", headers=user_auth_headers)
    assert response.status_code == 200
```

#### `admin_auth_headers`
管理员认证头（Bearer token）

```python
def test_admin_api(admin_auth_headers):
    response = client.get("/api/v1/users", headers=admin_auth_headers)
```

#### `user_auth_headers`
普通用户认证头

```python
def test_user_api(user_auth_headers):
    response = client.get("/api/v1/documents", headers=user_auth_headers)
```

#### `temp_upload_file`
临时上传文件

```python
def test_file_upload(client, user_auth_headers, temp_upload_file):
    with open(temp_upload_file, "rb") as f:
        response = client.post(
            "/api/v1/upload",
            headers=user_auth_headers,
            files={"file": f}
        )
```

### 自定义 Fixtures

在测试文件中定义自定义 fixtures：

```python
@pytest.fixture
def test_document(test_session):
    """创建测试文档"""
    doc = Document(
        title="测试文档",
        permission="private",
        status="completed"
    )
    test_session.add(doc)
    test_session.commit()
    test_session.refresh(doc)
    return doc

def test_with_document(test_document, client, user_auth_headers):
    response = client.get(f"/api/v1/documents/{test_document.id}", headers=user_auth_headers)
```

## 覆盖率

### 生成覆盖率报告

```bash
# 生成 HTML 覆盖率报告
pytest --cov=app --cov-report=html

# 生成终端覆盖率报告
pytest --cov=app --cov-report=term-missing

# 生成 XML 报告（用于 CI）
pytest --cov=app --cov-report=xml

# 生成所有格式
pytest --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml
```

### 查看覆盖率报告

```bash
# HTML 报告在 htmlcov/ 目录
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows
```

### 覆盖率目标

- **目标**: 80% 以上
- **核心模块**: 90% 以上
- **新增代码**: 100%

### 排除文件

在 `pytest.ini` 中配置覆盖率排除：

```ini
[coverage:run]
omit =
    */tests/*
    */migrations/*
    */__init__.py
    */conftest.py
```

## 测试类型

### 单元测试

测试单个函数或方法，隔离所有外部依赖。

```python
def test_password_hash():
    """测试密码哈希功能"""
    from app.core.security import get_password_hash

    password = "test_password"
    hashed = get_password_hash(password)

    assert hashed != password
    assert len(hashed) > 10
```

### 集成测试

测试多个模块或外部服务的集成。

```python
@pytest.mark.integration
def test_login_workflow(client, test_admin_user):
    """测试完整登录流程"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_test", "password": "admin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 端到端测试

测试完整的用户场景。

```python
@pytest.mark.integration
def test_upload_and_chat_workflow(client, user_auth_headers):
    """测试上传文档并问答的完整流程"""
    # 1. 上传文档
    upload_response = client.post("/api/v1/documents/upload", headers=user_auth_headers, files={...})
    assert upload_response.status_code == 200

    # 2. 索引文档
    doc_id = upload_response.json()["id"]
    index_response = client.post(f"/api/v1/documents/{doc_id}/index", headers=user_auth_headers)
    assert index_response.status_code == 200

    # 3. 问答
    chat_response = client.post(
        "/api/v1/chat",
        headers=user_auth_headers,
        json={"message": "测试问题", "conversation_id": "conv_123"}
    )
    assert chat_response.status_code == 200
```

## 调试测试

### 查看输出

```bash
# 显示详细的测试输出
pytest -vv -s

# 显示局部变量
pytest -l

# 显示 slowest 10 个测试
pytest --durations=10
```

### 调试失败的测试

```bash
# 在第一个失败时停止并进入调试器
pytest -x --pdb

# 在所有测试失败后进入调试器
pytest --pdb-trace
```

### 查看详细错误

```bash
# 显示完整的错误堆栈
pytest --tb=long

# 显示简短的错误信息
pytest --tb=short

# 以 Python 格式显示错误
pytest --tb=python
```

## 常见问题

### Q: 测试失败但手动测试通过

**可能原因：**
1. Fixture 返回了错误的数据
2. 测试之间的依赖
3. 数据库状态未清理

**解决方案：**
```python
# 确保每个测试独立
def test_isolated(client, test_session):
    test_session.rollback()  # 清理之前的数据

    # 执行测试...
```

### Q: 测试很慢

**优化建议：**
1. 使用内存数据库而不是真实数据库
2. Mock 外部 API 调用
3. 并行运行测试
4. 标记慢速测试

```bash
# 标记慢速测试
@pytest.mark.slow
def test_slow_operation():
    pass

# 排除慢速测试
pytest -m "not slow"
```

### Q: 如何 Mock 外部服务

使用 `pytest-mock` 或 `unittest.mock`：

```python
from unittest.mock import patch

def test_with_external_api_mock(client, user_auth_headers):
    with patch('app.services.llm_service.call_llm') as mock_llm:
        mock_llm.return_value = "模拟的回答"

        response = client.post("/api/v1/chat", headers=user_auth_headers, json={...})

        assert response.status_code == 200
        assert mock_llm.called
```

## 持续集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt

    - name: Run tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

## 最佳实践总结

1. **独立性**: 每个测试应该独立运行
2. **清晰性**: 使用有意义的测试名称和描述
3. **完整性**: 测试正常、边界和异常情况
4. **可维护性**: 使用 fixtures 减少重复
5. **快速性**: 优化测试速度，必要时 mock 外部依赖
6. **覆盖率**: 保持高覆盖率，目标是 80% 以上
7. **文档**: 为复杂测试添加文档字符串

## 参考资源

- [Pytest 文档](https://docs.pytest.org/)
- [FastAPI 测试指南](https://fastapi.tiangolo.com/tutorial/testing/)
- [测试覆盖率最佳实践](https://coverage.readthedocs.io/)
