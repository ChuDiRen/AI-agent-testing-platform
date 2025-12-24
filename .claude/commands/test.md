# /test - 生成测试用例

## 描述
根据代码自动生成测试用例。

## 使用方式
```
/test <文件路径> [--type <测试类型>] [--coverage]
```

## 参数说明
- `文件路径`: 要生成测试的源文件
- `--type`: 测试类型，可选：`unit`、`integration`、`e2e`
- `--coverage`: 生成覆盖率报告

## 测试类型

### 单元测试 (unit)
- 测试单个函数/方法
- Mock 外部依赖
- 快速执行

### 集成测试 (integration)
- 测试模块间交互
- 使用测试数据库
- 验证 API 端点

### 端到端测试 (e2e)
- 测试完整用户流程
- 使用 Playwright
- 模拟真实用户操作

## 生成示例

### Python 单元测试
```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.user import UserService

class TestUserService:
    @pytest.fixture
    def user_service(self):
        return UserService()
    
    @pytest.fixture
    def mock_repository(self):
        with patch('app.services.user.UserRepository') as mock:
            yield mock
    
    def test_get_user_by_id_success(self, user_service, mock_repository):
        """测试获取用户成功"""
        mock_repository.return_value.find_by_id.return_value = {
            "id": 1,
            "username": "test"
        }
        
        result = user_service.get_user_by_id(1)
        
        assert result is not None
        assert result["id"] == 1
    
    def test_get_user_by_id_not_found(self, user_service, mock_repository):
        """测试用户不存在"""
        mock_repository.return_value.find_by_id.return_value = None
        
        result = user_service.get_user_by_id(999)
        
        assert result is None
```

### API 集成测试
```python
# tests/api/test_user_api.py
import pytest
from httpx import AsyncClient

class TestUserAPI:
    @pytest.mark.asyncio
    async def test_list_users(self, auth_client: AsyncClient):
        """测试获取用户列表"""
        response = await auth_client.get("/api/users")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "list" in data["data"]
```

## 输出位置
- 单元测试: `tests/unit/test_{module}.py`
- 集成测试: `tests/api/test_{module}.py`
- E2E 测试: `tests/e2e/test_{feature}.py`

## 覆盖率报告
使用 `--coverage` 参数生成覆盖率报告：
```bash
pytest --cov=app --cov-report=html
```

## 注意事项
- 会分析源代码的函数签名和逻辑
- 自动生成正向和异常测试用例
- 遵循 AAA 模式（Arrange-Act-Assert）
