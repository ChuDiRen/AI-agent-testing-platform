# API Engine - 原生 Pytest 脚本示例

本目录包含使用原生 Python pytest 编写的 API 测试示例。

## 文件说明

- `conftest.py` - Pytest 配置文件，提供 fixtures
- `test_api_basic.py` - 基础 API 测试示例
- `test_api_advanced.py` - 高级特性示例（参数化、类、fixture 等）

## 运行方式

### 1. 运行所有测试

```bash
cd api-engine/examples/example-pytest-scripts
pytest -v -s
```

### 2. 运行特定测试文件

```bash
pytest test_api_basic.py -v -s
pytest test_api_advanced.py -v -s
```

### 3. 运行特定测试函数

```bash
pytest test_api_basic.py::test_login_api -v -s
pytest -k "test_login" -v -s
```

### 4. 运行标记的测试

```bash
pytest -m smoke -v -s           # 运行冒烟测试
pytest -m regression -v -s      # 运行回归测试
```

### 5. 生成 Allure 报告

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

### 6. 并行执行（需要安装 pytest-xdist）

```bash
pip install pytest-xdist
pytest -n auto -v
```

## Fixtures 说明

### api_keywords

提供 API 关键字实例，可以调用所有框架提供的关键字方法。

```python
def test_example(api_keywords):
    api_keywords.send_request(
        method="POST",
        url="http://example.com/api",
        json={"key": "value"}
    )
```

## 特性支持

- ✅ 参数化测试 (`@pytest.mark.parametrize`)
- ✅ Fixture 机制
- ✅ 测试类组织
- ✅ 测试标记 (`@pytest.mark.smoke`)
- ✅ Allure 报告集成
- ✅ 跳过测试 (`@pytest.mark.skip`)
- ✅ 预期失败 (`@pytest.mark.xfail`)

## 注意事项

1. 原生 pytest 脚本不使用 g_context 全局上下文
2. 变量管理使用 Python 原生方式或 fixture
3. 可以导入使用框架的 Keywords 类
4. 支持所有 pytest 原生特性

