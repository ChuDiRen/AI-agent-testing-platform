# /test - 生成测试用例

## 描述
根据代码自动生成测试用例。

## 使用方式
```
/test <文件路径> [--type <测试类型>] [--coverage]
```

## 参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `文件路径` | 要生成测试的源文件 | 必填 |
| `--type` | `unit`/`integration`/`e2e` | `unit` |
| `--coverage` | 生成覆盖率报告 | 否 |

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

## 代码模板

参考 `@templates/code-patterns.md` 中的后端代码规范生成测试。

### Python 单元测试
```python
# tests/unit/test_{module}_service.py
import pytest
from unittest.mock import Mock, patch

class TestXxxService:
    @pytest.fixture
    def service(self, session):
        return XxxService(session)
    
    def test_get_by_id_success(self, service):
        """测试获取成功"""
        result = service.get_by_id(1)
        assert result is not None
    
    def test_get_by_id_not_found(self, service):
        """测试不存在"""
        result = service.get_by_id(999)
        assert result is None
```

### API 集成测试
```python
# tests/api/test_{module}_api.py
import pytest
from httpx import AsyncClient

class TestXxxAPI:
    @pytest.mark.asyncio
    async def test_query_by_page(self, auth_client: AsyncClient):
        response = await auth_client.post("/api/Xxx/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code == 200
        assert response.json()["code"] == 0
```

## 输出位置
- 单元测试: `tests/unit/test_{module}.py`
- 集成测试: `tests/api/test_{module}.py`
- E2E 测试: `tests/e2e/test_{feature}.py`

## 示例
```bash
/test userService.py                    # 单元测试
/test UserController.py --type integration  # 集成测试
/test user --type e2e                   # E2E 测试
/test userService.py --coverage         # 带覆盖率
```
