# API Pytest 测试脚本示例

本目录包含 API 自动化测试的 Pytest 原生脚本示例，演示如何编写和组织 API 测试用例。

## 📁 文件结构

```
api-pytest-scripts/
├── conftest.py              # Pytest 配置和公共 Fixtures
├── test_api_basic.py        # 基础 API 测试示例
├── test_api_advanced.py     # 高级 API 测试示例
└── README.md               # 本文件
```

## 🎯 测试用例分类

### 1. **test_api_basic.py** - 基础测试

包含以下测试场景：

- **用户登录测试**
  - ✅ 用户名密码登录成功
  - ✅ 密码错误登录失败
  - ✅ 参数缺失登录失败（参数化测试）

- **商品查询测试**
  - ✅ 查询商品列表
  - ✅ 查询商品详情

- **数据驱动测试**
  - ✅ 多用户登录场景（参数化测试）

### 2. **test_api_advanced.py** - 高级测试

包含以下测试场景：

- **接口关联测试**
  - ✅ 登录后查询用户信息（数据传递）
  - ✅ 完整订单创建流程（多步骤关联）

- **性能测试**
  - ✅ 接口响应时间验证
  - ✅ 并发请求测试

- **错误处理测试**
  - ✅ 无效 HTTP 方法
  - ✅ 无效 JSON 格式
  - ✅ 超长字符串输入

- **数据验证测试**
  - ✅ 响应数据结构完整性验证

## 🚀 运行测试

### 运行全部测试

```bash
# 从 test-engine 根目录运行
python -m testrun.cli --engine-type=api --type=pytest --cases=examples/api-pytest-scripts
```

### 运行指定测试文件

```bash
# 只运行基础测试
python -m testrun.cli --engine-type=api --type=pytest --cases=examples/api-pytest-scripts/test_api_basic.py

# 只运行高级测试
python -m testrun.cli --engine-type=api --type=pytest --cases=examples/api-pytest-scripts/test_api_advanced.py
```

### 运行指定测试类

```bash
# 运行用户登录测试类
python -m testrun.cli --engine-type=api --type=pytest --cases=examples/api-pytest-scripts/test_api_basic.py::TestUserLogin
```

### 运行指定测试方法

```bash
# 运行登录成功测试
python -m testrun.cli --engine-type=api --type=pytest --cases=examples/api-pytest-scripts/test_api_basic.py::TestUserLogin::test_login_success
```

### 使用标记过滤

```bash
# 只运行冒烟测试
python -m testrun.cli --engine-type=api --type=pytest --cases=examples/api-pytest-scripts -m smoke

# 排除慢速测试
python -m testrun.cli --engine-type=api --type=pytest --cases=examples/api-pytest-scripts -m "not slow"
```

### 查看详细输出

```bash
# 显示详细日志
python -m testrun.cli --engine-type=api --type=pytest --cases=examples/api-pytest-scripts -v

# 显示 print 输出
python -m testrun.cli --engine-type=api --type=pytest --cases=examples/api-pytest-scripts -s
```

## 📚 Fixtures 说明

### Session 级别 Fixtures

| Fixture | 说明 | 作用域 |
|---------|------|--------|
| `base_url` | API 基础 URL | session |
| `api_headers` | 通用请求头 | session |
| `api_session` | 可复用的 requests Session | session |
| `login_token` | 登录 Token（自动登录） | session |

### Function 级别 Fixtures

| Fixture | 说明 | 作用域 |
|---------|------|--------|
| `api_client` | 已认证的 API 客户端（封装了常用方法） | function |

### 使用示例

```python
def test_example(api_client):
    """使用 api_client fixture"""
    response = api_client.get("/api/endpoint")
    assert response.status_code == 200
```

## 🏷️ 测试标记说明

| 标记 | 说明 | 使用场景 |
|------|------|---------|
| `@pytest.mark.smoke` | 冒烟测试 | 核心功能快速验证 |
| `@pytest.mark.regression` | 回归测试 | 完整功能验证 |
| `@pytest.mark.slow` | 慢速测试 | 耗时较长的测试 |

### 添加自定义标记

在 `conftest.py` 中添加：

```python
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "your_marker: 标记说明"
    )
```

## 📊 查看测试报告

### Allure 报告

测试执行后，Allure 报告会自动生成在 `test-engine/reports/allure-report/` 目录。

```bash
# 打开 Allure 报告
allure open test-engine/reports/allure-report
```

### 测试日志

测试日志保存在 `test-engine/reports/logdata/log.log`。

