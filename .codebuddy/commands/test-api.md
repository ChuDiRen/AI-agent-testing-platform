---
description: API接口测试命令
---

# 命令：test-api

## 功能描述

使用pytest和httpx进行API接口自动化测试，生成测试报告。

## 使用方式

```
/test-api
```

或

```
/test-api <接口或模块名称>
```

## 参数说明

- `--module=ModuleName` - 测试指定模块
- `--endpoint=/api/v1/users` - 测试指定接口
- `--coverage` - 生成覆盖率报告
- `--verbose` - 详细输出
- `--report=html` - 生成HTML测试报告

## 执行流程

1. **测试准备**：
   - 读取API文档
   - 准备测试数据
   - 配置测试环境

2. **测试用例生成**：
   - 正常场景测试
   - 异常场景测试
   - 边界值测试
   - 权限验证测试

3. **测试执行**：
   - 运行测试用例
   - 记录测试结果
   - 收集测试数据

4. **报告生成**：
   - 生成测试报告
   - 生成覆盖率报告
   - 标注失败用例

5. **结果分析**：
   - 分析失败原因
   - 提供修复建议

## 测试用例结构

```python
# tests/api/test_user.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient):
    """测试用户创建成功"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_create_user_duplicate(client: AsyncClient):
    """测试用户名重复"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    # 创建用户
    await client.post("/api/v1/users/", json=user_data)
    # 再次创建相同用户
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    assert "用户已存在" in response.json()["message"]
```

## 输出格式

### 终端输出

```markdown
【API测试执行中...】

==================== 测试开始 ====================

测试套件：用户模块
测试用例数：15
执行环境：http://localhost:8080

==================== 测试结果 ====================

✅ test_create_user_success - 通过
✅ test_create_user_duplicate - 通过
✅ test_get_user_by_id - 通过
✅ test_update_user - 通过
✅ test_delete_user - 通过
❌ test_user_login_wrong_password - 失败

==================== 测试统计 ====================

总计：15
通过：14
失败：1
跳过：0
通过率：93.33%
执行时间：2.34秒

==================== 覆盖率报告 ====================

模块 | 覆盖率 | 语句 | 分支 | 函数 | 行数
-----|--------|------|------|------|------
user | 92% | 120/130 | 45/50 | 20/20 | 250/270
product | 88% | 180/205 | 70/80 | 25/28 | 380/430
总计 | 90% | 300/335 | 115/130 | 45/48 | 630/700

详细报告已生成：tests/reports/api-test-report.html
```

## 失败分析

```markdown
【失败用例分析】

用例：test_user_login_wrong_password
失败原因：AssertionError: Expected 401, got 200
问题描述：使用错误密码登录时，应该返回401，但实际返回200

修复建议：
1. 检查登录接口的密码验证逻辑
2. 确保密码错误时返回正确的HTTP状态码
3. 添加错误消息

位置：app/services/auth.py:45
```

## 相关文件

```
tests/
├── api/              # API测试
│   ├── test_user.py
│   ├── test_product.py
│   └── test_order.py
├── conftest.py       # 测试配置
└── reports/          # 测试报告
    ├── api-test-report.html
    └── coverage-report.html
```

## 示例

```
/test-api --module=user --coverage --report=html
```

```
/test-api /api/v1/users/register
```

## 相关命令

- `/generate-api-doc` - 生成API文档
- `/develop-backend` - 后端开发
- `/test-e2e` - E2E测试
