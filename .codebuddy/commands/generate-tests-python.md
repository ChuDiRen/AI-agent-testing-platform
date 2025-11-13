---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [文件路径] | [模块名称]
description: 为 Python/FastAPI 项目生成包含单元测试、集成测试和边界情况覆盖的全面测试套件
---

# 生成测试

为以下目标生成全面的测试套件：$ARGUMENTS

## 当前测试设置

- 测试框架：pytest + pytest-asyncio + pytest-mock
- 现有测试：!find . -name "test_*.py" -o -name "*_test.py" | head -10
- 测试覆盖率：!pytest --cov=. --cov-report=term-missing 2>&1 || echo "运行 pytest 检查测试"
- 目标文件：@$ARGUMENTS（如果提供了文件路径）

## 任务

我将分析目标代码并创建完整的测试覆盖，包括：

1. 单元测试：标准函数、类方法和工具函数
2. 集成测试：FastAPI 路由、服务层交互、数据库操作
3. 边界情况和错误处理：异常处理、超时、并发安全、输入验证
4. Mock 实现：为依赖项生成 mock（使用 `pytest-mock`）
5. 测试工具和辅助函数：根据需求创建 fixture
6. 性能测试：使用 `pytest-benchmark` 进行基准测试（适用场景）

## 流程

我将遵循以下步骤：

1. 运行 `pytest --collect-only` 检查现有测试，运行 `pytest --cov` 查看覆盖率
2. 分析目标文件/模块结构：识别 Python 包结构、FastAPI 组件（routers、services、repositories）
3. 识别所有可测试函数、方法和行为：分析函数签名、依赖关系和框架组件类型
4. 检查项目中现有的测试模式和实践
5. 创建 `test_*.py` 文件：遵循项目命名规范
6. 实现完整测试用例：使用参数化测试，包含适当的 setup/teardown
7. 添加必要的 mock 和测试工具：使用 `pytest-mock`
8. 验证测试覆盖率 ≥80%，运行 `pytest -v` 确保所有测试通过

## 测试类型

### 单元测试

- 使用 `@pytest.mark.parametrize` 参数化测试，覆盖正常输入、错误输入、边界值
- 测试类方法的行为和状态变更
- 工具函数的全面测试
- 使用 `pytest.raises()` 验证异常抛出和错误信息

### 集成测试

- **FastAPI 路由测试**：使用 `TestClient` 测试端点、验证请求/响应和状态码、Mock 依赖项（数据库、外部服务）、验证错误处理和错误码、测试认证和权限
- **Service 层测试**：业务逻辑集成、多依赖项协调、事务处理测试
- **数据库集成测试**：使用测试数据库或 SQLite in-memory、数据一致性验证、事务回滚测试

### 边界情况和错误处理

- **异常处理**：测试各类异常的捕获和处理
- **输入验证**：边界值、None 值、空字符串、非法输入
- **超时处理**：验证超时机制的触发（`asyncio.wait_for`）
- **并发安全**：测试并发场景下的数据一致性
- **错误场景**：网络错误、数据库错误、业务错误

### FastAPI 特定测试

- **路由测试**：验证所有 HTTP 方法、路径参数和查询参数、Pydantic 模型验证
- **依赖注入测试**：使用 `app.dependency_overrides` Mock 依赖
- **中间件测试**：验证请求/响应处理、异常处理
- **异步测试**：使用 `@pytest.mark.asyncio` 标记

## 测试最佳实践

### 测试结构

- 使用描述性测试名称，清晰表达测试场景（使用中文）
- 遵循 AAA 模式（Arrange、Act、Assert）
- 使用 fixture 的 yield 实现 setup/teardown
- 使用适当的 setup/teardown 实现测试隔离

### Fixture 策略

- 在 `conftest.py` 中定义跨文件共享的 fixture
- 根据需求选择合适的作用域（`function`/`class`/`module`/`session`）
- 使用 `autouse=True` 实现自动化初始化和清理

### Mock 策略

- 仅 Mock 边界之外的依赖（数据库/网络/外部服务）
- 使用 `pytest-mock` 的 `mocker` fixture
- 使用 `responses` 或 `aioresponses` Mock HTTP 请求
- 验证 Mock 调用：`mock.assert_called_once_with()`
- 测试数据用工厂函数或 `faker` 库生成，必要时 Mock 时间（`freezegun`）

### 覆盖率目标

- 覆盖率 ≥ 80%（运行 `pytest --cov=. --cov-report=html`）
- 聚焦关键业务路径与错误场景
- 覆盖边界值、异常处理、超时与资源清理
- 使用 HTML 报告可视化未覆盖代码：`htmlcov/index.html`

### 完成检查

- [ ] `pytest -v` 所有测试通过
- [ ] 覆盖率 ≥ 80%
- [ ] 使用参数化测试（适用场景）
- [ ] Mock 验证通过
- [ ] 异步测试正确使用 `@pytest.mark.asyncio`