## ✨ 最佳实践

### 1. 使用 Allure 注解增强报告

```python
import allure

@allure.feature("功能模块")
@allure.story("用户故事")
class TestExample:
    
    @allure.title("测试用例标题")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_case(self):
        with allure.step("步骤1: 准备数据"):
            # ...
            allure.attach(data, "附件名称", allure.attachment_type.JSON)
        
        with allure.step("步骤2: 执行操作"):
            # ...
```

### 2. 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    ("value1", result1),
    ("value2", result2),
])
def test_with_params(input, expected):
    assert process(input) == expected
```

### 3. 使用 Fixtures 管理测试数据

```python
@pytest.fixture
def test_data():
    """提供测试数据"""
    return {"key": "value"}

def test_example(test_data):
    assert test_data["key"] == "value"
```

### 4. 异常处理

```python
def test_exception():
    with pytest.raises(ValueError):
        raise ValueError("预期的异常")
```

### 5. 跳过测试

```python
@pytest.mark.skip(reason="功能未实现")
def test_not_ready():
    pass

@pytest.mark.skipif(condition, reason="条件不满足")
def test_conditional():
    pass
```

## 🔧 自定义配置

### 修改基础 URL

在 `conftest.py` 中修改：

```python
@pytest.fixture(scope="session")
def base_url() -> str:
    return "https://your-api-domain.com"
```

或通过环境变量：

```python
import os

@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("API_BASE_URL", "http://default-url.com")
```

### 添加自定义 Fixtures

在 `conftest.py` 中添加：

```python
@pytest.fixture
def custom_fixture():
    # 前置操作
    data = setup()
    yield data
    # 后置清理
    teardown()
```

## 📝 编写新测试用例

### 1. 创建新测试文件

文件命名：`test_*.py` 或 `*_test.py`

```python
"""
测试模块描述
"""
import pytest
import allure


@allure.feature("功能模块")
class TestNewFeature:
    """测试类描述"""
    
    @allure.title("测试用例标题")
    def test_case_name(self, api_client):
        """
        测试用例详细说明
        
        步骤：
        1. 步骤1
        2. 步骤2
        """
        # 测试实现
        pass
```

### 2. 使用命名约定

- **测试类**: `Test` 开头，如 `TestUserLogin`
- **测试方法**: `test_` 开头，如 `test_login_success`
- **Fixture**: 使用描述性名称，如 `api_client`, `login_token`

### 3. 添加清晰的文档

- 模块级文档字符串：说明测试文件的目的
- 类级文档字符串：说明测试类的范围
- 方法级文档字符串：说明测试步骤和预期结果

## 🐛 调试技巧

### 1. 使用 print 调试

```bash
# 显示 print 输出
python -m testrun.cli --engine-type=api --type=pytest --cases=examples/api-pytest-scripts -s
```

### 2. 在失败时进入调试器

```python
def test_example():
    import pdb; pdb.set_trace()
    # 或使用 breakpoint() (Python 3.7+)
    breakpoint()
```

### 3. 只运行失败的测试

```bash
pytest --lf  # last-failed
pytest --ff  # failed-first
```

## 📖 参考资料

- [Pytest 官方文档](https://docs.pytest.org/)
- [Allure Pytest 集成](https://docs.qameta.io/allure/#_pytest)
- [Requests 文档](https://requests.readthedocs.io/)

## 💡 提示

1. **Session Fixture 复用**：`login_token` 在整个测试会话中只登录一次，提高效率
2. **API Client 封装**：使用 `api_client` fixture 简化请求代码
3. **Allure 报告**：充分使用 `@allure.step` 和 `allure.attach` 增强报告可读性
4. **参数化测试**：使用 `@pytest.mark.parametrize` 减少重复代码
5. **测试独立性**：确保每个测试用例可以独立运行，不依赖执行顺序

## ❓ 常见问题

### Q: 如何修改测试环境的 URL？

A: 在 `conftest.py` 中修改 `base_url` fixture 的返回值。

### Q: 如何添加新的公共 fixture？

A: 在 `conftest.py` 中定义新的 fixture 函数。

### Q: 如何处理测试数据？

A: 可以使用 fixture 提供测试数据，或从外部文件（JSON/YAML/Excel）加载。

### Q: 如何跳过某些测试？

A: 使用 `@pytest.mark.skip` 或 `@pytest.mark.skipif` 装饰器。

### Q: 如何运行特定标记的测试？

A: 使用 `-m` 参数，如 `python -m testrun.cli ... -m smoke`。
